# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import re
from collections import Counter

from odoo import api, models

from ..api import openplz_client

# Drops a trailing house-number token (``11``, ``11a``, ``11-13``, ``11/2``)
# so a street can be matched by its bare name.
_HOUSE_NUMBER_RE = re.compile(r"[\s,]+\d[\w\-/]*\.?$")

# Autofill dispatch by postal-code length: (country code, config parameter,
# OpenPLZ segment). The OpenPLZ segment is ``None`` when the local directory is
# already unambiguous (Austria, from the RTR table) and no tie-break is needed.
_ZIP_COUNTRY_BY_LENGTH = {
    4: ("AT", "partner_contact_zip_autofill.at_enabled", None),
    5: ("DE", "partner_contact_zip_autofill.de_enabled", "de"),
}


def strip_house_number(street):
    """Return the street string without a trailing house-number token."""
    stripped = (street or "").strip().rstrip(",").strip()
    return _HOUSE_NUMBER_RE.sub("", stripped).strip()


class ResPartner(models.Model):
    _inherit = "res.partner"

    def _zip_autofill_enabled(self, param):
        """Return whether the address autofill is switched on for ``param``."""
        return self.env["ir.config_parameter"].sudo().get_bool(param)

    def _zip_autofill_apply(
        self, zip_value, street_value=False, *, city_fname, state_fname, country_fname
    ):
        """Fill country, city and state from the ZIP directory.

        The country is chosen from the postal-code length (4 digits -> Austria,
        5 digits -> Germany) and only when that country's integration is
        enabled. The postal code is looked up in the local directory: a unique
        city is used directly. For Germany, an ambiguous code is disambiguated
        through the OpenPLZ full-text search when a street is present; otherwise
        (or on any miss) the most common city is used. Austria uses the RTR
        table, which is already unambiguous, so it never calls OpenPLZ.
        """
        zip_norm = (zip_value or "").strip()
        dispatch = _ZIP_COUNTRY_BY_LENGTH.get(len(zip_norm))
        if not (zip_norm.isdigit() and dispatch):
            return
        country_code, param, api_code = dispatch
        if not self._zip_autofill_enabled(param):
            return
        country = self.env.ref(f"base.{country_code.lower()}", raise_if_not_found=False)
        if not country:
            return
        rows = self.env["country.zip.city"].search(
            [("country_id", "=", country.id), ("zip", "=", zip_norm)]
        )
        if not rows:
            return
        street_norm = (street_value or "").strip()
        if api_code and street_norm and len(set(rows.mapped("city"))) > 1:
            picked = self._zip_autofill_disambiguate(
                rows, api_code, zip_norm, street_norm
            )
            if picked:
                rows = picked
        self._zip_autofill_apply_rows(
            rows,
            country,
            city_fname=city_fname,
            state_fname=state_fname,
            country_fname=country_fname,
        )

    def _zip_autofill_disambiguate(self, rows, api_code, zip_norm, street_norm):
        """Narrow ambiguous rows to one city via OpenPLZ, or return empty.

        Uses the full-text search on ``<street> <plz>`` and matches the
        returned municipality back onto a directory row (by municipality code,
        then by city name). If the hits already agree on a single city that is
        used directly; only when they disagree are they narrowed to the hits
        whose street name matches the entered street. Returns an empty recordset
        when the API errors out or does not resolve to a single city, so the
        caller falls back to the deterministic pick.
        """
        trimmed = strip_house_number(street_norm) or street_norm
        try:
            results = openplz_client.fetch_fulltext(api_code, f"{trimmed} {zip_norm}")
        except openplz_client.OpenPlzApiError:
            return rows.browse()
        # Only ever trust hits for the exact postal code that was entered, so a
        # same-named street in another PLZ can never pull in the wrong city.
        matches = [
            result
            for result in results
            if str(result.get("postalCode") or "").strip() == zip_norm
        ]
        if not matches:
            return rows.browse()
        # Instant match: every hit already points at the same city.
        picked = self._zip_autofill_rows_for_hits(rows, matches)
        if len(set(picked.mapped("city"))) == 1:
            return picked
        # Otherwise narrow to the hits whose street name matches the entered
        # street (the full-text search also returns loosely-related streets,
        # e.g. "Dorfplatz" when searching "Am Dorfplatz").
        target = trimmed.strip().casefold()
        exact = [
            result
            for result in matches
            if (result.get("name") or "").strip().casefold() == target
        ]
        if exact:
            picked = self._zip_autofill_rows_for_hits(rows, exact)
            if len(set(picked.mapped("city"))) == 1:
                return picked
        return rows.browse()

    def _zip_autofill_rows_for_hits(self, rows, hits):
        """Map OpenPLZ hits back onto directory rows.

        Rows are matched by municipality code first (stable across sources),
        then by city/locality name. ``rows`` is already scoped to the entered
        postal code, so a match can only ever be a city of that PLZ.
        """
        codes = set()
        names = set()
        for hit in hits:
            municipality = hit.get("municipality") or {}
            for value in (municipality.get("key"), municipality.get("code")):
                if value:
                    codes.add(str(value).strip())
            for value in (hit.get("locality"), municipality.get("name")):
                if value:
                    names.add(value.strip().lower())
        picked = rows.filtered(lambda r: (r.municipality_code or "") in codes)
        if not picked:
            picked = rows.filtered(lambda r: (r.city or "").strip().lower() in names)
        return picked

    def _zip_autofill_apply_rows(
        self, rows, country, *, city_fname, state_fname, country_fname
    ):
        if country:
            self[country_fname] = country
        city = self._zip_autofill_most_common(rows.mapped("city"))
        if city:
            self[city_fname] = city
        state = self._zip_autofill_dominant_state(rows)
        if state:
            self[state_fname] = state

    @staticmethod
    def _zip_autofill_most_common(values):
        """Pick the most frequent value, breaking ties alphabetically."""
        counter = Counter(value for value in values if value)
        if not counter:
            return False
        top = max(counter.values())
        return min(value for value, count in counter.items() if count == top)

    def _zip_autofill_dominant_state(self, rows):
        """Pick the state covering the most rows (lowest id on a tie)."""
        counter = Counter(record.state_id.id for record in rows if record.state_id)
        if not counter:
            return self.env["res.country.state"].browse()
        top = max(counter.values())
        state_id = min(sid for sid, count in counter.items() if count == top)
        return self.env["res.country.state"].browse(state_id)

    @api.onchange("zip", "street")
    def _onchange_zip_autofill(self):
        """Fill country, city and state from the ZIP directory."""
        self._zip_autofill_apply(
            self.zip,
            self.street,
            city_fname="city",
            state_fname="state_id",
            country_fname="country_id",
        )
