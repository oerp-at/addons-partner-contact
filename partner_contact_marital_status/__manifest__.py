# Copyright 2026, Weboffice IT-Service und Marketing GmbH & Co KG

{
    "name": "Partner Contact Marital Status",
    "summary": "Marital status on the personal information page of contacts",
    "version": "20.0.1.0.0",
    "category": "Sales/CRM",
    "author": "Weboffice IT und Marketing GmbH & CoKG,Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/partner-contact",
    "license": "AGPL-3",
    "depends": ["contacts", "partner_contact_personal_information_page"],
    "data": [
        "security/ir.access.csv",
        "data/res_partner_marital_status_data.xml",
        "views/res_partner_views.xml",
        "views/res_partner_marital_status_views.xml",
    ],
    "installable": True,
}
