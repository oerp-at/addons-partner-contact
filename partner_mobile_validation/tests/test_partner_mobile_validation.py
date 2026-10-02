# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestPartnerMobileValidation(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env["res.partner"].create(
            {
                "name": "Mobile Test",
                "country_id": cls.env.ref("base.at").id,
                "mobile": "0664 1234567",
            }
        )

    def test_mobile_companion_fields(self):
        self.assertEqual(self.partner.mobile, "0664 1234567")
        self.assertEqual(self.partner.mobile_sanitized, "+436641234567")
        self.assertEqual(self.partner.mobile_formatted, "+43 664 1234567")

    def test_mobile_companion_fields_follow_country(self):
        self.partner.country_id = self.env.ref("base.be")
        self.partner.mobile = "0456 99 88 77"
        self.assertEqual(self.partner.mobile_sanitized, "+32456998877")
        self.assertEqual(self.partner.mobile_formatted, "+32 456 99 88 77")

    def test_mobile_invalid_number_falls_back_to_raw_value(self):
        self.partner.mobile = "abc"
        self.assertFalse(self.partner.mobile_sanitized)
        self.assertFalse(self.partner.mobile_formatted)
