{
    'name': 'purchase_sample',
    'version': '2.0',
    'category': 'Sales_order',
    'author': 'Gowthamjohn',
    'sequence': -10,
    'summary': 'Sales_order',
    'website': 'https://www.shope.com',
    'depends': ['sale','purchase'],
    'data': [
        # 'security/ir.model.access.csv',
        'views/purchase.xml'
    ],
    'demo': [],
    'installable': True,
    'application': True,
    'auto_install': False,
}
