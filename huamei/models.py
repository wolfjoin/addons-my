# -*- coding: utf-8 -*-

from openerp import models, fields, api

class ProductAmazon(models.Model):
	_inherit = 'product.product'

	length_product = fields.Float('Length')
	width_product = fields.Float('Width')
	height_product = fields.Float('Height')
	unit_product = fields.Many2one('product.uom',domain=[('category_id','=',"Length / Distance")])
	volume = fields.Float('Volume of Product', compute='_calc_volume_product')

	length_package = fields.Float('Length')
	width_package = fields.Float('Width')
	height_package = fields.Float('Height')
	unit_package = fields.Many2one('product.uom',domain=[('category_id','=',"Length / Distance")])
	volume_package = fields.Float('Volume', compute='_calc_volume_package')

	ean13 = fields.Char('barcode', help="商品实物标签条码，亚马逊对应FNSKU，以X开头")

	asin = fields.Char('ASIN', help="ASIN码(AMAZON STANDARD IDENTIFICATION NUMBER)是亚马逊自己的商品编号，"
		"由亚马逊系统自动生成的，不需要卖家自行添加。ASIN码相当于一个独特的产品ID，在亚马逊平台上具有唯一性，"
		"同一个产品同一个UPC在不同站点对应的ASIN通常是一致的，即一个ASIN码对应一个SKU。"
		"在平台前端和卖家店铺后台都可以使用ASIN码来查询到产品。")


	@api.onchange('length_product','width_product','height_product')
	def _calc_volume_product(self):
		for r in self:
			r.volume = r.length_product * r.width_product * r.height_product

	@api.onchange('length_package','width_package','height_package')
	def _calc_volume_package(self):
		for r in self:
			r.volume_package = r.length_package * r.width_package * r.height_package


	# 修改ean13条码验证无约束
	def _check_ean_key(self, cr, uid, ids, context=None):
		return True

	_constraints = [(_check_ean_key, '', ['ean13'])]

class AccountInvoiceLineAdd(models.Model):
	_inherit = 'account.invoice.line'

	sku = fields.Char('SKU', help="自定义内部产品编码")
	transaction_type = fields.Char('transaction-type')
	amount_type = fields.Char('amount-type')
	amount_description = fields.Char('amount-description')

class AccountInvoiceAdd(models.Model):
	_inherit = 'account.invoice'

	settlement_id = fields.Char('Settlement id')
	