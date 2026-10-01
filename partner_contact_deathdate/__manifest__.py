# Copyright 2026, Weboffice IT-Service und Marketing GmbH & Co KG

{
    "name": "Partner Date of Death",
    "summary": "Adds a Date of Death field on the OCA Personal Information page of contacts and computes age using OCA birthdate",
    "version": "19.0.1.0.1",
    "category": "Customer Relationship Management",
    "license": "AGPL-3",
    "author": "Weboffice IT und Marketing GmbH & CoKG",
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
