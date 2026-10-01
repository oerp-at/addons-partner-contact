# -*- coding: utf-8 -*-
# Copyright 2026, Weboffice IT-Service und Marketing GmbH & Co KG

from dateutil.relativedelta import relativedelta
from odoo import models, fields, api
from odoo.exceptions import ValidationError

class ResPartner(models.Model):
    _inherit = "res.partner"

    deathdate = fields.Date(string="Date of Death")

    @api.constrains("birthdate_date", "deathdate")
    def _check_death_after_birth(self):
        for partner in self:
            if (
                partner.birthdate_date
                and partner.deathdate
                and partner.deathdate < partner.birthdate_date
            ):
                raise ValidationError(self.env._("Date of Death cannot be earlier than Birthdate."))
            if (
                partner.deathdate
                and partner.deathdate > fields.Date.today()
            ):
                raise ValidationError(self.env._("Date of Death cannot be in the future."))

    @api.depends("deathdate")
    def _compute_age(self):
        super()._compute_age()
        for rec in self:
          if rec.birthdate_date and rec.deathdate:
                if rec.deathdate >= rec.birthdate_date:
                    rec.age = relativedelta(rec.deathdate, rec.birthdate_date).years
