# -*- coding: utf-8 -*-

import openerp.addons.decimal_precision as dp
from openerp import fields, models, api
from openerp.tools.sql import drop_view_if_exists

class BankStatementsReport(models.Model):
    _name = "bank.statements.report"
    _description = "Bank Report"
    _auto = False
    _order = 'date'

    @api.one
    @api.depends('get', 'pay', 'journal_id')
    def _compute_balance(self):
        # 相邻的两条记录，bank_id不同，重新计算账户余额1
        pre_record = self.search(
            [('id', '<=', self.id), ('journal_id', '=', self.journal_id.id)])
        for pre in pre_record:
            self.balance += pre.get - pre.pay


    journal_id = fields.Many2one('account.journal', string=u'账户', readonly=True)
    date = fields.Date(string=u'日期', readonly=True)
    
    date = fields.Date(string=u'日期', readonly=True)
    name = fields.Char(string=u'单据编号', readonly=True)
    get = fields.Float(string=u'收入', readonly=True,
                       digits=dp.get_precision('Amount'))
    pay = fields.Float(string=u'支出', readonly=True,
                       digits=dp.get_precision('Amount'))
    balance = fields.Float(string=u'账户余额',
                           compute='_compute_balance', readonly=True,
                           digits=dp.get_precision('Amount'))
    partner_id = fields.Many2one('res.partner', string=u'往来单位', readonly=True)
    note = fields.Char(string=u'备注', readonly=True)

    def init(self, cr):
        # union money_order, other_money_order, money_transfer_order
        # cr = self._cr
        # tools.drop_view_if_exists(cr, 'bank_statements_report')
        drop_view_if_exists(cr, 'bank_statements_report')
        cr.execute("""
            create or replace view bank_statements_report as (
                select
                ROW_NUMBER() OVER(ORDER BY journal_id,date) AS id,
                absl.date as date,
                absl.name as name,
                absl.journal_id as journal_id,
                (CASE WHEN absl.amount >= 0 THEN absl.amount ELSE 0 END) AS get,
                (CASE WHEN absl.amount < 0 THEN -absl.amount ELSE 0 END) AS pay,
                0 as balance,
                absl.partner_id as partner_id,
                absl.note as note

            from
                account_bank_statement_line as absl
            )""")



