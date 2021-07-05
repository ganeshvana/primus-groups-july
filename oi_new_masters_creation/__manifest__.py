# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'FrankAirjet',
    'version': '1.1',
    'category': '',
    'summary': '',
    'depends':['base','sale'],
    'data': [  
	'security/ir.model.access.csv',
	'views/fields_creation.xml'
            ],
    'installable': True,
    'application':True,
    'auto_install': False
}
