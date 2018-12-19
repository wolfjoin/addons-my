# -*- coding: utf-8 -*-

from openerp import models, fields, api

class YsaleOrder(models.Model):
    _name = 'ysale.order'
    _description = 'Sale Order'

    name = fields.Char(string='订单号')
    order_line_ids = fields.One2many('ysale.order.line', 'order_id', string='订单明细', copy=True)
    pay_ids = fields.One2many('ysale.pay', 'order_id', string="付款明细")
    amount_total = fields.Float(string='总计金额', store=True, readonly=True, compute='_amount_all', track_visibility='always')

    @api.one
    @api.depends('order_line_ids.subtotal')
    def _amount_all(self):
    	for order in self:
	    	for line in self.order_line_ids:
	    		order.amount_total += line.subtotal

class YsaleOrderLine(models.Model):
	_name = 'ysale.order.line'
	_description = 'Sale Order Line'

	order_id = fields.Many2one('ysale.order', string='订单号', required=True, ondelete='cascade', index=True)
	name = fields.Char(string='备注')
	quantity = fields.Float(string='数量')
	price_unit = fields.Float(string='单价')
	shipping_price = fields.Float(string='运费')
	product_id = fields.Many2one('yproduct.product', string='产品', index=True)
	subtotal = fields.Float(string='金额', store=True, readonly=True, compute='_compute_amount')

	@api.multi
	@api.depends('quantity', 'price_unit')
	def _compute_amount(self):
		"""
		计算订单行金额
		"""
		for line in self:
			line.subtotal = line.quantity * line.price_unit




class YproductProdct(models.Model):
	_name = 'yproduct.product'
	_description = 'Yprodct Product'

	name = fields.Char('名称')
	sku = fields.Char('Sku')


class YsalePay(models.Model):
	_name = 'ysale.pay'
	_description = 'Ysale Pay'

	name = fields.Char('内容')
	order_id = fields.Many2one('ysale.order', string='订单号')
	product_id = fields.Many2one('yproduct.product', string='产品')
	order_type = fields.Selection([
		('order', '订单付款'),
		('service', '服务费'),
		('orther', '其他'),
		('oback','退款'),
		], string='交易类型', index=True)
	money = fields.Float('金额')
