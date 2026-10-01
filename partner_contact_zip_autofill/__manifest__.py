# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Partner contact zip autofill",
    "summary": "Autofill partner city, state and country from the official "
    "Austrian (Statistik Austria) and German (OpenStreetMap) postal-code "
    "directories, with OpenPLZ full-text search as a tie-breaker.",
    "version": "20.0.1.0.0",
    "category": "Customer Relationship Management",
    "website": "https://github.com/OCA/partner-contact",
    "author": "Weboffice IT und Marketing GmbH & CoKG,Odoo Community Association (OCA)",
    "maintainers": [],
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        "base",
        "base_setup",
        "contacts",
    ],
    "data": [
        "security/ir.access.csv",
        "views/country_zip_city_views.xml",
        "views/res_config_settings_views.xml",
    ],
}
