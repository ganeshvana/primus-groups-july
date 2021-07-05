# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Purchase Portal',
    'version': '1.2',
    'category': 'Purchases',
    'sequence': 60,
    'summary': 'Purchase portal',
    'description': "",
    'website': 'https://www.odoo.com/page/purchase',
    'depends': ['purchase', 'stock', 'purchase_stock', 'oi_primus_product_extended', 'custom_primus'],
    'data': [        
        'views/portal_templates.xml',  
        'views/purchase.xml',        
    ],
    'demo': [],
    'installable': True,
    'auto_install': False,
    'application': True,
}
