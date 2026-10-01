# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Partner contact zip autofill",
    "summary": "Autofill partner city, state and country from the official "
    "Austrian (Statistik Austria) and German (OpenStreetMap) postal-code "
    "directories, with OpenPLZ full-text search as a tie-breaker.",
    "version": "19.0.6.0.2",
    "category": "Customer Relationship Management",
    "website": "https://github.com/OCA/partner-contact",
    "author": "Odoo Community Association (OCA), Weboffice IT-Service und Marketing GmbH & Co KG",
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
        "security/ir.model.access.csv",
        "views/country_zip_city_views.xml",
        "views/res_config_settings_views.xml",
    ],
}
