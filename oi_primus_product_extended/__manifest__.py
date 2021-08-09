# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Product Master - Extended',
    'version': '14.0.1.0',
    'category': 'Inventory',
    'summary': 'Product Master - Extended',
    'description': "",
    'website': 'https://www.odooimplementers.com',
    'depends': ['base','l10n_in','stock','product','account', 'mrp', 'secondary_uom_app', 'website_sale', 'custom_primus'],
    'data': [
        'security/ir.model.access.csv',
        'security/bulk_product.xml',
        'wizard/template_mass_edit.xml',
        'views/sequence.xml',
		'views/product_template_view.xml'

    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}
