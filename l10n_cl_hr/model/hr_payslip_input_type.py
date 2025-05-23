# -*- coding:utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models

import logging
_logger = logging.getLogger(__name__)


class CLHrPayslipInputType(models.Model):
    _name = 'l10n_cl_hr.payslip.input.type'
    _description = 'Tipo de input de nómina Chile (modificado)'

    name = fields.Char(required=True)
    code = fields.Char()
    show_input = fields.Boolean('Agrega input en Nómina', default=False)
    invisible_show_input = fields.Boolean(compute='_compute_invisible_show_input')

    def _compute_invisible_show_input(self):
        for input_type in self:
            input_type.invisible_show_input = not input_type.show_input
