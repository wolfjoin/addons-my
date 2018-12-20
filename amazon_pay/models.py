# -*- coding: utf-8 -*-
import openerp.addons.decimal_precision as dp

from openerp import models, fields, api

class AmazonPay(models.Model):
	_inherit = 'account.bank.statement.line'

	amount_type = fields.Char(string="amount-type")
	transaction_type = fields.Char(string="transaction-type")
	amount_type = fields.Char(string="amount-type")
	amount_description = fields.Char(string="amount-description")
	product_id = fields.Many2one('product.product', string="sku")
	quantity_purchased = fields.Float(string="quantity-purchased",
										digits=dp.get_precision("Product Unit of Measure"))
	merchant_order_id = fields.Char(string="merchant-order-id")
	promotion_id = fields.Char(string="promotion-id")
	marketplace_name = fields.Char(string="marketplace-name")
	shipment_id = fields.Char(string="shipment-id")
	adjustment_id = fields.Char(string="adjustment-id")
	fulfillment_id = fields.Char(string="fulfillment-id")
	order_item_code = fields.Char(string="order-item-code")
	merchant_order_item_id = fields.Char(string="merchant-order-item-id")
	merchant_adjustment_item_id = fields.Char(string="merchant-adjustment-item-id")
