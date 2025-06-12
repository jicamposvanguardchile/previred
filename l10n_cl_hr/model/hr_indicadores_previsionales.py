#
# v.1.1 20220717 Cambio en metodologia web scraping. Vanguard.
#
from odoo import api, fields, models, tools, _
from urllib.request import urlopen
from bs4 import BeautifulSoup
from datetime import datetime
import logging
import requests
import re
import unicodedata

import locale

locale._override_localeconv["thousands_sep"] = "."
locale._override_localeconv["decimal_point"] = ","


URL_PREVIRED = "https://www.previred.com/indicadores-previsionales/"
URL_BCENTRAL = "https://si3.bcentral.cl/indicadoressiete/secure/Serie.aspx?gcode=IPC&param=UQBSAEYAYwAxAFIARABYADAALQBqAHAAWABKAHEAcQBzAHAAQgB4ADcATwBHAGIAMgBfAEwATgBOAHIAWQA1ACMAZwBsAC4AeABtAEwATQBsAHcAdQBvAGQARwBQAGUARQBvAG0ASwB4AEQAbABTAGgARgAxAGUAQgBxAHkAcwA5AG8ARQAzAGgAMQBPAFQARgBSAEwASABZAE0ARgBKAFoAMwBmAHYATgBoAGMANQBpAE8ANwBFAGMAJAA="

_logger = logging.getLogger(__name__)

MONTH_LIST= [('1', 'Enero'), 
        ('2', 'Febrero'), ('3', 'Marzo'), 
        ('4', 'Abril'), ('5', 'Mayo'), 
        ('6', 'Junio'), ('7', 'Julio'), 
        ('8', 'Agosto'), ('9', 'Septiembre'), 
        ('10', 'Octubre'), ('11', 'Noviembre'),
        ('12', 'Diciembre')]

STATES = {'draft': [('readonly', False)]}

