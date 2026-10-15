# Copyright 2026, Weboffice IT-Service und Marketing GmbH & Co KG

from odoo import fields, models


class ResPartnerMaritalStatus(models.Model):
    _name = "res.partner.marital.status"
    _order = "id"
    _description = "Partner Marital Status"

    active = fields.Boolean(default=True)
    name = fields.Char(string="Marital Status", required=True, translate=True)
