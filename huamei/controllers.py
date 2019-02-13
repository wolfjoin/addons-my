# -*- coding: utf-8 -*-
from openerp import http

# class ./addons-my/huamei(http.Controller):
#     @http.route('/./addons-my/huamei/./addons-my/huamei/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/./addons-my/huamei/./addons-my/huamei/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('./addons-my/huamei.listing', {
#             'root': '/./addons-my/huamei/./addons-my/huamei',
#             'objects': http.request.env['./addons-my/huamei../addons-my/huamei'].search([]),
#         })

#     @http.route('/./addons-my/huamei/./addons-my/huamei/objects/<model("./addons-my/huamei../addons-my/huamei"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('./addons-my/huamei.object', {
#             'object': obj
#         })