# -*- coding: utf-8 -*-
{
    'name': "Primus Customisations",

    'summary': """
        Primus Customisations""",

    'description': """
        Primus Customisations
    """,

    'author': "My Company",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'sale', 'mrp', 'product','uom','stock', 'mrp_subcontracting', 'oi_primus_product_extended'],
# , 'website_sale'
    # always loaded
    'data': [
        'security/product_bom.xml',
        'security/ir.model.access.csv',
        'views/sale_views.xml',
        'views/sequence.xml',
    ],
    # only loaded in demonstration mode
    
}
