# Copyright 2025 Akretion France (https://www.akretion.com/)
# @author: Alexis de Lattre <alexis.delattre@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    # Since 20.0, phone_validation keeps the raw number and the phone widget
    # displays <fname>_formatted and dials <fname>_sanitized instead.
    mobile_sanitized = fields.Char(
        compute="_compute_number_companion_fields",
        export_string_translation=False,
        help="Mobile number in E164 format, used by the phone widget to dial.",
    )
    mobile_formatted = fields.Char(
        compute="_compute_number_companion_fields",
        export_string_translation=False,
        help="Mobile number in international format, displayed by the phone widget.",
    )

    # For phone, the default companion names phone_formatted/phone_sanitized
    # belong to mail.thread.phone and hold the first valid number of
    # mobile/phone, so the phone widget of phone would show and dial the
    # mobile number. Give phone its own companion fields, so each widget
    # shows and dials the number of its own field.
    phone_own_sanitized = fields.Char(
        compute="_compute_number_companion_fields",
        export_string_translation=False,
        help="Phone number in E164 format, used by the phone widget to dial.",
    )
    phone_own_formatted = fields.Char(
        compute="_compute_number_companion_fields",
        export_string_translation=False,
        help="Phone number in international format, displayed by the phone widget.",
    )

    @api.depends(lambda self: self._phone_get_sanitize_triggers())
    def _compute_number_companion_fields(self):
        self._phone_update_companion_fields(("mobile",))
        for partner in self:
            sanitized = partner._phone_format(fname="phone") or False
            partner.phone_own_sanitized = sanitized
            partner.phone_own_formatted = partner._phone_get_formatted(sanitized)

    # no need to inherit the method _phone_get_number_fields() because by default
    # it has 'phone' and 'mobile' if the 2 fields exist on self
