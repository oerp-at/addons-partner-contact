# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import csv
import json
import logging

import requests
from psycopg2.extras import execute_values

from odoo import SUPERUSER_ID, fields, models
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

# Official Austrian postal-code table published as open data by RTR / the
# Austrian Post (~0.5 MB JSON). One canonical delivery town (Bestimmungsort)
# per postal code, so Austrian codes are never ambiguous.
AT_URL = "https://data.rtr.at/api/v1/tables/plz.json"
# OpenStreetMap-derived German street list published by openPLZ.
# Source: https://github.com/openpotato/openplzapi.data (data licensed ODbL,
# (c) OpenStreetMap contributors). ~55 MB, comma-separated.
DE_URL = (
    "https://raw.githubusercontent.com/openpotato/openplzapi.data/main/"
    "src/de/osm/streets.updated.csv"
)
# Generous timeout for the whole download of the large bodies.
DOWNLOAD_TIMEOUT = 300

# Per-country download layout. ``format`` selects the parser (``json`` for the
# RTR table, ``csv`` for the German street list).
_COUNTRY_CONFIG = {
    "AT": {"url": AT_URL, "format": "json"},
    "DE": {
        "url": DE_URL,
        "format": "csv",
        "delimiter": ",",
        "data_start": 1,
        "encoding": "utf-8",
    },
}

# RTR "bundesland" short code -> Odoo base.state_at_<n> record.
_AT_STATE_XMLID = {
    "B": "base.state_at_1",
    "K": "base.state_at_2",
    "N": "base.state_at_3",
    "O": "base.state_at_4",
    "Sa": "base.state_at_5",
    "St": "base.state_at_6",
    "T": "base.state_at_7",
    "V": "base.state_at_8",
    "W": "base.state_at_9",
}

# The first two digits of the RegionalKey (AGS) identify the Bundesland.
_AGS_STATE_XMLID = {
    "01": "base.state_de_sh",
    "02": "base.state_de_hh",
    "03": "base.state_de_ni",
    "04": "base.state_de_hb",
    "05": "base.state_de_nw",
    "06": "base.state_de_he",
    "07": "base.state_de_rp",
    "08": "base.state_de_bw",
    "09": "base.state_de_by",
    "10": "base.state_de_sl",
    "11": "base.state_de_be",
    "12": "base.state_de_bb",
    "13": "base.state_de_mv",
    "14": "base.state_de_sn",
    "15": "base.state_de_st",
    "16": "base.state_de_th",
}


