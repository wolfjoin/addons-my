# -*- coding: utf-8 -*-
{
    'name': "amazon_pay",

    'summary': """
        按照亚马逊结算报告模板V2格式设置字段，
        添加到银行表单明细后""",

    'description': """
        按照亚马逊结算报告模板V2格式设置字段，
        添加到银行表单明细account.bank.statement.line后
        通过内连接

    """,

    'author': "Your Company",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/openerp/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','account'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo.xml',
    ],
}