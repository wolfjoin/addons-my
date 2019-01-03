# -*- coding: utf-8 -*-
from openerp import http

# class ./addonsAdd/amazonPay(http.Controller):
#     @http.route('/./addons_add/amazon_pay/./addons_add/amazon_pay/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/./addons_add/amazon_pay/./addons_add/amazon_pay/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('./addons_add/amazon_pay.listing', {
#             'root': '/./addons_add/amazon_pay/./addons_add/amazon_pay',
#             'objects': http.request.env['./addons_add/amazon_pay../addons_add/amazon_pay'].search([]),
#         })

#     @http.route('/./addons_add/amazon_pay/./addons_add/amazon_pay/objects/<model("./addons_add/amazon_pay../addons_add/amazon_pay"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('./addons_add/amazon_pay.object', {
#             'object': obj
#         })