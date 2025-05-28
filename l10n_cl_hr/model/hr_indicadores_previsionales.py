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


URL_PREVIRED = "https://www.previred.com/web/previred/indicadores-previsionales"

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
    asignacion_familiar_primer = fields.Float('Asignación Familiar Tramo 1', readonly=True, states=STATES,
        help="Asig Familiar Primer Tramo")
    asignacion_familiar_segundo = fields.Float('Asignación Familiar Tramo 2', readonly=True, states=STATES,
        help="Asig Familiar Segundo Tramo")
    asignacion_familiar_tercer = fields.Float('Asignación Familiar Tramo 3', readonly=True, states=STATES,
        help="Asig Familiar Tercer Tramo")
    asignacion_familiar_monto_a = fields.Float( 'Monto Tramo Uno', readonly=True, states=STATES, help="Monto A")
    asignacion_familiar_monto_b = fields.Float( 'Monto Tramo Dos', readonly=True, states=STATES, help="Monto B")
    asignacion_familiar_monto_c = fields.Float( 'Monto Tramo Tres', readonly=True, states=STATES, help="Monto C")
    contrato_plazo_fijo_empleador = fields.Float( 'Contrato Plazo Fijo Empleador', readonly=True, states=STATES,
        help="Contrato Plazo Fijo Empleador")
    contrato_plazo_fijo_trabajador = fields.Float( 'Contrato Plazo Fijo Trabajador', readonly=True, states=STATES,
        help="Contrato Plazo Fijo Trabajador")    
    contrato_plazo_indefinido_empleador = fields.Float( 'Contrato Plazo Indefinido Empleador', readonly=True, states=STATES,
        help="Contrato Plazo Fijo")
    contrato_plazo_indefinido_empleador_otro = fields.Float( 'Contrato Plazo Indefinido Empleador 11 anos o mas', 
        readonly=True, states=STATES, help="Contrato Plazo Indefinido 11 anos Empleador")
    contrato_plazo_indefinido_trabajador_otro = fields.Float( 'Contrato Plazo Indefinido Trabajador 11 anos o mas', 
        readonly=True, states=STATES, help="Contrato Plazo Indefinido 11 anos Trabajador")
    contrato_plazo_indefinido_trabajador = fields.Float( 'Contrato Plazo Indefinido Trabajador', readonly=True, states=STATES,
        help="Contrato Plazo Indefinido Trabajador")
    caja_compensacion  = fields.Float( 'Caja Compensación', readonly=True, states=STATES, help="Caja de Compensacion")
    deposito_convenido = fields.Float( 'Deposito Convenido', readonly=True, states=STATES, help="Deposito Convenido")
    fonasa = fields.Float('Fonasa', readonly=True, states=STATES, help="Fonasa")
    mutual_seguridad = fields.Float( 'Mutualidad', readonly=True, states=STATES, help="Mutual de Seguridad")
    isl = fields.Float( 'ISL', readonly=True, states=STATES, help="Instituto de Seguridad Laboral")
    pensiones_ips = fields.Float( 'Pensiones IPS', readonly=True, states=STATES, help="Pensiones IPS")
    sueldo_minimo = fields.Float( 'Trab. Dependientes e Independientes', readonly=True, states=STATES, help="Sueldo Minimo")
    sueldo_minimo_otro = fields.Float( 'Menores de 18 y Mayores de 65:', readonly=True, states=STATES,
        help="Sueldo Mínimo para Menores de 18 y Mayores a 65")
    tasa_afp_cuprum  = fields.Float( 'Cuprum', readonly=True, states=STATES, help="Tasa AFP Cuprum")
    tasa_afp_capital = fields.Float( 'Capital', readonly=True, states=STATES, help="Tasa AFP Capital")
    tasa_afp_provida = fields.Float( 'ProVida', readonly=True, states=STATES, help="Tasa AFP Provida")
    tasa_afp_modelo  = fields.Float( 'Modelo', readonly=True, states=STATES, help="Tasa AFP Modelo")
    tasa_afp_planvital = fields.Float( 'PlanVital', readonly=True, states=STATES, help="Tasa AFP PlanVital")
    tasa_afp_habitat = fields.Float( 'Habitat',  help="Tasa AFP Habitat")
    tasa_afp_uno = fields.Float( 'Uno', help="Tasa AFP Uno")
    tasa_sis_cuprum  = fields.Float('SIS', readonly=True, states=STATES, help="Tasa SIS Cuprum")
    tasa_sis_capital = fields.Float( 'SIS', readonly=True, states=STATES, help="Tasa SIS Capital")
    tasa_sis_provida = fields.Float( 'SIS', readonly=True, states=STATES, help="Tasa SIS Provida")
    tasa_sis_planvital = fields.Float( 'SIS', readonly=True, states=STATES, help="Tasa SIS PlanVital")
    tasa_sis_habitat = fields.Float( 'SIS', readonly=True, states=STATES, help="Tasa SIS Habitat")
    tasa_sis_modelo  = fields.Float( 'SIS',  help="Tasa SIS Modelo")
    tasa_sis_uno = fields.Float( 'SIS', help="Tasa SIS Uno")
    tasa_independiente_cuprum = fields.Float( 'SIS', readonly=True, states=STATES, help="Tasa Independientes Cuprum")
    tasa_independiente_capital = fields.Float( 'SIS', readonly=True, states=STATES, help="Tasa Independientes Capital")
    tasa_independiente_provida = fields.Float( 'SIS', readonly=True, states=STATES, help="Tasa Independientes Provida")
    tasa_independiente_planvital = fields.Float( 'SIS', readonly=True, states=STATES, help="Tasa Independientes PlanVital")
    tasa_independiente_habitat = fields.Float( 'SIS', readonly=True, states=STATES, help="Tasa Independientes Habitat")
    tasa_independiente_modelo = fields.Float( 'SIS',  help="Tasa Independientes Modelo")
    tasa_independiente_uno = fields.Float( 'SIS', help="Tasa Independientes Uno")
    tope_anual_apv = fields.Float( 'Tope Anual APV', readonly=True, states=STATES, help="Tope Anual APV")
    tope_mensual_apv = fields.Float( 'Tope Mensual APV', readonly=True, states=STATES, help="Tope Mensual APV")
    tope_imponible_afp = fields.Float( 'Tope imponible AFP', readonly=True, states=STATES, help="Tope Imponible AFP")
    tope_imponible_ips = fields.Float( 'Tope Imponible IPS', readonly=True, states=STATES, help="Tope Imponible IPS")
    tope_imponible_salud = fields.Float( 'Tope Imponible Salud', readonly=True, states=STATES,)
    tope_imponible_seguro_cesantia = fields.Float( 'Tope Imponible Seguro Cesantía', readonly=True, states=STATES,
        help="Tope Imponible Seguro de Cesantía")
    uf  = fields.Float('UF', states=STATES, help="UF fin de Mes")
    utm = fields.Float('UTM',  readonly=True, states=STATES, help="UTM Fin de Mes")
    uta = fields.Float('UTA', readonly=True, states=STATES, help="UTA Fin de Mes")
    uf_otros = fields.Float( 'UF Otros', readonly=True, states=STATES, help="UF Seguro Complementario")
    mutualidad_id = fields.Many2one('hr.mutual', 'MUTUAL', readonly=True, states=STATES)
    ccaf_id = fields.Many2one('hr.ccaf', 'CCAF', readonly=True, states=STATES)
    month = fields.Selection(MONTH_LIST, string='Mes',  states=STATES)
    year = fields.Integer('Año',  default=datetime.now().strftime('%Y'), readonly=True, states=STATES)
    gratificacion_legal = fields.Boolean('Gratificación L. Manual', readonly=True, states=STATES)
    mutual_seguridad_bool = fields.Boolean('Mutual Seguridad', default=True, readonly=True, states=STATES)
    ipc = fields.Float('IPC',   readonly=True, states=STATES, help="Indice de Precios al Consumidor (IPC)")
    
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
        try:
            url = 'https://www.previred.com/indicadores-previsionales/'
            _logger.info('url %s'%(url))
            page = urlopen(url)
            html_bytes = page.read()
            html = html_bytes.decode("utf-8")
            brute = re.findall("\$ [\d\.,]+<|>[\d]+\.[\d\.]+<|>[\d,]+%<|>[\d,]+% R\.I\. ?<", html)
            _logger.info('brute %s'%(brute))
            pure = []
            for item in brute:
                pure.append(float((re.search("[\d\.,]+", item)[0]).replace('.','').replace(',','.')))
        except ValueError:
            return ""

        try:
            new_ind = self._hrIndPrevired()
            _logger.info('new_ind %s'%(new_ind))
            mes = new_ind('MES_UTM') or ''
            uf_mes = new_ind.t('UF', {}).get(mes)
            if not mes or uf_mes is None:
                raise ValueError(f"Mes UTM no encontrado o no existe UF para el mes '{mes}'")
        
            # UF
            self.uf = uf_mes

            # 1 UTM
            self.utm = new_ind['UTM']

            # 1 UTA
            self.uta = new_ind['UTA', 0.0]

            # 3 RENTAS TOPES IMPONIBLES (UF)
            self.tope_imponible_afp             = new_ind['RENTAS_TOPE_AFP'][0]
            self.tope_imponible_ips             = new_ind['RENTAS_TOPE_IPS', [0.0]][0] 
            self.tope_imponible_seguro_cesantia = new_ind['RENTAS_TOPE_SEGURO', [0.0]][0] 

            # 4 RENTAS MINIMAS IMPONIBLES
            self.sueldo_minimo      = new_ind['RENTAS_MINIMA_DEP_INDEP', [0.0]][0]
            self.sueldo_minimo_otro = new_ind['RENTAS_MINIMA_18_Y_65', [0.0]][0]

            # Ahorro Previsional Voluntario (UF)
            self.tope_mensual_apv = new_ind['APV_TOPE_MENSUAL'[0.0]][0]
            self.tope_anual_apv   = new_ind['APV_TOPE_ANUAL'[0.0]][0]

            # 5 DEPÓSITO CONVENIDO (UF)
            self.deposito_convenido = new_ind['DEPOSITO_CONVENIDO_TOPE_ANUAL', [0.0]][0]

            # 6 SEGURO DE CESANTÍA (AFC)
            self.contrato_plazo_indefinido_empleador      = new_ind['SEGURO_CESANTIA_PLAZO_INDEF', [0.0]][0]
            self.contrato_plazo_indefinido_trabajador     = new_ind['SEGURO_CESANTIA_PLAZO_INDEF', [0.0]][1]
            self.contrato_plazo_fijo_empleador            = new_ind['SEGURO_CESANTIA_PLAZO_FIJO', 0.0]
            self.contrato_plazo_indefinido_empleador_otro = new_ind['SEGURO_CESANTIA_11_ANNOS', 0.0]

            # 7 ASIGNACIÓN FAMILIAR
            self.asignacion_familiar_monto_a = new_ind['ASIGNACION_FAMILIAR_A', [0.0]][0]
            self.asignacion_familiar_monto_b = new_ind['ASIGNACION_FAMILIAR_B', [0.0]][0]
            self.asignacion_familiar_monto_c = new_ind['ASIGNACION_FAMILIAR_C', [0.0]][0]

            self.asignacion_familiar_primer  = new_ind['ASIGNACION_FAMILIAR_A', [0.0]][1]
            self.asignacion_familiar_segundo = new_ind['ASIGNACION_FAMILIAR_B', [0.0]][1]
            self.asignacion_familiar_tercer  = new_ind['ASIGNACION_FAMILIAR_C', [0.0]][1]

            # 8 TASA COTIZACIÓN OBLIGATORIO AFP
            self.tasa_afp_capital           = new_ind['TASA_CAPITAL', [0.0]][0]
            self.tasa_sis_capital           = new_ind['TASA_CAPITAL', [0.0]][1]
            self.tasa_independiente_capital = new_ind['TASA_CAPITAL', [0.0]][2]

            self.tasa_afp_cuprum           = new_ind['TASA_CUPRUM', [0.0]][0]
            self.tasa_sis_cuprum           = new_ind['TASA_CUPRUM', [0.0]][1]
            self.tasa_independiente_cuprum = new_ind['TASA_CUPRUM', [0.0]][2]

            self.tasa_afp_habitat           = new_ind['TASA_HABITAT', [0.0]][0]
            self.tasa_sis_habitat           = new_ind['TASA_HABITAT', [0.0]][1]
            self.tasa_independiente_habitat = new_ind['TASA_HABITAT', [0.0]][2]

            self.tasa_afp_planvital           = new_ind['TASA_PLANVITAL', [0.0]][0]
            self.tasa_sis_planvital           = new_ind['TASA_PLANVITAL', [0.0]][1]
            self.tasa_independiente_planvital = new_ind['TASA_PLANVITAL', [0.0]][2]

            self.tasa_afp_provida           = new_ind['TASA_PROVIDA', [0.0]][0]
            self.tasa_sis_provida           = new_ind['TASA_PROVIDA', [0.0]][1]
            self.tasa_independiente_provida = new_ind['TASA_PROVIDA', [0.0]][2]

            self.tasa_afp_modelo           = new_ind['TASA_MODELO', [0.0]][0]
            self.tasa_sis_modelo           = new_ind['TASA_MODELO', [0.0]][1]
            self.tasa_independiente_modelo = new_ind['TASA_MODELO', [0.0]][2]

            self.tasa_afp_uno           = new_ind['TASA_UNO', [0.0]][0]
            self.tasa_sis_uno           = new_ind['TASA_UNO', [0.0]][1]
            self.tasa_independiente_uno = new_ind['TASA_UNO', [0.0]][2]
        except Exception as e:
            _logger.error(f"Error actualizando indicadores previsionales: {e}")



    def _hrIndPrevired(self):
        page = requests.get(URL_PREVIRED)
        if page.status_code != 200:
            return None

        indicadores = {
            'UF':0,
            'UTM':0,
            'UTA':0,
            'MES_UTM':0,
            'RENTAS_TOPE_AFP':[],
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
            _logger.info('extraccion %s'%(extraccion))
            if extraccion:
                return float(extraccion.group(1).replace('.', '').replace(',', '.').replace('$', '').replace('%', ''))
            return 0
        
        def extraer_porcentaje(texto):
            match = re.search(r'(\d{1,2},\d{1,2})\s*%', texto)
            if match:
                return match.group(1).replace(',', '.') + '%'
            return texto.strip()

        soup = BeautifulSoup(page.content, "html.parser")
        indicadores['mes'] = MONTH_LIST

        tablas = soup.find_all('table')
        for tabla in tablas:
            for fila in tabla.find_all('tr'):
                texto_raw = fila.get_text(strip=True)
                texto = normalizar(texto_raw)

                if ('uf' in texto or 'Al 31 de mayo del 2025' in texto) and indicadores['UF'] == 0:
                    indicadores['UF'] = extraer_monto(texto_raw)
                
                if ('utm' in texto or 'mayo 2025' in texto) and indicadores['UTM'] == 0:
                    indicadores['UTM'] = extraer_monto(texto_raw)

                if ('uta' in texto or 'mayo 2025' in texto) and indicadores['UTA'] == 0:
                    indicadores['UTA'] = extraer_monto(texto_raw)  

                if ('mes' in texto or 'Al 31 de mayo del 2025' in texto) and indicadores['MES_UTM'] == 0:
                    indicadores['MES_UTM'] = extraer_monto(texto_raw)
                
                if 'para afiliados a una afp' in texto and indicadores['RENTAS_TOPE_AFP'] == 0:
                    indicadores['RENTAS_TOPE_AFP'] = extraer_monto(texto_raw)
                
                if ('ips' in texto or 'para afiliados a ips' in texto) and indicadores['RENTAS_TOPE_IPS'] == 0:
                    indicadores['RENTAS_TOPE_IPS'] = extraer_monto(texto_raw)

                if 'cesantia' in texto and indicadores['RENTAS_TOPE_SEGURO'] == 0:
                    indicadores['RENTAS_TOPE_SEGURO'] = extraer_monto(texto_raw)

            s = div.find_all(class_='encabezado_tabla_ind')
            for encabezado in s:
                titulo = encabezado.get_text().strip().upper()
                #print('-'+f.get_text()+'-')
                if titulo == 'VALOR UF':
                    for tr in div.find_all('tr'):
                        texto = tr.get_text()
                        fecha_match = re.search(r'al\s+(\d+)\s+de\s+(\w+)\s+(\d+)', texto, re.IGNORECASE)
                        if fecha_match:
                            mes = fecha_match.group(2).upper()
                            valor_match = re_monto_patron.search(texto)
                            if valor_match:
                                indicadores['UF'][mes] = extraer_monto(valor_match.group(1))

                elif titulo == 'VALORES UTM Y UTA':
                    for tr in div.find_all('tr'):
                        celdas = tr.find_all('td')
                        if len(celdas) >= 3:
                            mes_utm = celdas[0].get_text().strip().upper()
                            utm = extraer_monto(celdas[1].get_text())
                            uta = extraer_monto(celdas[2].get_text())
                            indicadores['MES_UTM'] = mes_utm
                            indicadores['UTM'] = utm
                            indicadores['UTA'] = uta                

                elif 'RENTAS TOPES IMPONIBLES' in titulo:
                    for tr in div.find_all('tr'):
                        texto = tr.get_text().strip().lower()
                        valores = re_monto_patron.findall(tr.get_text())
                        if 'afp' in texto and valores:
                            indicadores['RENTAS_TOPE_AFP'] = [extraer_monto(valores[0])]
                        elif 'ips' in texto and valores:
                            indicadores['RENTAS_TOPE_IPS'] = [extraer_monto(valores[0])]
                        elif 'cesantia' in texto and valores:
                            indicadores['RENTAS_TOPE_SEGURO'] = [extraer_monto(valores[0])]

                elif 'RENTAS MÍNIMAS' in titulo or 'RENTAS MINIMAS' in titulo:
                    for tr in div.find_all('tr'):
                        texto = tr.get_text().strip().lower()
                        valores = re_monto_patron.findall(tr.get_text())
                        if 'dependientes' in texto and valores:
                            indicadores['RENTAS_MINIMA_DEP_INDEP'] = [extraer_monto(valores[0])]
                        elif 'menores de 18' in texto and valores:
                            indicadores['RENTAS_MINIMA_18_Y_65'] = [extraer_monto(valores[0])]
                        elif 'casa particular' in texto and valores:
                            indicadores['RENTAS_MINIMA_CASA_PARTICULAR'] = [extraer_monto(valores[0])]
                        elif 'no remuneracionales' in texto and valores:
                            indicadores['RENTAS_MINIMA_NO_REMU'] = [extraer_monto(valores[0])]

                elif 'AHORRO PREVISIONAL VOLUNTARIO (APV)' in titulo:
                    for tr in div.find_all('tr'):
                        texto = tr.get_text().strip().lower()
                        valores = re_monto_patron.findall(tr.get_text())
                        if 'mensual' in texto and valores:
                            indicadores['APV_TOPE_MENSUAL'] = [extraer_monto(valores[0])]
                        elif 'anual' in texto and valores:
                            indicadores['APV_TOPE_ANUAL'] = [extraer_monto(valores[0])]

                elif 'DEPÓSITO CONVENIDO' in titulo:
                    for tr in div.find_all('tr'):
                        valores = re_monto_patron.findall(tr.get_text())
                        if valores:
                            indicadores['DEPOSITO_CONVENIDO_TOPE_ANUAL'] = [extraer_monto(valores[0])]

                elif 'SEGURO DE CESANTÍA (AFC)' in titulo:
                    for tr in div.find_all('tr'):
                        texto = tr.get_text().strip().lower()
                        valores = re.findall(r'(\d+,\d+)\s*%', texto)
                        if 'indefinido' in texto and len(valores) >= 2:
                            indicadores['SEGURO_CESANTIA_PLAZO_INDEF'] = [float(v.replace(',', '.')) for v in valores]
                        elif 'plazo fijo' in texto and valores:
                            indicadores['SEGURO_CESANTIA_PLAZO_FIJO'] = [float(valores[0].replace(',', '.'))]
                        elif '11 anos' in texto and valores:
                            indicadores['SEGURO_CESANTIA_11_ANNOS'] = [float(valores[0].replace(',', '.'))]
                        elif 'casa particular' in texto and valores:
                            indicadores['SEGURO_CESANTIA_CASA_PARTICULAR'] = [float(valores[0].replace(',', '.'))]
                elif 'DISTRIBUCIÓN DEL 7% SALUD, PARA EMPLEADORES AFILIADOS A CCAF (*)' in titulo:
                    for tr in div.find_all('tr'):
                        texto = tr.get_text().strip().lower()
                        porcentajes = re_monto_porcentaje.findall(texto)
                        if 'ccaf' in texto and porcentajes:
                            indicadores['DISTRIBUCION_7P_CCAF'] = [float(p.replace(',', '.')) for p in porcentajes]
                        elif 'fonasa' in texto and porcentajes:
                            indicadores['DISTRIBUCION_7P_FONASA'] = [float(p.replace(',', '.')) for p in porcentajes]

                elif 'TASA COTIZACIÓN OBLIGATORIO AFP' in titulo:
                    for tr in div.find_all('tr'):
                        if titulo().strip() != tr.get_text().strip():
                            b = re.findall(r'>\s*Capital\s*<',str(tr),re.IGNORECASE)
                            if b:
                                valor_clp = re_monto_porcentaje.findall(str(tr))
                                indicadores['TASA_CAPITAL'] = [
                                        locale.atof(valor_clp[0]),
                                        locale.atof(valor_clp[1]),
                                        locale.atof(valor_clp[2])]
                            b = re.findall(r'>\s*Cuprum\s*<',str(tr),re.IGNORECASE)
                            if b:
                                valor_clp = re_monto_porcentaje.findall(str(tr))
                                indicadores['TASA_CUPRUM'] = [
                                        locale.atof(valor_clp[0]),
                                        locale.atof(valor_clp[1]),
                                        locale.atof(valor_clp[2])]
                            b = re.findall(r'>\s*Habitat\s*<',str(tr),re.IGNORECASE)
                            if b:
                                valor_clp = re_monto_porcentaje.findall(str(tr))
                                indicadores['TASA_HABITAT'] = [
                                        locale.atof(valor_clp[0]),
                                        locale.atof(valor_clp[1]),
                                        locale.atof(valor_clp[2])]
                            b = re.findall(r'>\s*PlanVital\s*<',str(tr),re.IGNORECASE)
                            if b:
                                valor_clp = re_monto_porcentaje.findall(str(tr))
                                indicadores['TASA_PLANVITAL'] = [
                                        locale.atof(valor_clp[0]),
                                        locale.atof(valor_clp[1]),
                                        locale.atof(valor_clp[2])]
                            b = re.findall(r'>\s*ProVida\s*<',str(tr),re.IGNORECASE)
                            if b:
                                valor_clp = re_monto_porcentaje.findall(str(tr))
                                indicadores['TASA_PROVIDA'] = [
                                        locale.atof(valor_clp[0]),
                                        locale.atof(valor_clp[1]),
                                        locale.atof(valor_clp[2])]
                            b = re.findall(r'>\s*Modelo\s*<',str(tr),re.IGNORECASE)
                            if b:
                                valor_clp = re_monto_porcentaje.findall(str(tr))
                                indicadores['TASA_MODELO'] = [
                                        locale.atof(valor_clp[0]),
                                        locale.atof(valor_clp[1]),
                                        locale.atof(valor_clp[2])]
                            b = re.findall(r'>\s*Uno\s*<',str(tr),re.IGNORECASE)
                            if b:
                                valor_clp = re_monto_porcentaje.findall(str(tr))
                                indicadores['TASA_UNO'] = [
                                        locale.atof(valor_clp[0]),
                                        locale.atof(valor_clp[1]),
                                        locale.atof(valor_clp[2])]
                elif 'ASIGNACIÓN FAMILIAR' in titulo:
                    for tr in div.find_all('tr')[1:]:
                        celdas = tr.find_all('td')
                        if len(celdas) >= 2:
                            tramo = celdas[0].get_text(strip=True).upper()
                            monto = extraer_monto(celdas[1].get_text(strip=True))
                            limite = extraer_monto(celdas[0].get_text(strip=True).split()[-1])
                            if   'A' in tramo:
                                indicadores['ASIGNACION_FAMILIAR_A'] = [monto, limite]
                            elif 'B' in tramo:
                                indicadores['ASIGNACION_FAMILIAR_B'] = [monto, limite]
                            elif 'C' in tramo:
                                indicadores['ASIGNACION_FAMILIAR_C'] = [monto, limite]
                            elif 'D' in tramo:
                                indicadores['ASIGNACION_FAMILIAR_D'] = [monto, limite]                
                
                elif 'TRABAJOS PESADOS' in titulo or 'TRABAJO PESADO' in titulo:
                    for tr in div.find_all('tr')[1:]:
                        celdas = tr.find_all('td')
                        if len(celdas) >= 3:
                            puesto = celdas[0].get_text(strip=True).upper()
                            empleador = extraer_monto(celdas[1].get_text(strip=True))
                            trabajador = extraer_monto(celdas[2].get_text(strip=True))
                            if 'MENOS PESADO' in puesto:
                                indicadores['COTIZACION_TRAB_MENOS_PESADO'] = [empleador, trabajador]
                            else:
                                indicadores['COTIZACION_TRAB_PESADO'] = [empleador, trabajador]
                
        self.env['hr.indicadores2'].create(indicadores)
        _logger.info('self %s'%(self))

        return indicadores