class hr_indicadores_previsionales(models.Model):
    _name = 'hr.indicadores'
    _description = 'Indicadores Previsionales'

    name = fields.Char('Nombre')
    state = fields.Selection([
        ('draft','Borrador'),
        ('done','Validado'),
        ], string=u'Estado', readonly=True, default='draft')
    asignacion_familiar_primer = fields.Float('Asignación Familiar Tramo 1',
        help="Asig Familiar Primer Tramo")
    asignacion_familiar_segundo = fields.Float('Asignación Familiar Tramo 2', 
        help="Asig Familiar Segundo Tramo")
    asignacion_familiar_tercer = fields.Float('Asignación Familiar Tramo 3', 
        help="Asig Familiar Tercer Tramo")
    asignacion_familiar_cuarto = fields.Float('Asignación Familiar Tramo 4', 
        help="Asig Familiar Cuarto Tramo")
    asignacion_familiar_monto_a = fields.Float( 'Monto Tramo Uno',  help="Monto A")
    asignacion_familiar_monto_b = fields.Float( 'Monto Tramo Dos',  help="Monto B")
    asignacion_familiar_monto_c = fields.Float( 'Monto Tramo Tres',  help="Monto C")
    asignacion_familiar_monto_d = fields.Float( 'Monto Tramo Cuatro',  help="Monto D")
    contrato_plazo_fijo_empleador = fields.Float( 'Contrato Plazo Fijo Empleador', 
        help="Contrato Plazo Fijo Empleador")
    contrato_plazo_fijo_trabajador = fields.Float( 'Contrato Plazo Fijo Trabajador',
        help="Contrato Plazo Fijo Trabajador")    
    contrato_plazo_indefinido_empleador = fields.Float( 'Contrato Plazo Indefinido Empleador', 
        help="Contrato Plazo Fijo")
    contrato_plazo_indefinido_empleador_otro = fields.Float( 'Contrato Plazo Indefinido Empleador 11 anos o mas', 
        help="Contrato Plazo Indefinido 11 anos Empleador")
    contrato_plazo_indefinido_trabajador_otro = fields.Float( 'Contrato Plazo Indefinido Trabajador 11 anos o mas', 
        help="Contrato Plazo Indefinido 11 anos Trabajador")
    contrato_plazo_indefinido_trabajador = fields.Float( 'Contrato Plazo Indefinido Trabajador', 
        help="Contrato Plazo Indefinido Trabajador")
    contrato_particular_trabajador = fields.Float( 'Contrato Casa Particular Trabajador',
        help="Contrato Casa Particular Trabajador")
    caja_compensacion  = fields.Float( 'Caja Compensación', help="Caja de Compensacion")
    deposito_convenido = fields.Float( 'Deposito Convenido', help="Deposito Convenido")
    fonasa = fields.Float('Fonasa', help="Fonasa")
    mutual_seguridad = fields.Float( 'Mutualidad', help="Mutual de Seguridad")
    isl = fields.Float( 'ISL', help="Instituto de Seguridad Laboral")
    pensiones_ips = fields.Float( 'Pensiones IPS',  help="Pensiones IPS")
    sueldo_minimo_dep_indep = fields.Float( 'Trab. Dependientes e Independientes',  help="Sueldo Minimo")
    sueldo_minimo_men_18_may_65 = fields.Float( 'Menores de 18 y Mayores de 65:', 
        help="Sueldo Mínimo para Menores de 18 y Mayores a 65")
    sueldo_minimo_casa_particular = fields.Float('Trabajadores de Casa Particular',  
        help="Sueldo Minimo para Trabajadores de Casa Particular")
    sueldo_minimo_no_remun = fields.Float('Para fines no remuneracional',  
        help="Sueldo Minimo para Fines no Remuneracionales")
    tasa_afp_cuprum  = fields.Float( 'Cuprum', help="Tasa AFP Cuprum")
    tasa_afp_capital = fields.Float( 'Capital', help="Tasa AFP Capital")
    tasa_afp_provida = fields.Float( 'ProVida', help="Tasa AFP Provida")
    tasa_afp_modelo  = fields.Float( 'Modelo', help="Tasa AFP Modelo")
    tasa_afp_planvital = fields.Float( 'PlanVital', help="Tasa AFP PlanVital")
    tasa_afp_habitat = fields.Float( 'Habitat',  help="Tasa AFP Habitat")
    tasa_afp_uno = fields.Float( 'Uno', help="Tasa AFP Uno")
    tasa_sis_cuprum  = fields.Float('SIS', help="Tasa SIS Cuprum")
    tasa_sis_capital = fields.Float( 'SIS', help="Tasa SIS Capital")
    tasa_sis_provida = fields.Float( 'SIS', help="Tasa SIS Provida")
    tasa_sis_planvital = fields.Float( 'SIS', help="Tasa SIS PlanVital")
    tasa_sis_habitat = fields.Float( 'SIS', help="Tasa SIS Habitat")
    tasa_sis_modelo  = fields.Float( 'SIS',  help="Tasa SIS Modelo")
    tasa_sis_uno = fields.Float( 'SIS', help="Tasa SIS Uno")
    tasa_independiente_cuprum = fields.Float( 'SIS',  help="Tasa Independientes Cuprum")
    tasa_independiente_capital = fields.Float( 'SIS',  help="Tasa Independientes Capital")
    tasa_independiente_provida = fields.Float( 'SIS',  help="Tasa Independientes Provida")
    tasa_independiente_planvital = fields.Float( 'SIS',  help="Tasa Independientes PlanVital")
    tasa_independiente_habitat = fields.Float( 'SIS',  help="Tasa Independientes Habitat")
    tasa_independiente_modelo = fields.Float( 'SIS',  help="Tasa Independientes Modelo")
    tasa_independiente_uno = fields.Float( 'SIS', help="Tasa Independientes Uno")
    tope_anual_apv = fields.Float( 'Tope Anual APV',  help="Tope Anual APV")
    tope_mensual_apv = fields.Float( 'Tope Mensual APV',  help="Tope Mensual APV")
    tope_imponible_afp = fields.Float( 'Tope imponible AFP',  help="Tope Imponible AFP")
    tope_imponible_ips = fields.Float( 'Tope imponible IPS',  help="Tope Imponible IPS")
    tope_imponible_salud = fields.Float( 'Tope Imponible Salud', )
    tope_imponible_seguro_cesantia = fields.Float( 'Tope Imponible Seguro Cesantía', 
        help="Tope Imponible Seguro de Cesantía")
    trabajo_pesado = fields.Float( 'Cotizacion Trabajo Pesado',  help="Cotizacion Trabajo Pesado")
    trabajo_pesado_empleador = fields.Float( 'Calificacion Trabajo Pesado Empleador',  
        help="Cotizacion Trabajo Pesado Empleador")
    trabajo_pesado_trabajador = fields.Float( 'Trabajo Pesado Trabajador',  
        help="Cotizacion Trabajo Pesado Trabajador")
    trabajo_menos_pesado = fields.Float( 'Cotizacion Trabajo Menos Pesado',  
        help="Cotizacion Trabajo Menos Pesado")
    trabajo_menos_pesado_empleador = fields.Float( 'Trabajo Menos Pesado Empleador',  
        help="Calificacion Trabajo Menos Empleador")
    trabajo_menos_pesado_trabajador = fields.Float( 'Trabajo Menos Pesado Trabajador',  
        help="Cotizacion Trabajo Menos Pesado Trabajador")
    uf  = fields.Float('UF', help="UF fin de Mes")
    utm = fields.Float('UTM',   help="UTM Fin de Mes")
    uta = fields.Float('UTA',  help="UTA Fin de Mes")
    uf_otros = fields.Float( 'UF Otros',  help="UF Seguro Complementario")
    mutualidad_id = fields.Many2one('hr.mutual', 'MUTUAL')
    ccaf_id = fields.Many2one('hr.ccaf', 'CCAF' )
    month = fields.Selection(MONTH_LIST, string='Mes' )
    year = fields.Integer('Año',  default=datetime.now().strftime('%Y'))
    gratificacion_legal = fields.Boolean('Gratificación L. Manual')
    mutual_seguridad_bool = fields.Boolean('Mutual Seguridad', default=True)
    ipc = fields.Float('IPC',    help="Indice de Precios al Consumidor (IPC)")
    
    def action_done(self):
        self.write({'state': 'done'})
        return True
    
    def action_draft(self):
        self.write({'state': 'draft'})
        return True

    @api.onchange('month')
    def get_name(self):
        self.name = str(self.month).replace('10', 'Octubre').replace('11', 'Noviembre').replace('12', 'Diciembre').replace('1', 'Enero').replace('2', 'Febrero').replace('3', 'Marzo').replace('4', 'Abril').replace('5', 'Mayo').replace('6', 'Junio').replace('7', 'Julio').replace('8', 'Agosto').replace('9', 'Septiembre') + " " + str(self.year)

    def find_between_r(self, s, first, last ):
        try:
            start = s.rindex( first ) + len( first )
            end = s.rindex( last, start )
            return s[start:end]
        except ValueError:
            return ""

    def find_month(self, s):
        if s == '1':
            return 'Enero'
        if s == '2':
            return 'Febrero'
        if s == '3':
            return 'Marzo'
        if s == '4':
            return 'Abril'
        if s == '5':
            return 'Mayo'
        if s == '6':
            return 'Junio'
        if s == '7':
            return 'Julio'
        if s == '8':
            return 'Agosto'
        if s == '9':
            return 'Septiembre'
        if s == '10':
            return 'Octubre'
        if s == '11':
            return 'Noviembre'
        if s == '12':
            return 'Diciembre'


    def update_document(self):
        #self.update_date = datetime.today()
        #try:
        
        #    url = 'https://www.previred.com/indicadores-previsionales/'
         #   _logger.info('url %s'%(url))
          #  page = urlopen(url)
           # html_bytes = page.read()
            #html = html_bytes.decode("utf-8")
            #brute = re.findall("\$ [\d\.,]+<|>[\d]+\.[\d\.]+<|>[\d,]+%<|>[\d,]+% R\.I\. ?<", html)
            #_logger.info('brute %s'%(brute))
            #pure = []
            #for item in brute:
            #    pure.append(float((re.search("[\d\.,]+", item)[0]).replace('.','').replace(',','.')))
        #except ValueError:
        #    return ""

        #try:
        new_ind = self._hrIndPrevired()
        _logger.info('new_ind %s'%(new_ind))
        
            # UF
        self.uf = new_ind['UF']

            # 1 UTM
        self.utm = new_ind['UTM']

            # 1 UTA
        self.uta = new_ind['UTA']

            # 3 RENTAS TOPES IMPONIBLES (UF)
        self.tope_imponible_afp             = new_ind['RENTAS_TOPE_AFP']
        self.tope_imponible_ips             = new_ind['RENTAS_TOPE_IPS'] 
        self.tope_imponible_seguro_cesantia = new_ind['RENTAS_TOPE_SEGURO'] 

            # 4 RENTAS MINIMAS IMPONIBLES
        self.sueldo_minimo_dep_indep        = new_ind['RENTAS_MINIMA_DEP_INDEP']
        self.sueldo_minimo_men_18_may_65    = new_ind['RENTAS_MINIMA_18_Y_65']
        self.sueldo_minimo_casa_particular  = new_ind['RENTAS_MINIMA_CASA_PARTICULAR']
        self.sueldo_minimo_no_remun         = new_ind['RENTAS_MINIMA_NO_REMU']

            # Ahorro Previsional Voluntario (UF)
        self.tope_mensual_apv = new_ind['APV_TOPE_MENSUAL']
        self.tope_anual_apv   = new_ind['APV_TOPE_ANUAL']

            # 5 DEPÓSITO CONVENIDO (UF)
        self.deposito_convenido = new_ind['DEPOSITO_CONVENIDO_TOPE_ANUAL']

            # 6 SEGURO DE CESANTÍA (AFC)
        self.contrato_plazo_indefinido_empleador      = new_ind['SEGURO_CESANTIA_PLAZO_INDEF'][0]
        self.contrato_plazo_indefinido_trabajador     = new_ind['SEGURO_CESANTIA_PLAZO_INDEF'][1]
        self.contrato_plazo_fijo_empleador            = new_ind['SEGURO_CESANTIA_PLAZO_FIJO']
        self.contrato_plazo_indefinido_empleador_otro = new_ind['SEGURO_CESANTIA_11_ANNOS'][0]
        self.contrato_particular_trabajador           = new_ind['SEGURO_CESANTIA_CASA_PARTICULAR'][0]

            # 7 ASIGNACIÓN FAMILIAR
        self.asignacion_familiar_monto_a = new_ind['ASIGNACION_FAMILIAR_A'][0]
        self.asignacion_familiar_monto_b = new_ind['ASIGNACION_FAMILIAR_B'][0]
        self.asignacion_familiar_monto_c = new_ind['ASIGNACION_FAMILIAR_C'][0]
        self.asignacion_familiar_monto_d = new_ind['ASIGNACION_FAMILIAR_D'][0]


        self.asignacion_familiar_primer  = new_ind['ASIGNACION_FAMILIAR_A'][1]
        self.asignacion_familiar_segundo = new_ind['ASIGNACION_FAMILIAR_B'][1]
        self.asignacion_familiar_tercer  = new_ind['ASIGNACION_FAMILIAR_C'][1]
        self.asignacion_familiar_cuarto  = new_ind['ASIGNACION_FAMILIAR_D'][1]

        # 8 TASA COTIZACIÓN OBLIGATORIO AFP
        self.tasa_afp_capital           = new_ind['TASA_CAPITAL'][0]
        self.tasa_sis_capital           = new_ind['TASA_CAPITAL'][1]
        self.tasa_independiente_capital = new_ind['TASA_CAPITAL'][2]

        self.tasa_afp_cuprum           = new_ind['TASA_CUPRUM'][0]
        self.tasa_sis_cuprum           = new_ind['TASA_CUPRUM'][1]
        self.tasa_independiente_cuprum = new_ind['TASA_CUPRUM'][2]

        self.tasa_afp_habitat           = new_ind['TASA_HABITAT'][0]
        self.tasa_sis_habitat           = new_ind['TASA_HABITAT'][1]
        self.tasa_independiente_habitat = new_ind['TASA_HABITAT'][2]

        self.tasa_afp_planvital           = new_ind['TASA_PLANVITAL'][0]
        self.tasa_sis_planvital           = new_ind['TASA_PLANVITAL'][1]
        self.tasa_independiente_planvital = new_ind['TASA_PLANVITAL'][2]

        self.tasa_afp_provida           = new_ind['TASA_PROVIDA'][0]
        self.tasa_sis_provida           = new_ind['TASA_PROVIDA'][1]
        self.tasa_independiente_provida = new_ind['TASA_PROVIDA'][2]

        self.tasa_afp_modelo           = new_ind['TASA_MODELO'][0]
        self.tasa_sis_modelo           = new_ind['TASA_MODELO'][1]
        self.tasa_independiente_modelo = new_ind['TASA_MODELO'][2]

        self.tasa_afp_uno           = new_ind['TASA_UNO'][0]
        self.tasa_sis_uno           = new_ind['TASA_UNO'][1]
        self.tasa_independiente_uno = new_ind['TASA_UNO'][2]

        # 9 COTIZACION TRABAJOS PESADOS
        self.trabajo_pesado         = new_ind['COTIZACION_TRAB_PESADO'][0]
        self.trabajo_menos_pesado   = new_ind['COTIZACION_TRAB_MENOS_PESADO'][0]

        self.trabajo_pesado_empleador = new_ind['COTIZACION_TRAB_PESADO'][1]
        self.trabajo_menos_pesado_empleador = new_ind['COTIZACION_TRAB_MENOS_PESADO'][1]

        self.trabajo_menos_pesado_trabajador = new_ind['COTIZACION_TRAB_MENOS_PESADO'][2]
        self.trabajo_pesado_trabajador = new_ind['COTIZACION_TRAB_PESADO'][2]

        # 10 IPC
        self.ipc                    = new_ind['IPC']

        #except Exception as e:
         #   _logger.error(f"Error actualizando indicadores previsionales: {e}")



    def _hrIndPrevired(self):
        page = requests.get(URL_PREVIRED)
        page_ipc = requests.get(URL_BCENTRAL)
        
        if page.status_code != 200 or page_ipc.status_code != 200:
            return None
        


        indicadores = {
            'UF':0,
            'UTM':0,
            'UTA':0.0,
            'MES_UTM':'',
            'RENTAS_TOPE_AFP':0,
            'RENTAS_TOPE_IPS':0,
            'RENTAS_TOPE_SEGURO':0,
            'RENTAS_MINIMA_DEP_INDEP':0,
            'RENTAS_MINIMA_18_Y_65':0,
            'RENTAS_MINIMA_CASA_PARTICULAR':0,
            'RENTAS_MINIMA_NO_REMU':0,
            'APV_TOPE_MENSUAL':0,
            'APV_TOPE_ANUAL':0,
            'DEPOSITO_CONVENIDO_TOPE_ANUAL':0,
            'SEGURO_CESANTIA_PLAZO_INDEF':0,
            'SEGURO_CESANTIA_PLAZO_FIJO':0,
            'SEGURO_CESANTIA_11_ANNOS':0,
            'SEGURO_CESANTIA_CASA_PARTICULAR':0,
            'DISTRIBUCION_7P_CCAF':0,
            'DISTRIBUCION_7P_FONASA':0,
            'TASA_CAPITAL':0,
            'TASA_CUPRUM':0,
            'TASA_HABITAT':0,
            'TASA_PLANVITAL':0,
            'TASA_PROVIDA':0,
            'TASA_MODELO':0,
            'TASA_UNO':0,
            'ASIGNACION_FAMILIAR_A':0,
            'ASIGNACION_FAMILIAR_B':0,
            'ASIGNACION_FAMILIAR_C':0,
            'ASIGNACION_FAMILIAR_D':0,
            'COTIZACION_TRAB_PESADO':0,
            'COTIZACION_TRAB_MENOS_PESADO':0,
            'IPC':0
        }


            
        def normalizar(texto):
            texto = unicodedata.normalize('NFKD', texto)
            return ''.join(c for c in texto if not unicodedata.combining(c)).lower()
        
        def extraer_monto(texto):
            extraccion = re.search(r'\$\s*(\d{1,3}(?:[\.\,]\d{3})*(?:[\.,]\d{2})?)', texto)
            if not extraccion:
                extraccion = re.search(r'(\d{1,3}(?:[\.\,]\d{3})*(?:[\.,]\d{2}))', texto)
            if not extraccion:
                extraccion = re.search(r'(\d+(?:[\.,]\d+)?)\s*%', texto)
            #_logger.info('extraccion %s'%(extraccion))
            #_logger.info('%s'%(float(extraccion.group(1).replace('.', '').replace(',', '.').replace('$', '').replace('%', ''))))
            if extraccion:
                return float(extraccion.group(1).replace('.', '').replace(',', '.').replace('$', '').replace('%', ''))
            return 0
        
        def extraer_porcentaje(texto):
            return ''
            match = re.search(r'(\d{1,2},\d{1,2})\s*%', texto)
            if match:
                return match.group(1).replace(',', '.') + '%'
            return texto.strip()

        soup = BeautifulSoup(page.content, "html.parser")

        #Extraccion previred

        tablas = soup.find_all('table')
        #_logger.info('tablas %s'%(tablas))
        for tabla in tablas:
            for fila in tabla.find_all('tr'):
                #_logger.info('fila %s' %(fila))
                texto_raw = fila.get_text(strip=True)
                texto = normalizar(texto_raw)

                 # UF
            #if ('uf abril' in texto or '30 de abril del' in texto):
             #   indicadores['UF']['ABRIL'] = extraer_monto(texto_raw)

                if ('uf mayo' in texto or 'al 31 de mayo del 2025' in texto):
                    indicadores['UF'] = extraer_monto(texto_raw)
                #_logger.info('texto_raw %s'%(texto_raw))
                #_logger.info('texto %s'%(texto))


                # UTM y UTA
                if 'mayo 2025' in texto:
                    celdas = fila.find_all('td')
                    if len(celdas) >= 3:
                        if indicadores['UTM'] == 0:
                            indicadores['UTM'] = extraer_monto(celdas[1].get_text(strip=True))
                            indicadores['MES_UTM'] = 'MAYO'
                        if indicadores['UTA'] == 0:
                            indicadores['UTA'] = extraer_monto(celdas[2].get_text(strip=True))

                # Topes
                if 'afiliados a una afp' in texto and indicadores['RENTAS_TOPE_AFP'] == 0:
                    indicadores['RENTAS_TOPE_AFP'] = extraer_monto(texto_raw)
                if 'para afiliados al ips (ex inp)' in texto and indicadores['RENTAS_TOPE_IPS'] == 0:
                    indicadores['RENTAS_TOPE_IPS'] = extraer_monto(texto_raw)
                if 'para seguro de cesantia' in texto and indicadores['RENTAS_TOPE_SEGURO'] == 0:
                    indicadores['RENTAS_TOPE_SEGURO'] = extraer_monto(texto_raw)

                # Rentas mínimas
                if 'trab. dependientes e independientes' in texto and indicadores['RENTAS_MINIMA_DEP_INDEP'] == 0:
                    indicadores['RENTAS_MINIMA_DEP_INDEP'] = extraer_monto(texto_raw)
                if 'menores de 18 y mayores de 65' in texto and indicadores['RENTAS_MINIMA_18_Y_65'] == 0: 
                    indicadores['RENTAS_MINIMA_18_Y_65'] = extraer_monto(texto_raw)
                if 'trabajadores de casa particular' in texto and indicadores['RENTAS_MINIMA_CASA_PARTICULAR'] == 0:
                    indicadores['RENTAS_MINIMA_CASA_PARTICULAR'] = extraer_monto(texto_raw)
                if 'para fines no remuneracionales' in texto and indicadores['RENTAS_MINIMA_NO_REMU'] == 0:
                    indicadores['RENTAS_MINIMA_NO_REMU'] = extraer_monto(texto_raw)

                # APV
                if 'tope mensual' in texto and indicadores['APV_TOPE_MENSUAL'] == 0:
                    indicadores['APV_TOPE_MENSUAL'] = extraer_monto(texto_raw)
                if 'tope anual' in texto and indicadores['APV_TOPE_ANUAL'] == 0:
                    indicadores['APV_TOPE_ANUAL'] = extraer_monto(texto_raw)

                # Depósito Convenido
                if 'tope anual (900 uf)' in texto and indicadores['DEPOSITO_CONVENIDO_TOPE_ANUAL'] == 0:
                    indicadores['DEPOSITO_CONVENIDO_TOPE_ANUAL'] = extraer_monto(texto_raw)
                
                # Seguro Cesantia
                # Seguro Cesantía Plazo Indefinido
                if 'plazo indefinido' in texto and not indicadores['SEGURO_CESANTIA_PLAZO_INDEF']:
                    celdas = fila.find_all('td')
                    if len(celdas) >= 3:
                        indicadores['SEGURO_CESANTIA_PLAZO_INDEF'] = [
                            extraer_monto(celdas[1].get_text(strip=True)),  # Empleador
                            extraer_monto(celdas[2].get_text(strip=True))   # Trabajador
                        ]

                # plazo fijo
                if 'plazo fijo' in texto and indicadores['SEGURO_CESANTIA_PLAZO_FIJO'] == 0:
                    celdas = fila.find_all('td')
                    if len(celdas) >= 2:
                        porcentaje = extraer_monto(celdas[1].get_text(strip=True))
                        indicadores['SEGURO_CESANTIA_PLAZO_FIJO'] = porcentaje

                #plazo indefinido 11 años
                # Seguro Cesantía 11 años
                if 'plazo indefinido 11 anos o mas (*)' in texto and indicadores['SEGURO_CESANTIA_11_ANNOS'] == 0:
                    celdas = fila.find_all('td')
                    if len(celdas) >= 2:
                        indicadores['SEGURO_CESANTIA_11_ANNOS'] = [
                            extraer_monto(celdas[1].get_text(strip=True)),
                            extraer_monto(celdas[2].get_text(strip=True))
                        ]

                #trabajador casa particular
                if 'trabajador de casa particular (**)' in texto and indicadores['SEGURO_CESANTIA_CASA_PARTICULAR'] == 0:
                    celdas = fila.find_all('td')
                    if len(celdas) >= 2:
                        indicadores['SEGURO_CESANTIA_CASA_PARTICULAR'] = [
                            extraer_monto(celdas[1].get_text(strip=True)),
                            extraer_monto(celdas[2].get_text(strip=True))
                        ]
                
                # CCAF y FONASA
                if 'ccaf' in texto and indicadores['DISTRIBUCION_7P_CCAF'] == 0:
                    indicadores['DISTRIBUCION_7P_CCAF'] = extraer_monto(texto_raw)
                if 'fonasa' in texto and indicadores['DISTRIBUCION_7P_FONASA'] == 0:
                    indicadores['DISTRIBUCION_7P_FONASA'] = extraer_monto(texto_raw)
                
                # Tasa AFP Capital
                if 'capital' in texto and indicadores['TASA_CAPITAL'] == 0:
                    celdas = fila.find_all('td')
                    if len(celdas) >= 4:
                        indicadores['TASA_CAPITAL'] = [
                            extraer_monto(celdas[1].get_text(strip=True)),  
                            extraer_monto(celdas[2].get_text(strip=True)),  
                            extraer_monto(celdas[3].get_text(strip=True))   
                        ]
                
                # Tasa AFP Cuprum
                if 'cuprum' in texto and indicadores['TASA_CUPRUM'] == 0:
                    celdas = fila.find_all('td')
                    if len(celdas) >= 4:
                        indicadores['TASA_CUPRUM'] = [
                            extraer_monto(celdas[1].get_text(strip=True)),
                            extraer_monto(celdas[2].get_text(strip=True)),
                            extraer_monto(celdas[3].get_text(strip=True))
                        ]

                # Tasa AFP Habitat
                if 'habitat' in texto and indicadores['TASA_HABITAT'] == 0:
                    celdas = fila.find_all('td')
                    if len(celdas) >= 4:
                        indicadores['TASA_HABITAT'] = [
                            extraer_monto(celdas[1].get_text(strip=True)),
                            extraer_monto(celdas[2].get_text(strip=True)),
                            extraer_monto(celdas[3].get_text(strip=True))
                        ]
                
                # Tasa AFP PlanVital
                if 'planvital' in texto and indicadores['TASA_PLANVITAL'] == 0:
                    celdas = fila.find_all('td')
                    if len(celdas) >= 4:
                        indicadores['TASA_PLANVITAL'] = [
                            extraer_monto(celdas[1].get_text(strip=True)),
                            extraer_monto(celdas[2].get_text(strip=True)),
                            extraer_monto(celdas[3].get_text(strip=True))
                        ]
                
                # Tasa AFP Uno
                if 'uno' in texto and indicadores['TASA_UNO'] == 0:
                    celdas = fila.find_all('td')
                    if len(celdas) >= 4:
                        indicadores['TASA_UNO'] = [
                            extraer_monto(celdas[1].get_text(strip=True)),
                            extraer_monto(celdas[2].get_text(strip=True)),
                            extraer_monto(celdas[3].get_text(strip=True))
                        ]
                
                # Tasa AFP ProVida
                if 'provida' in texto and indicadores['TASA_PROVIDA'] == 0:
                    celdas = fila.find_all('td')
                    if len(celdas) >= 4:
                        indicadores['TASA_PROVIDA'] = [
                            extraer_monto(celdas[1].get_text(strip=True)),
                            extraer_monto(celdas[2].get_text(strip=True)),
                            extraer_monto(celdas[3].get_text(strip=True))
                        ]
                
                # Tasa Modelo
                if 'modelo' in texto and indicadores['TASA_MODELO'] == 0:
                    celdas = fila.find_all('td')
                    if len(celdas) >= 4:
                        indicadores['TASA_MODELO'] = [
                            extraer_monto(celdas[1].get_text(strip=True)),
                            extraer_monto(celdas[2].get_text(strip=True)),
                            extraer_monto(celdas[3].get_text(strip=True))
                        ]
                                
                # Asignacion Familiar
                if '1 (a)' in texto and indicadores['ASIGNACION_FAMILIAR_A'] == 0:
                    celdas = fila.find_all('td')
                    if len(celdas) >=3:
                        indicadores['ASIGNACION_FAMILIAR_A'] =[
                            extraer_monto(celdas[1].get_text(strip=True)),
                            extraer_monto(celdas[2].get_text(strip=True))
                        ]

                # Asignación Familiar Tramo B
                if '2 (b)' in texto and indicadores['ASIGNACION_FAMILIAR_B'] == 0:
                    celdas = fila.find_all('td')
                    if len(celdas) >= 3:
                        texto_tope = celdas[2].get_text(strip=True)
                        partes = texto_tope.split('$')
                        ultimo_monto = extraer_monto('$' + partes[-1]) if len(partes) > 1 else extraer_monto(texto_tope)

                        indicadores['ASIGNACION_FAMILIAR_B'] = [
                            extraer_monto(celdas[1].get_text(strip=True)),  
                            ultimo_monto                                    
                        ]

                # Asignación Familiar Tramo C
                if '3 (c)' in texto and indicadores['ASIGNACION_FAMILIAR_C'] == 0:
                    celdas = fila.find_all('td')
                    if len(celdas) >= 3:
                        texto_tope = celdas[2].get_text(strip=True)
                        partes = texto_tope.split('$')
                        ultimo_monto = extraer_monto('$' + partes[-1]) if len(partes) > 1 else extraer_monto(texto_tope)

                        indicadores['ASIGNACION_FAMILIAR_C'] = [
                            extraer_monto(celdas[1].get_text(strip=True)),  
                            ultimo_monto                                    
                        ]
                
                # Asignación Familiar Trabo D
                if '4 (d)' in texto and indicadores['ASIGNACION_FAMILIAR_D'] == 0:
                    celdas = fila.find_all('td')
                    if len(celdas) >= 3:
                        texto_tope = celdas[2].get_text(strip=True)
                        partes = texto_tope.split('$')
                        ultimo_monto = extraer_monto('$' + partes[-1]) if len(partes) > 1 else extraer_monto(texto_tope)

                        indicadores['ASIGNACION_FAMILIAR_D'] = [
                            extraer_monto(celdas[1].get_text(strip=True)),  
                            ultimo_monto                                    
                        ]
                
                # Cotización trabajo pesado
                if 'trabajo pesado' in texto and indicadores['COTIZACION_TRAB_PESADO'] == 0:
                    celdas = fila.find_all('td')
                    if len(celdas) >= 4:
                        indicadores['COTIZACION_TRAB_PESADO'] =[
                            extraer_monto(celdas[1].get_text(strip=True)),
                            extraer_monto(celdas[2].get_text(strip=True)),
                            extraer_monto(celdas[3].get_text(strip=True))
                        ]
                
                # Cotizacion trabajo menos pesado
                if 'trabajo menos pesado' in texto and indicadores['COTIZACION_TRAB_MENOS_PESADO'] == 0:
                    celdas = fila.find_all('td')
                    if len(celdas) >= 3:
                        indicadores['COTIZACION_TRAB_MENOS_PESADO'] =[
                            extraer_monto(celdas[1].get_text(strip=True)),
                            extraer_monto(celdas[2].get_text(strip=True)),
                            extraer_monto(celdas[3].get_text(strip=True))
                        ]

        #Extraccion IPC
        soup_ipc = BeautifulSoup(page_ipc.content, "html.parser")
        tablas_ipc = soup_ipc.find_all('table')
        
        for tabla_ipc in tablas_ipc:
            for fila_ipc in tabla_ipc.find_all('tr'):
                _logger.info('fila_ipc %s' %(fila_ipc))
                texto_raw_ipc = fila_ipc.get_text(strip=True)
                #_logger.info('texto_raw_ipc %s' %(texto_raw_ipc))
                textos = normalizar(texto_raw_ipc)

                if re.search('2025', str(fila_ipc)) and indicadores['IPC'] == 0:
                    #_logger.info('textos %s' %(textos))
                    celdas = fila_ipc.find_all('td')
                    for celda in celdas:
                        get_txt = celda.get_text(strip=True)
                        celda = str(celda)
                        _logger.info('celda %s' %(celda))
                        _logger.info('type(celda) %s' %(type(celda)))
                        if re.search("Mayo", celda):
                            _logger.info('celda.get_text %s' %(get_txt))
                            indicadores['IPC'] = extraer_monto(get_txt)
                            break
                #if '2025' in textos and 'gr_ctl99_Mayo' and indicadores['IPC'] == 0:
                 #   celdas = fila_ipc.find_all("td")
                  #  if len(celdas) >= 6:
                   #     texto_ipc = celdas[5].get_text(strip=True)
                    #    indicadores['IPC'] = extraer_monto(texto_ipc)
                
        return indicadores