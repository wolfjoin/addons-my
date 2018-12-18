# -*- coding: utf-8 -*-
from openerp import http

# class Ysale(http.Controller):
#     @http.route('/ysale/ysale/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/ysale/ysale/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('ysale.listing', {
#             'root': '/ysale/ysale',
#             'objects': http.request.env['ysale.ysale'].search([]),
#         })

#     @http.route('/ysale/ysale/objects/<model("ysale.ysale"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('ysale.object', {
#             'object': obj
#         })