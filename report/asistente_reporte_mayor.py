# -*- encoding: utf-8 -*-

from openerp import models, fields, api, _
from openerp.exceptions import UserError, ValidationError
import time
import xlwt
import base64
import io
import logging

class AsistenteReporteMayor(models.TransientModel):
    _name = 'l10n_gt_extra.asistente_reporte_mayor'

    def _default_cuenta(self):
        if len(self.env.context.get('active_ids', [])) > 0:
            return self.env.context.get('active_ids')
        else:
            return self.env['account.account'].search([]).ids

    cuentas_id = fields.Many2many("account.account", string="Cuenta", required=True, default=_default_cuenta)
    folio_inicial = fields.Integer(string="Folio Inicial", required=True, default=1)
    agrupado_por_dia = fields.Boolean(string="Agrupado por dia")
    fecha_desde = fields.Date(string="Fecha Inicial", required=True, default=lambda self: time.strftime('%Y-%m-01'))
    fecha_hasta = fields.Date(string="Fecha Final", required=True, default=lambda self: time.strftime('%Y-%m-%d'))
    name = fields.Char('Nombre archivo', size=32)
    archivo = fields.Binary('Archivo', filters='.xls')

    def print_report(self):
        active_ids = self.env.context.get('active_ids', [])
        data = {
             'ids': active_ids,
             'model': self.env.context.get('active_model', 'ir.ui.menu'),
             'form': self.read()[0]
        }
        return self.env['report'].get_action([], 'l10n_gt_extra.reporte_mayor', data=data)

    def print_report_excel(self):
        for w in self:
            dict = {}
            dict['fecha_hasta'] = w['fecha_hasta']
            dict['fecha_desde'] = w['fecha_desde']
            dict['agrupado_por_dia'] = w['agrupado_por_dia']
            dict['cuentas_id'] =[x.id for x in w.cuentas_id]
            res = self.env['report.l10n_gt_extra.reporte_mayor'].lineas(dict)

            libro = xlwt.Workbook()
            hoja = libro.add_sheet('reporte')

            xlwt.add_palette_colour("custom_colour", 0x21)
            libro.set_colour_RGB(0x21, 200, 200, 200)
            estilo = xlwt.easyxf('pattern: pattern solid, fore_colour custom_colour')
            hoja.write(0, 0, 'LIBRO MAYOR')
            hoja.write(2, 0, 'NUMERO DE IDENTIFICACION TRIBUTARIA')
            hoja.write(2, 1, w.cuentas_id[0].company_id.partner_id.vat)
            hoja.write(3, 0, 'NOMBRE COMERCIAL')
            hoja.write(3, 1, w.cuentas_id[0].company_id.partner_id.name)
            hoja.write(2, 3, 'DOMICILIO FISCAL')
            hoja.write(2, 4, w.cuentas_id[0].company_id.partner_id.street)
            hoja.write(3, 3, 'REGISTRO DEL')
            hoja.write(3, 4, w.fecha_desde + ' al ' + w.fecha_hasta)

            y = 5
            if w['agrupado_por_dia']:
                lineas = res['lineas']

                hoja.write(y, 0, 'Codigo')
                hoja.write(y, 1, 'Cuenta')
                hoja.write(y, 2, 'fecha')
                hoja.write(y, 3, 'Saldo Inicial')
                hoja.write(y, 4, 'Debe')
                hoja.write(y, 5, 'Haber')
                hoja.write(y, 6, 'Saldo FInal')

                for cuenta in lineas:
                    y += 1
                    hoja.write(y, 0, cuenta['codigo'])
                    hoja.write(y, 1, cuenta['cuenta'])
                    hoja.write(y, 3, cuenta['saldo_inicial'])
                    hoja.write(y, 4, cuenta['total_debe'])
                    hoja.write(y, 5, cuenta['total_haber'])
                    hoja.write(y, 6, cuenta['saldo_final'])
                    for fechas in cuenta['fechas']:
                        y += 1
                        hoja.write(y, 2, fechas['fecha'])
                        hoja.write(y, 4, fechas['debe'])
                        hoja.write(y, 5, fechas['haber'])
                    y += 1
            else:
                lineas = res['lineas']
                totales = res['totales']

                hoja.write(y, 0, 'Codigo')
                hoja.write(y, 1, 'Cuenta')
                hoja.write(y, 2, 'Debe')
                hoja.write(y, 3, 'Haber')

                for linea in lineas:
                    y += 1

                    hoja.write(y, 0, linea['codigo'])
                    hoja.write(y, 1, linea['cuenta'])
                    hoja.write(y, 2, linea['debe'])
                    hoja.write(y, 3, linea['haber'])

                y += 1
                hoja.write(y, 1, 'Totales')
                hoja.write(y, 2, totales['debe'])
                hoja.write(y, 3, totales['haber'])

            xlwt.add_palette_colour("custom_colour", 0x21)
            libro.set_colour_RGB(0x21, 200, 200, 200)
            estilo = xlwt.easyxf('pattern: pattern solid, fore_colour custom_colour')

            f = io.BytesIO()
            libro.save(f)
            datos = base64.b64encode(f.getvalue())
            self.write({'archivo':datos, 'name':'libro_mayor.xls'})

        return {
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'l10n_gt_extra.asistente_reporte_mayor',
            'res_id': self.id,
            'view_id': False,
            'type': 'ir.actions.act_window',
            'target': 'new',
        }
