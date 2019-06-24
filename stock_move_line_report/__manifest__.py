# -*- coding: utf-8 -*-

{
    'name': "stock_move_line_report",
    'category': 'Hidden',
    'version': '1.0',
    'author': 'Raul Rodriguez',
    'depends': ['product', 'stock'],
    'data': [
        'security/ir.model.access.csv',
        'report/stock_move_line_report.xml'
    ],
    'installable': True,
}
