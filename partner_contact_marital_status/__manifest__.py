# -*- coding: utf-8 -*-
# Copyright 2026, Weboffice IT-Service und Marketing GmbH & Co KG

# noinspection PyStatementEffect
# pylint: disable=missing-readme
{
    "name": "Partner Contact Marital Status",
    "version": "19.0.2.0.0",
    'category': 'Sales/CRM',
    'author': 'Weboffice IT-Service und Marketing GmbH & Co KG',
    'website': 'https://weboffice.at',
    'license': 'OPL-1',
    'depends': ['contacts', 'partner_contact_personal_information_page'],

    'data': [
        'security/ir.model.access.csv',
        'data/res_partner_marital_status_data.xml',
        'views/res_partner_views.xml',
        'views/res_partner_marital_status_views.xml',
    ],

    'installable': True
}

