# -*- encoding: utf-8 -*-

from openerp import models, fields, api, _
from openerp.exceptions import UserError, ValidationError
import time

class AsistenteReporteDiario(models.TransientModel):
    _name = 'l10n_gt_extra.asistente_reporte_diario'

    def _default_cuenta(self):
        if len(self.env.context.get('active_ids', [])) > 0:
            return self.env.context.get('active_ids')
        else:
            return self.env['account.account'].search([]).ids

    cuentas_id = fields.Many2many("account.account", string="Diario", required=True, default=_default_cuenta)
    folio_inicial = fields.Integer(string="Folio Inicial", required=True, default=1)
    fecha_desde = fields.Date(string="Fecha Inicial", required=True, default=lambda self: time.strftime('%Y-%m-01'))
    fecha_hasta = fields.Date(string="Fecha Final", required=True, default=lambda self: time.strftime('%Y-%m-%d'))

    @api.multi
    def print_report(self):
        data = {
             'ids': [],
             'model': 'l10n_gt_extra.asistente_reporte_diario',
             'form': self.read()[0]
        }
        return self.env.ref('l10n_gt_extra.action_reporte_diario').report_action(self, data=data)