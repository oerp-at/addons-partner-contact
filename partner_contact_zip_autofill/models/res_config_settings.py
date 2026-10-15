# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    at_address_autofill_enabled = fields.Boolean(
        string="Address Autofill (AT)",
        config_parameter="partner_contact_zip_autofill.at_enabled",
        help="Fill country, city and state on contacts from the Austrian ZIP "
        "directory (RTR / Austrian Post) when a 4-digit postal code is entered.",
    )
    de_address_autofill_enabled = fields.Boolean(
        string="Address Autofill (DE)",
        config_parameter="partner_contact_zip_autofill.de_enabled",
        help="Fill country, city and state on contacts from the German ZIP "
        "directory (OpenStreetMap) when a 5-digit postal code is entered.",
    )

    def action_import_zip_directory_at(self):
        return self._import_zip_directory("AT")

    def action_import_zip_directory_de(self):
        return self._import_zip_directory("DE")

    def _import_zip_directory(self, country_code):
        self.ensure_one()
        created = self.env["country.zip.city"]._import_zip_directory(country_code)
        return self._zip_directory_notification(
            self.env._(
                "Imported %(count)s %(code)s postal-code entries.",
                count=created,
                code=country_code,
            ),
            "success",
        )

    def _zip_directory_notification(self, message, notification_type):
        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "type": notification_type,
                "title": self.env._("Address Autofill"),
                "message": message,
                "sticky": False,
            },
        }
