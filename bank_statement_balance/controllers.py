# -*- coding: utf-8 -*-
from openerp import http

# class BankStatementBalance(http.Controller):
#     @http.route('/bank_statement_balance/bank_statement_balance/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/bank_statement_balance/bank_statement_balance/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('bank_statement_balance.listing', {
#             'root': '/bank_statement_balance/bank_statement_balance',
#             'objects': http.request.env['bank_statement_balance.bank_statement_balance'].search([]),
#         })

#     @http.route('/bank_statement_balance/bank_statement_balance/objects/<model("bank_statement_balance.bank_statement_balance"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('bank_statement_balance.object', {
#             'object': obj
#         })