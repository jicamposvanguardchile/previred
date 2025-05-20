
from odoo import models, api, fields

class Indicadores(models.Model):
    _name = "hr.indicadores"
    asignacion_familiar_ids =fields.One2many("hr.asignacion.familiar", "indicador_id")
    seguro_cesantia_ids =fields.One2many("hr.seguro.cesantia", "seguro_id")
    cotizacion_afp_ids = fields.One2many("hr.cotizacion.obligatoria.afp", "indicador_afp_id")
    trabajos_ids = fields.One2many("hr.cotizacion_trabajos_pesados", "trabajos_id")
    mes = fields.Integer(string="mes en curso", required=True)
    uf_abril = fields.Float(string="Valor UF Abril")
    uf_marzo = fields.Float(string="Valor UF Marzo")
    utm_abril = fields.Float(string="Valor UTM Abril")
    uta_abril = fields.Float(string="Valor UTA Abril")
    af_afp = fields.Float(string="Valor Venta Tope Afiliado a AFP")
    af_ips = fields.Float(string="Valor Venta Tope Afiliado a IPS")
    seg_cesantia = fields.Float(string="Valor Venta Tope Seguro Cesantia")
    t_dep_indep = fields.Float(string="Valor Renta Minima Dependientes e Independiente")
    men_18_may_65 = fields.Float(string="Valor Renta Minima Menores 18 y Mayores 65 años")
    t_casa = fields.Float(string="Valor Renta Minima Trabajadores de Casa Particular")
    no_remun = fields.Float(string="Valor Renta Minima No Remuneracionales")
    a_tope_mens = fields.Float(string="Ahorro Prev Volun, Tope Mensual(50UF)")
    a_tope_anual = fields.Float(string="Ahorro Prev Volun, Tope Anual(600UF)")
    d_tope_anual = fields.Float(string="Deposito Convenido, Tope Anual(900UF)")
    ccaf =fields.Float(string="Distribucion de salud para afiliados a CCAF")
    fonasa =fields.Float(string="Distribucion de salud para afiliados a FONASA")


class HrAsignacionFamiliar(models.Model):
    _name = 'hr.asignacion.familiar'
    _description = 'Tramo y monto asignación familiar por renta'

    indicador_id = fields.Many2one("hr.indicadores", string='mes')
    renta_ingresada = fields.Float(string="Renta Ingresada")
    tramo = fields.Char(string="Tramo")
    monto = fields.Float(string="Monto")

class SeguroCesantia(models.Model):
    _name ='hr.seguro.cesantia'
    _description = 'Financiamiento Segun Tipo Contrato'
    seguro_id = fields.Many2one("hr.indicadores", string='mes')
    contrato = fields.Char(string="Tipo de Contrato")
    empleador = fields.Float(string="Financiamiento Segun Empleador")
    trabajador = fields.Float(string="Financiamiento Segun Trabajador")

class CotizacionObligatoriaAFP(models.Model):
    _name = 'hr.cotizacion.obligatoria.afp'
    _description = 'Cotizacion para trabajadores dep y indep segun AFP'
    indicador_afp_id = fields.Many2one("hr.indicadores", string='mes')
    tipo_afp = fields.Char(string="Tipo AFP")
    tasa_afp = fields.Float(string="Tasa AFP Para Trabajadores Dep")
    sis = fields.Float(string="Tasa SIS Para Trabajadores Dep")
    tasa_afp3 = fields.Float(string="Tasa AFP Para Trabajadores Indep")

class CotizacionTrabajosPesados(models.Model):
    _name = 'hr.cotizacion_trabajos_pesados'
    _description = 'Financiamiento Para Empleador y Trabajador Segun Trabajo'
    trabajos_id = fields.Many2one("hr.indicadores", string='mes')
    puesto_trabajo = fields.Char(string="Calificacion Segun Puesto de Trabajo")
    financ_empleador = fields.Char(string="Financiamiento de Empleador Segun Trabajo")
    financ_trabajador = fields.Char(string="Financiamiento de Trabajador Segun Trabajo")

