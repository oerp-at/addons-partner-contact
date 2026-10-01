# Copyright 2026, Weboffice IT-Service und Marketing GmbH & Co KG

from odoo import fields, models


class ResPartnerDenomination(models.Model):
    _name = "res.partner.denomination"
    _order = "id"
    _description = "Partner Denomination"

    active = fields.Boolean(default=True)
    name = fields.Char(required=True, translate=True)
