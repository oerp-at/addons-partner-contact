# Copyright 2026 Weboffice IT und Marketing GmbH & CoKG
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests import Form, TransactionCase

from ..hooks import post_init_hook

VALID_VAT = "ATU12345675"


class TestPartnerCompanyManual(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.Partner = cls.env["res.partner"]
        cls.austria = cls.env.ref("base.at")

    def test_automatic_without_manual_type(self):
        """Without a manual type the Odoo rule (VAT) decides."""
        person = self.Partner.create({"name": "Max Mustermann"})
        company = self.Partner.create(
            {"name": "Muster GmbH", "country_id": self.austria.id, "vat": VALID_VAT}
        )
        self.assertFalse(person.is_company_manual)
        self.assertFalse(person.is_company)
        self.assertEqual(person.company_type, "person")
        self.assertFalse(company.is_company_manual)
        self.assertTrue(company.is_company)
        self.assertEqual(company.company_type, "company")

    def test_company_without_vat(self):
        """A company without VAT stays a company, also after VAT changes."""
        partner = self.Partner.create(
            {"name": "Pfarre Breitenlee", "company_type": "company"}
        )
        self.assertEqual(partner.is_company_manual, "company")
        self.assertTrue(partner.is_company)
        partner.write({"country_id": self.austria.id, "vat": VALID_VAT})
        partner.write({"vat": "/"})
        self.assertTrue(partner.is_company)

    def test_person_with_vat(self):
        """A manual person stays a person even with a VAT."""
        partner = self.Partner.create(
            {
                "name": "Eva Einzelunternehmerin",
                "country_id": self.austria.id,
                "vat": VALID_VAT,
                "company_type": "person",
            }
        )
        self.assertFalse(partner.is_company)

    def test_toggle(self):
        partner = self.Partner.create({"name": "Toggle Test"})
        partner.company_type = "company"
        self.assertTrue(partner.is_company)
        partner.company_type = "person"
        self.assertFalse(partner.is_company)
        self.assertEqual(partner.is_company_manual, "person")

    def test_is_company_in_vals(self):
        """Code that still writes is_company (API up to 19.0) keeps working."""
        partner = self.Partner.create({"name": "Legacy GmbH", "is_company": True})
        self.assertEqual(partner.is_company_manual, "company")
        self.assertTrue(partner.is_company)
        partner.write({"is_company": False})
        self.assertEqual(partner.is_company_manual, "person")
        self.assertFalse(partner.is_company)

    def test_copy_keeps_manual_type(self):
        partner = self.Partner.create({"name": "Copy GmbH", "company_type": "company"})
        self.assertTrue(partner.copy().is_company)

    def test_form_toggle(self):
        """The radio in the form switches is_company immediately (onchange)."""
        with Form(self.Partner, view="base.view_partner_form") as partner_form:
            self.assertFalse(partner_form.is_company)
            partner_form.company_type = "company"
            self.assertTrue(partner_form.is_company)
            partner_form.name = "Standesamt Wien-Ottakring"
        partner = partner_form.save()
        self.assertTrue(partner.is_company)
        self.assertEqual(partner.is_company_manual, "company")

    def test_post_init_hook_freezes_state(self):
        company = self.Partner.create({"name": "Old Company", "is_company": True})
        person = self.Partner.create({"name": "Old Person"})
        self.env.flush_all()
        self.env.cr.execute(
            "UPDATE res_partner SET is_company_manual = NULL WHERE id IN %s",
            (tuple((company | person).ids),),
        )
        (company | person).invalidate_recordset(["is_company_manual"])
        post_init_hook(self.env)
        (company | person).invalidate_recordset(["is_company_manual"])
        self.assertEqual(company.is_company_manual, "company")
        self.assertEqual(person.is_company_manual, "person")
