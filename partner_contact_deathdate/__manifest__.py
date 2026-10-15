# Copyright 2026, Weboffice IT-Service und Marketing GmbH & Co KG

{
    "name": "Partner Date of Death",
    "summary": "Date of death on contacts, age is computed up to the death",
    "version": "20.0.1.0.0",
    "category": "Customer Relationship Management",
    "license": "AGPL-3",
    "author": "Weboffice IT und Marketing GmbH & CoKG,Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/partner-contact",
    "depends": [
        "contacts",
        "partner_contact_personal_information_page",
        "partner_contact_birthdate",
    ],
    "data": [
        "views/res_partner_view.xml",
    ],
    "installable": True,
    "application": False,
}
