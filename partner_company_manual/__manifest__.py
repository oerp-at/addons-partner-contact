# Copyright 2026 Weboffice IT und Marketing GmbH & CoKG
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Partner Company Manual",
    "version": "20.0.1.0.0",
    "category": "Customer Relationship Management",
    "license": "AGPL-3",
    "summary": "Restore the manual person/company toggle on partners",
    "author": "Weboffice IT und Marketing GmbH & CoKG,Odoo Community Association (OCA)",
    "development_status": "Beta",
    "website": "https://github.com/OCA/partner-contact",
    "depends": ["base"],
    "data": [
        "views/res_partner_views.xml",
    ],
    "post_init_hook": "post_init_hook",
    "installable": True,
}
