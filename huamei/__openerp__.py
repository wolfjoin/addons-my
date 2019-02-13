# -*- coding: utf-8 -*-
{
    'name': "huamei-自定义模块",

    'summary': """
        华美亚马逊个性化定制
        """,

    'description': """
        产品增加字段；

    """,

    'author': "Wolfjoin",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/openerp/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','product','account'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'templates.xml',
        'views/product_product.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo.xml',
    ],
}