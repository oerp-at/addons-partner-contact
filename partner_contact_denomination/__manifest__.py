# Copyright 2026, Weboffice IT-Service und Marketing GmbH & Co KG

# noinspection PyStatementEffect
# pylint: disable=missing-readme
{
    "name": "Partner Contact Denomination",
    "summary": "Adds a Religious Denomination Dropdown on the OCA Personal Information page of contacts",
    "version": "19.0.2.0.0",
    "category": "Sales/CRM",
    "license": "AGPL-3",
    "author": "Weboffice IT und Marketing GmbH & CoKG, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/partner-contact",
    "depends": [
        "contacts",
        "partner_contact_personal_information_page",
    ],
    "data": [
        "security/ir.model.access.csv",
        "data/res_partner_denomination_data.xml",
        "views/res_partner_view.xml",
        "views/res_partner_denomination_views.xml",
    ],
    "installable": True,
    "application": False,
}
