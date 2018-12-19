# -*- coding: utf-8 -*-
################################################################
#    License, author and contributors information in:          #
#    __openerp__.py file at the root folder of this module.    #
################################################################

from openerp import models, fields
from openerp.tools.translate import _
import logging
_logger = logging.getLogger(__name__)


class AccountMove(models.Model):
    _inherit = 'account.move'

    picking = fields.Many2one(
        string=_('Picking'),
        required=False,
        readonly=False,
        index=False,
        default=None,
        help=_('Picking number'),
        comodel_name='stock.picking',
        domain=[],
        context={},
        ondelete='cascade',
        auto_join=False,
    )
