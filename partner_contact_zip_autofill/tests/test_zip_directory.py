# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import json
from unittest.mock import patch

import requests

from odoo.tests.common import TransactionCase

_MODULE = "odoo.addons.partner_contact_zip_autofill.models.country_zip_city"

# RTR postal-code table (JSON). One row per (plz, bezirk); a postal code always
# resolves to a single "ort". B -> Burgenland, St -> Steiermark, W -> Wien.
AT_ROWS = [
    {
        "plz": 7000,
        "ort": "Eisenstadt",
        "bundesland": "B",
        "bezirk": "Eisenstadt(Stadt)",
        "gueltigbis": None,
    },
    {
        "plz": 8410,
        "ort": "Wildon",
        "bundesland": "St",
        "bezirk": "Leibnitz",
        "gueltigbis": None,
    },
    {
        "plz": 1010,
        "ort": "Wien",
        "bundesland": "W",
        "bezirk": "Wien  1.,Innere Stadt",
        "gueltigbis": None,
    },
    # Same code, second district row -> collapses into one (zip, city) entry.
    {
        "plz": 1010,
        "ort": "Wien",
        "bundesland": "W",
        "bezirk": "Wien (duplicate)",
        "gueltigbis": None,
    },
    # Expired entry -> skipped.
    {
        "plz": 9999,
        "ort": "Altort",
        "bundesland": "St",
        "bezirk": "Irgendwo",
        "gueltigbis": "2000-01-01",
    },
]

# Name,PostalCode,Locality,RegionalKey,Borough,Suburb (comma-separated).
# 08 -> Baden-Württemberg, 16 -> Thüringen.
DE_LINES = [
    "Name,PostalCode,Locality,RegionalKey,Borough,Suburb",
    "Hauptstraße,70173,Stuttgart,08111000,,",
    '"Königstraße",70173,Stuttgart,08111000,Mitte,',
    "Bahnhofstraße,99084,Erfurt,16051000,,",
]

AT_CONTENT = json.dumps({"data": AT_ROWS, "status": 200}).encode("utf-8")
DE_CONTENT = "\n".join(DE_LINES).encode("utf-8")


class _FakeResponse:
    def __init__(self, content):
        self.content = content
        self.status_code = 200
        self.headers = {"Content-Type": "application/json"}

    def raise_for_status(self):
        return None


def _fake_get(url, timeout=None, **kwargs):
    content = DE_CONTENT if "openplzapi.data" in url else AT_CONTENT
    return _FakeResponse(content)


class TestZipDirectory(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.City = cls.env["country.zip.city"]
        # Start from an empty directory so assertions are independent of any
        # real data already imported into this database (rolled back on teardown).
        cls.env.cr.execute("DELETE FROM country_zip_city")
        cls.City.invalidate_model()

    def _import(self, country_code):
        with patch(f"{_MODULE}.requests.get", side_effect=_fake_get):
            return self.City._import_zip_directory(country_code)

    def test_at_import_creates_distinct_city_rows(self):
        created = self._import("AT")
        # The duplicate 1010 district row collapses; the expired 9999 is skipped.
        self.assertEqual(created, 3)
        self.assertEqual(self.City.search_count([]), 3)

        eisenstadt = self.City.search([("zip", "=", "7000")])
        self.assertEqual(eisenstadt.city, "Eisenstadt")
        # Austria has no municipality code in the RTR table.
        self.assertFalse(eisenstadt.municipality_code)
        self.assertEqual(eisenstadt.state_id, self.env.ref("base.state_at_1"))
        self.assertEqual(eisenstadt.country_id, self.env.ref("base.at"))

        wien = self.City.search([("zip", "=", "1010")])
        self.assertEqual(wien.city, "Wien")
        self.assertEqual(wien.state_id, self.env.ref("base.state_at_9"))

        self.assertFalse(self.City.search([("zip", "=", "9999")]))

    def test_de_import_creates_distinct_city_rows(self):
        created = self._import("DE")
        # Both Stuttgart street rows collapse into one (zip, city) entry.
        self.assertEqual(created, 2)

        stuttgart = self.City.search([("zip", "=", "70173")])
        self.assertEqual(stuttgart.city, "Stuttgart")
        self.assertEqual(stuttgart.state_id, self.env.ref("base.state_de_bw"))
        self.assertEqual(stuttgart.country_id, self.env.ref("base.de"))

        erfurt = self.City.search([("zip", "=", "99084")])
        self.assertEqual(erfurt.city, "Erfurt")
        self.assertEqual(erfurt.state_id, self.env.ref("base.state_de_th"))

    def test_reimport_replaces_country_rows(self):
        self._import("AT")
        first = self.City.search_count([])
        created = self._import("AT")
        self.assertEqual(created, first)
        self.assertEqual(self.City.search_count([]), first)

    def test_at_and_de_coexist(self):
        self._import("AT")
        self._import("DE")
        self.assertEqual(
            self.City.search_count([("country_id", "=", self.env.ref("base.at").id)]),
            3,
        )
        self.assertEqual(
            self.City.search_count([("country_id", "=", self.env.ref("base.de").id)]),
            2,
        )

    def test_download_error_leaves_data_untouched(self):
        def _boom(*args, **kwargs):
            raise requests.exceptions.ConnectionError("down")

        with (
            self.assertRaises(requests.exceptions.ConnectionError),
            patch(f"{_MODULE}.requests.get", side_effect=_boom),
        ):
            self.City._import_zip_directory("AT")
        self.assertEqual(self.City.search_count([]), 0)
