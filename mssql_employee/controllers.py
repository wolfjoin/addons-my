# -*- coding: utf-8 -*-
from openerp import http

# class MssqlEmployee(http.Controller):
#     @http.route('/mssql_employee/mssql_employee/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/mssql_employee/mssql_employee/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('mssql_employee.listing', {
#             'root': '/mssql_employee/mssql_employee',
#             'objects': http.request.env['mssql_employee.mssql_employee'].search([]),
#         })

#     @http.route('/mssql_employee/mssql_employee/objects/<model("mssql_employee.mssql_employee"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('mssql_employee.object', {
#             'object': obj
#         })