# -*- coding: utf-8 -*-
###############################################################################
#    License, author and contributors information in:                         #
#    __openerp__.py file at the root folder of this module.                   #
###############################################################################

from openerp import models, fields
from datetime import date
import logging
_logger = logging.getLogger(__name__)


class StockQuant(models.Model):
    _inherit = 'stock.quant'

    def _create_account_move_line(
       self, cr, uid, quants, move, credit_account_id, debit_account_id,
       journal_id, context=None):
        quant_cost_qty = {}
        for quant in quants:
            if quant_cost_qty.get(quant.cost):
                quant_cost_qty[quant.cost] += quant.qty
            else:
                quant_cost_qty[quant.cost] = quant.qty
        move_obj = self.pool.get('account.move')
        for cost, qty in quant_cost_qty.items():
            move_lines = self._prepare_account_move_line(
                cr, uid, move, qty, cost, credit_account_id, debit_account_id,
                context=context)
            period_id = context.get(
                'force_period', self.pool.get('account.period')
                .find(cr, uid, context=context)[0])
            move_obj.create(cr, uid, {
                'journal_id': journal_id,
                'line_id': move_lines,
                'period_id': period_id,
                'date': date.today(),
                'ref': move.picking_id.name,
                'picking': move.picking_id.id,
            }, context=context)

    def _prepare_account_move_line(
       self, cr, uid, move, qty, cost, credit_account_id, debit_account_id,
       context=None):
        """
        Generate the account.move.line values to post to track the stock
        valuation difference due to the processing of the given quant.
        """
        if context is None:
            context = {}
        currency_obj = self.pool.get('res.currency')
        if context.get('force_valuation_amount'):
            valuation_amount = context.get('force_valuation_amount')
        else:
            if move.product_id.cost_method == 'average':
                valuation_amount = cost \
                    if move.location_id.usage != 'internal' and \
                    move.location_dest_id.usage == 'internal' \
                    else move.product_id.standard_price
            else:
                valuation_amount = cost \
                    if move.product_id.cost_method == 'real' \
                    else move.product_id.standard_price
        valuation_amount = currency_obj.round(
            cr, uid, move.company_id.currency_id, valuation_amount * qty)
        partner_id = (
            move.picking_id.partner_id and self.pool.get('res.partner').
            _find_accounting_partner(move.picking_id.partner_id).id) or False
        debit_line_vals = {
                    'name': move.name,
                    'product_id': move.product_id.id,
                    'quantity': qty,
                    'product_uom_id': move.product_id.uom_id.id,
                    'ref': move.picking_id and move.picking_id.name or False,
                    'date': move.date,
                    'partner_id': partner_id,
                    'debit': valuation_amount > 0 and valuation_amount or 0,
                    'credit': valuation_amount < 0 and -valuation_amount or 0,
                    'account_id': debit_account_id,
                    'analytic_account_id': move.picking_id.project_id.id,
        }
        credit_line_vals = {
                    'name': move.name,
                    'product_id': move.product_id.id,
                    'quantity': qty,
                    'product_uom_id': move.product_id.uom_id.id,
                    'ref': move.picking_id and move.picking_id.name or False,
                    'date': move.date,
                    'partner_id': partner_id,
                    'credit': valuation_amount > 0 and valuation_amount or 0,
                    'debit': valuation_amount < 0 and -valuation_amount or 0,
                    'account_id': credit_account_id,
        }
        return [(0, 0, debit_line_vals), (0, 0, credit_line_vals)]
