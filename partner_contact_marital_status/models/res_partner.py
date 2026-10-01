# -*- coding: utf-8 -*-
# Copyright 2026, Weboffice IT-Service und Marketing GmbH & Co KG

from odoo import models, fields


class ResPartner(models.Model):
    _inherit = "res.partner"

    marital_status_id = fields.Many2one('res.partner.marital.status')
