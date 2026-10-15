# Copyright 2026 Weboffice IT und Marketing GmbH & CoKG
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models

COMPANY_TYPE_SELECTION = [("person", "Person"), ("company", "Company")]


class ResPartner(models.Model):
    _inherit = "res.partner"

    is_company_manual = fields.Selection(
        selection=COMPANY_TYPE_SELECTION,
        string="Manual Company Type",
        copy=True,
        help="Person/company type chosen by the user. When empty, Odoo decides "
        "(own commercial entity with a VAT, refined by localizations).",
    )
    # Interface field like company_type up to 19.0, do not use it in business logic
    company_type = fields.Selection(
        selection=COMPANY_TYPE_SELECTION,
        compute="_compute_company_type",
        inverse="_inverse_company_type",
        readonly=False,
    )

    @api.depends("is_company_manual")
    def _compute_is_company(self):
        result = super()._compute_is_company()
        for partner in self.filtered("is_company_manual"):
            partner.is_company = partner.is_company_manual == "company"
        return result

    @api.depends("is_company")
    def _compute_company_type(self):
        for partner in self:
            partner.company_type = "company" if partner.is_company else "person"

    def _inverse_company_type(self):
        for partner in self:
            partner.is_company_manual = partner.company_type

    @api.onchange("company_type")
    def _onchange_company_type(self):
        for partner in self:
            partner.is_company_manual = partner.company_type

    @api.model
    def _vals_with_manual_company_type(self, vals):
        """Map an explicit is_company (API up to 19.0) to the manual type."""
        if "is_company" in vals and not {"is_company_manual", "company_type"} & set(
            vals
        ):
            # is_company stays in vals for other overrides (e.g. partner_firstname)
            vals = dict(
                vals, is_company_manual="company" if vals["is_company"] else "person"
            )
        return vals

    @api.model_create_multi
    def create(self, vals_list):
        vals_list = [self._vals_with_manual_company_type(vals) for vals in vals_list]
        return super().create(vals_list)

    def write(self, vals):
        return super().write(self._vals_with_manual_company_type(vals))
