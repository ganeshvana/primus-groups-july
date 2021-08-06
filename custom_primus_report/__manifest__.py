# -*- coding: utf-8 -*-
{
    'name': "Primus Reports",

    'summary': """
        Primus Reports""",

    'description': """
        Primus Reports
    """,

    'author': "My Company",
    'website': "http://www.yourcompany.com",

    'category': 'Uncategorized',
    'version': '0.1',

    'depends': ['base', 'account'],

    'data': [
        'security/ir.model.access.csv',
        'wizard/sku_template.xml',
        'views/report_views.xml',
    ],
    
}
