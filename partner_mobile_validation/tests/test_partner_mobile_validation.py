# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from lxml import etree

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

    def test_phone_widget_keeps_own_number(self):
        self.partner.phone = "01 234567"
        # phone_validation picks the first valid number of mobile/phone
        self.assertEqual(self.partner.phone_sanitized, "+436641234567")
        self.assertEqual(self.partner.phone_own_sanitized, "+431234567")
        self.assertEqual(self.partner.phone_own_formatted, "+43 1 234567")
        self.assertEqual(self.partner.mobile_sanitized, "+436641234567")

    def test_mobile_change_does_not_touch_phone(self):
        self.partner.phone = "01 234567"
        self.partner.mobile = "0676 7654321"
        self.assertEqual(self.partner.phone, "01 234567")
        self.assertEqual(self.partner.phone_own_formatted, "+43 1 234567")
        self.assertEqual(self.partner.mobile_formatted, "+43 676 7654321")

    def test_partner_views_use_own_phone_companion_fields(self):
        views = [
            ("base.view_partner_form", "form"),
            ("base.view_partner_simple_form", "form"),
            ("base.view_partner_tree", "list"),
            ("base.res_partner_kanban_view", "kanban"),
        ]
        for xmlid, view_type in views:
            with self.subTest(view=xmlid):
                arch = etree.fromstring(
                    self.env["res.partner"].get_view(self.env.ref(xmlid).id, view_type)[
                        "arch"
                    ]
                )
                phone_nodes = arch.xpath("//field[@name='phone'][@widget='phone']")
                self.assertTrue(phone_nodes)
                for node in phone_nodes:
                    self.assertIn("phone_own_formatted", node.get("options", ""))
                    self.assertIn("phone_own_sanitized", node.get("options", ""))
                self.assertTrue(arch.xpath("//field[@name='mobile_formatted']"))
