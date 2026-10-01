# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from unittest.mock import patch

from odoo.tests.common import TransactionCase

from odoo.addons.partner_contact_zip_autofill.api.openplz_client import (
    OpenPlzApiError,
)

_CLIENT = "odoo.addons.partner_contact_zip_autofill.api.openplz_client"


class TestZipAutofill(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.country_at = cls.env.ref("base.at")
        cls.country_de = cls.env.ref("base.de")
        cls.state_b = cls.env.ref("base.state_at_1")
        cls.state_n = cls.env.ref("base.state_at_3")
        cls.state_st = cls.env.ref("base.state_at_6")
        cls.state_w = cls.env.ref("base.state_at_9")
        cls.state_be = cls.env.ref("base.state_de_be")
        cls.state_by = cls.env.ref("base.state_de_by")
        cls.state_bw = cls.env.ref("base.state_de_bw")
        cls.state_th = cls.env.ref("base.state_de_th")
        cls.state_sn = cls.env.ref("base.state_de_sn")
        params = cls.env["ir.config_parameter"]
        params.set_bool("partner_contact_zip_autofill.at_enabled", True)
        params.set_bool("partner_contact_zip_autofill.de_enabled", True)
        # Start from an empty directory so the seeded rows are the only matches,
        # independent of any real data already imported (rolled back on teardown).
        cls.env.cr.execute("DELETE FROM country_zip_city")
        cls.env["country.zip.city"].invalidate_model()
        cls.env["country.zip.city"].create(
            [
                # -- Austria (4-digit, from RTR: unambiguous, no muni code) ---
                {"zip": "1010", "city": "Wien", "state_id": cls.state_w.id},
                {"zip": "7000", "city": "Eisenstadt", "state_id": cls.state_b.id},
                # A deliberately ambiguous AT code to prove Austria never calls
                # OpenPLZ and falls back to the deterministic pick instead.
                {"zip": "9999", "city": "StadtA", "state_id": cls.state_st.id},
                {"zip": "9999", "city": "StadtA", "state_id": cls.state_n.id},
                {"zip": "9999", "city": "StadtB", "state_id": cls.state_n.id},
                # -- Germany (5-digit) ------------------------------------
                {
                    "zip": "10115",
                    "city": "Berlin",
                    "municipality_code": "11000000",
                    "state_id": cls.state_be.id,
                },
                {
                    "zip": "80331",
                    "city": "München",
                    "municipality_code": "09162000",
                    "state_id": cls.state_by.id,
                },
                # Ambiguous 99999: Alt (Thüringen, 2 rows) vs Neu (BW, 1 row).
                {
                    "zip": "99999",
                    "city": "Alt",
                    "municipality_code": "16051000",
                    "state_id": cls.state_th.id,
                },
                {
                    "zip": "99999",
                    "city": "Alt",
                    "municipality_code": "16052000",
                    "state_id": cls.state_th.id,
                },
                {
                    "zip": "99999",
                    "city": "Neu",
                    "municipality_code": "08111000",
                    "state_id": cls.state_bw.id,
                },
                # Shared code where the full-text search returns two *different*
                # streets; only "Am Dorfplatz" belongs to Riesa.
                {
                    "zip": "01594",
                    "city": "Hirschstein",
                    "municipality_code": "14627220",
                    "state_id": cls.state_sn.id,
                },
                {
                    "zip": "01594",
                    "city": "Riesa",
                    "municipality_code": "14627230",
                    "state_id": cls.state_sn.id,
                },
                {
                    "zip": "01594",
                    "city": "Stauchitz",
                    "municipality_code": "14627260",
                    "state_id": cls.state_sn.id,
                },
            ]
        )

    def _fill(self, zip_value, street_value=False, api=None):
        """Fill a new partner, patching the OpenPLZ full-text search.

        ``api`` may be a list of result rows, or an exception instance to raise.
        Returns the partner and the patched mock (to assert call behaviour).
        """
        with patch("%s.fetch_fulltext" % _CLIENT) as mock:
            if isinstance(api, Exception):
                mock.side_effect = api
            else:
                mock.return_value = api or []
            partner = self.env["res.partner"].new(
                {"name": "ZIP Autofill Test", "zip": zip_value, "street": street_value}
            )
            partner._onchange_zip_autofill()
        return partner, mock

    @staticmethod
    def _de_result(municipality_key, locality):
        return [
            {
                "postalCode": "99999",
                "locality": locality,
                "municipality": {"key": municipality_key, "name": locality},
                "federalState": {"key": municipality_key[:2], "name": locality},
            }
        ]

    # -- Austria: unambiguous, never calls OpenPLZ -----------------------

    def test_at_unique_zip_sets_city_without_api(self):
        partner, mock = self._fill("1010")
        self.assertEqual(partner.country_id, self.country_at)
        self.assertEqual(partner.city, "Wien")
        self.assertEqual(partner.state_id, self.state_w)
        mock.assert_not_called()

    def test_at_unique_zip_ignores_street_and_api(self):
        partner, mock = self._fill("7000", "Untere Kirchberggasse 5")
        self.assertEqual(partner.city, "Eisenstadt")
        self.assertEqual(partner.state_id, self.state_b)
        mock.assert_not_called()

    def test_at_ambiguous_never_calls_api_picks_most_common(self):
        partner, mock = self._fill("9999", "Andere Gasse 5")
        self.assertEqual(partner.city, "StadtA")
        mock.assert_not_called()

    def test_at_ambiguous_no_street_picks_most_common(self):
        partner, mock = self._fill("9999")
        self.assertEqual(partner.city, "StadtA")
        mock.assert_not_called()

    # -- Germany: unique -------------------------------------------------

    def test_de_unique_zip_sets_city_without_api(self):
        partner, mock = self._fill("10115", "Invalidenstraße 12")
        self.assertEqual(partner.country_id, self.country_de)
        self.assertEqual(partner.city, "Berlin")
        self.assertEqual(partner.state_id, self.state_be)
        mock.assert_not_called()

    # -- Germany: ambiguous + street -> OpenPLZ --------------------------

    def test_de_ambiguous_street_resolves_via_api(self):
        partner, mock = self._fill(
            "99999", "Musterweg 2", api=self._de_result("08111000", "Neu")
        )
        self.assertEqual(partner.city, "Neu")
        self.assertEqual(partner.state_id, self.state_bw)
        mock.assert_called_once()

    def test_de_ambiguous_street_name_filters_loose_hits(self):
        # Full-text search returns two *different* streets; only "Am Dorfplatz"
        # belongs to Riesa, so the entered street must pin it down.
        result = [
            {
                "name": "Am Dorfplatz",
                "postalCode": "01594",
                "locality": "Riesa",
                "municipality": {"key": "14627230", "name": "Riesa, Stadt"},
                "federalState": {"key": "14", "name": "Sachsen"},
            },
            {
                "name": "Dorfplatz",
                "postalCode": "01594",
                "locality": "Stauchitz",
                "municipality": {"key": "14627260", "name": "Stauchitz"},
                "federalState": {"key": "14", "name": "Sachsen"},
            },
        ]
        partner, mock = self._fill("01594", "Am Dorfplatz 22", api=result)
        self.assertEqual(partner.city, "Riesa")
        self.assertEqual(partner.state_id, self.state_sn)
        mock.assert_called_once()

    def test_de_ambiguous_instant_match_skips_street_filter(self):
        # Both hits already point at Riesa (different streets, same city), so it
        # resolves even though neither name equals the entered street.
        result = [
            {
                "name": "Hauptstraße",
                "postalCode": "01594",
                "locality": "Riesa",
                "municipality": {"key": "14627230", "name": "Riesa, Stadt"},
                "federalState": {"key": "14", "name": "Sachsen"},
            },
            {
                "name": "Bahnhofstraße",
                "postalCode": "01594",
                "locality": "Riesa",
                "municipality": {"key": "14627230", "name": "Riesa, Stadt"},
                "federalState": {"key": "14", "name": "Sachsen"},
            },
        ]
        partner, _mock = self._fill("01594", "Irgendeinweg 1", api=result)
        self.assertEqual(partner.city, "Riesa")

    def test_de_ambiguous_api_miss_falls_back(self):
        partner, mock = self._fill("99999", "Unbekanntgasse 1", api=[])
        self.assertEqual(partner.city, "Alt")
        self.assertEqual(partner.state_id, self.state_th)
        mock.assert_called_once()

    def test_de_ambiguous_api_error_falls_back(self):
        partner, _mock = self._fill("99999", "Musterweg 2", api=OpenPlzApiError())
        self.assertEqual(partner.city, "Alt")
        self.assertEqual(partner.state_id, self.state_th)

    def test_de_ambiguous_no_street_picks_most_common(self):
        partner, mock = self._fill("99999")
        self.assertEqual(partner.city, "Alt")
        self.assertEqual(partner.state_id, self.state_th)
        mock.assert_not_called()

    # -- Guard rails ------------------------------------------------------

    def test_at_disabled_does_nothing(self):
        self.env["ir.config_parameter"].set_bool(
            "partner_contact_zip_autofill.at_enabled", False
        )
        try:
            partner, _mock = self._fill("1010", "Rotenturmstraße 11")
            self.assertFalse(partner.country_id)
            self.assertFalse(partner.city)
            self.assertFalse(partner.state_id)
        finally:
            self.env["ir.config_parameter"].set_bool(
                "partner_contact_zip_autofill.at_enabled", True
            )

    def test_de_disabled_does_nothing(self):
        self.env["ir.config_parameter"].set_bool(
            "partner_contact_zip_autofill.de_enabled", False
        )
        try:
            partner, _mock = self._fill("10115", "Invalidenstraße 12")
            self.assertFalse(partner.country_id)
            self.assertFalse(partner.city)
        finally:
            self.env["ir.config_parameter"].set_bool(
                "partner_contact_zip_autofill.de_enabled", True
            )

    def test_unknown_zip_does_nothing(self):
        partner, _mock = self._fill("2222")
        self.assertFalse(partner.country_id)
        self.assertFalse(partner.city)
        self.assertFalse(partner.state_id)

    def test_wrong_zip_length_does_nothing(self):
        for zip_value in ("101", "123456", "abcd"):
            with self.subTest(zip=zip_value):
                partner, _mock = self._fill(zip_value)
                self.assertFalse(partner.country_id)
                self.assertFalse(partner.city)
                self.assertFalse(partner.state_id)
