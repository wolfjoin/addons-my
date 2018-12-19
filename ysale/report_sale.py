# -*- coding: utf-8 -*-

from openerp import models, fields, api
from openerp.tools.sql import drop_view_if_exists


class ReportYsale(models.Model):
	_name = 'report.ysale.order'
	_description = 'Report Ysale Order'
	_auto = False

	name = fields.Char(string='订单号', readonly=True)
	order_amount = fields.Float(string='总计金额', readonly=True)
	pay_amount = fields.Float(string="付款金额",readonly=True)

	def init(self,cr):
		drop_view_if_exists(cr, 'report_ysale_order')
		cr.execute("""
					create or replace view report_yo as (
					select
						s.id as id,
						s.name as name,
						sum(sl.subtotal) as order_amount
					from
					ysale_order s
						left join ysale_order_line sl on (s.id=sl.order_id)
					group by s.id
					);	
						



					create or replace view report_yp as (
					SELECT s.id,
					s.name,
					sum(sp.money) AS pay_amount
					FROM ysale_order s
					 LEFT JOIN ysale_pay sp ON s.id = sp.order_id
					GROUP BY s.id
					);	


					create or replace view report_ysale_order as (
					SELECT o.id,
					o.name,
					o.order_amount,
					p.pay_amount
					FROM report_yo o
					 LEFT JOIN report_yp p ON o.id = p.id
					)
			""")

