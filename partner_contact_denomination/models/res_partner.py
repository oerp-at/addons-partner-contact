# Copyright 2026, Weboffice IT-Service und Marketing GmbH & Co KG

from odoo import fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    denomination_id = fields.Many2one("res.partner.denomination")
