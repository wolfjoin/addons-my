# -*- coding: utf-8 -*-
###############################################################################
#    License, author and contributors information in:                         #
#    __openerp__.py file at the root folder of this module.                   #
###############################################################################

from openerp import models, fields
from openerp.tools.translate import _
import logging
_logger = logging.getLogger(__name__)


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    project_id = fields.Many2one(
        string=_('Analytic Account'),
        required=False,
        readonly=False,
        index=False,
        default=None,
        help=_('Project id'),
        comodel_name='account.analytic.account',
        domain=lambda self: [('type', 'in', ['normal', 'contract'])],
        context={},
        ondelete='cascade',
        auto_join=False,
    )
