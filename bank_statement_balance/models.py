# -*- coding: utf-8 -*-
import openerp.addons.decimal_precision as dp
from openerp import models, fields, api, tools

class BankStatementBalance(models.Model):
    _inherit ='account.bank.statement.line'
    _order = "trade_datetime,sequence"

    @api.one
    # @api.depends('amount', 'journal_id')
    # 改为onchange实时显示余额
    @api.onchange('amount', 'journal_id')
    def _compute_balance(self):
        # 相邻的两条记录，bank_id不同，重新计算账户余额
        # 按照分录journal_id，绑定的是唯一银行卡，但是保存后，明细才会生成journal_id信息
        # todo: 如何设置银行明细能实时拥有journal_id，尝试onchange
        pre_record = self.search(
            [('trade_datetime', '<=', self.trade_datetime), ('journal_id', '=', self.journal_id.id)])
        for pre in pre_record:
            self.balance += pre.amount

    @api.one
    # Expected singleton: account.bank.statement.line(19, 12)
    # 报错提示非单个集，使用@api.one解决问题
    @api.onchange('balance', 'real_bank_balance')
    def _compute_balance_calc_real(self):
        # 计算理论余额与实际银行提供余额的差额
        # 可以设置若实际余额没有写，忽略不计算
        # 计算账户余额再保存前为0，在保存后才会计算

        for record in self:
            if self.real_bank_balance != 0 :
                # or (self.real_bank_balance == 0 and self.balance != 0):
                # 不可能每个明细都会有实际余额，若不填写，默认为0，就不计算差额
                # 只计算填写了实际余额的。若实际余额本身就为0，
                # TypeError: unsupported operand type(s) for &: 'int' and 'float'
                # 因为用了& 提示如上错误，修改为and解决问题
                self.balance_calc_real = self.real_bank_balance - self.balance

    @api.one
    @api.onchange('trade_datetime')
    def _compute_date(self):
        if  self.trade_datetime:
            self.date = self.trade_datetime


    balance = fields.Float(string=u'理论余额',
                           compute='_compute_balance', readonly=True,
                           digits=dp.get_precision('Amount'))
    real_bank_balance = fields.Float(string=u'实际余额', 
                           digits=dp.get_precision('Amount'))

    balance_calc_real = fields.Float(string=u'差额',
                           compute='_compute_balance_calc_real', readonly=True,
                           digits=dp.get_precision('Amount'))

    # balance = fields.Float(string=u'账户余额',readonly=True,
    #                        digits=dp.get_precision('Amount'))
    trade_datetime = fields.Datetime(string=u'交易日期')
    # 时间类型首字母大写，严格区分大小写

    # journal_id = fields.Many2one('account.bank.statement', default=lambda self: self.statement_id.journal_id)
    # 如果自动获取明细行分录为父表单的默认值，不是保存后

    date = fields.Date(string='Date', default=_compute_date)