class CountryZipCity(models.Model):
    _name = "country.zip.city"
    _description = "Country ZIP City"
    _order = "zip, city"

    zip = fields.Char(required=True, index=True)
    city = fields.Char(
        required=True,
        help="Delivery town used for autofill (Bestimmungsort for AT, "
        "Locality for DE).",
    )
    municipality_code = fields.Char(
        index=True,
        help="RegionalKey/AGS (DE). Used to map an OpenPLZ result back onto a "
        "directory row. Empty for Austria.",
    )
    state_id = fields.Many2one(
        "res.country.state",
        required=True,
        ondelete="cascade",
        index=True,
    )
    country_id = fields.Many2one(
        "res.country",
        related="state_id.country_id",
        store=True,
        readonly=True,
    )

    # -- Import ----------------------------------------------------------

    def _import_zip_directory(self, country_code):
        """Download and import a whole country ZIP directory in one go.

        Distinct ``(zip, city, municipality_code, state)`` combinations are
        extracted from the source, then the country's existing rows are
        replaced in a single delete + bulk insert. A session advisory lock
        guards against two imports running at once. Returns the number of rows
        written.
        """
        country_code = (country_code or "").upper()
        if country_code not in _COUNTRY_CONFIG:
            raise UserError(
                self.env._("Unsupported ZIP directory country %s.", country_code)
            )
        lock_name = "czc_import_%s" % country_code
        self.env.cr.execute(
            "SELECT pg_try_advisory_xact_lock(hashtext(%s)::bigint)", (lock_name,)
        )
        if not self.env.cr.fetchone()[0]:
            raise UserError(
                self.env._(
                    "A %s ZIP directory import is already running.", country_code
                )
            )
        cfg = _COUNTRY_CONFIG[country_code]
        country = self.env.ref("base.%s" % country_code.lower())
        rows = self._download_and_parse(country_code, cfg)
        created = self._replace_country_rows(country.id, rows)
        _logger.info("%s ZIP directory import finished: %s rows", country_code, created)
        return created

    def _download_and_parse(self, country_code, cfg):
        """Return the distinct ``(zip, city, municipality_code, state_id)`` rows."""
        url = cfg["url"]
        _logger.info(
            "Downloading %s ZIP directory from %s (timeout %ss)",
            country_code,
            url,
            DOWNLOAD_TIMEOUT,
        )
        response = requests.get(url, timeout=DOWNLOAD_TIMEOUT)
        response.raise_for_status()
        content = response.content
        _logger.info(
            "%s ZIP directory downloaded: HTTP %s, %s bytes, content-type %s",
            country_code,
            response.status_code,
            len(content),
            response.headers.get("Content-Type") or "unknown",
        )
        if cfg["format"] == "json":
            return self._parse_at_json(content)
        return self._parse_de_csv(content, cfg)

    def _replace_country_rows(self, country_id, rows):
        """Delete the country's rows and bulk-insert the distinct combinations."""
        self.env.cr.execute(
            "DELETE FROM country_zip_city WHERE country_id = %s", (country_id,)
        )
        self.invalidate_model()
        if not rows:
            return 0
        now = fields.Datetime.now()
        uid = self.env.uid or SUPERUSER_ID
        argslist = [
            (zip_code, city, code or None, state_id, country_id, uid, now, uid, now)
            for (zip_code, city, code, state_id) in rows
        ]
        sql = """
            INSERT INTO country_zip_city
                (zip, city, municipality_code, state_id, country_id,
                 create_uid, create_date, write_uid, write_date)
            VALUES %s
        """
        execute_values(self.env.cr, sql, argslist, page_size=10000)
        self.invalidate_model()
        return len(argslist)

    # -- Parsing ---------------------------------------------------------

    def _parse_at_json(self, content):
        """Return distinct AT rows from the RTR postal-code JSON table."""
        state_cache = self._state_cache_from(_AT_STATE_XMLID)
        payload = json.loads(content.decode("utf-8", errors="replace"))
        seen = set()
        for row in payload.get("data", []):
            if row.get("gueltigbis"):
                continue
            zip_code = str(row.get("plz") or "").strip()
            city = (row.get("ort") or "").strip()
            state_id = state_cache.get((row.get("bundesland") or "").strip())
            if not (zip_code and city and state_id):
                continue
            seen.add((zip_code, city, None, state_id))
        return seen

    def _parse_de_csv(self, content, cfg):
        """Return distinct DE rows from the openPLZ street CSV."""
        state_cache = self._state_cache_from(_AGS_STATE_XMLID)
        lines = content.decode(cfg["encoding"], errors="replace").splitlines()
        data_lines = lines[cfg["data_start"] :]
        seen = set()
        for row in csv.reader(data_lines, delimiter=cfg["delimiter"]):
            parsed = self._row_de(row, state_cache)
            if parsed:
                seen.add(parsed)
        return seen

    def _state_cache_from(self, mapping):
        cache = {}
        for key, xmlid in mapping.items():
            state = self.env.ref(xmlid, raise_if_not_found=False)
            if state:
                cache[key] = state.id
        return cache

    def _row_de(self, row, state_cache):
        if len(row) < 4:
            return None
        zip_code = (row[1] or "").strip()
        city = (row[2] or "").strip()
        regional_key = (row[3] or "").strip()
        state_id = state_cache.get(regional_key[:2])
        if not (zip_code and city and state_id):
            return None
        return (zip_code, city, regional_key, state_id)
