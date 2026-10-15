# Copyright 2026 Weboffice IT und Marketing GmbH & CoKG
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from datetime import date, timedelta

from odoo import fields
from odoo.exceptions import ValidationError
from odoo.tests import TransactionCase


class TestPartnerDeathdate(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env["res.partner"].create(
            {"name": "Anna Muster", "birthdate_date": date(1940, 5, 10)}
        )

    def test_age_until_death(self):
        self.partner.deathdate = date(2020, 5, 9)
        self.assertEqual(self.partner.age, 79)
        self.partner.deathdate = date(2020, 5, 10)
        self.assertEqual(self.partner.age, 80)

    def test_age_without_death(self):
        self.assertGreater(self.partner.age, 80)

    def test_death_before_birth(self):
        with self.assertRaises(ValidationError):
            self.partner.deathdate = date(1930, 1, 1)

    def test_death_in_future(self):
        with self.assertRaises(ValidationError):
            self.partner.deathdate = fields.Date.today() + timedelta(days=1)
