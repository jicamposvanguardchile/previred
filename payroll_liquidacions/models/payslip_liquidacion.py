import re
import requests
from bs4 import BeautifulSoup
from odoo import models
import unicodedata
import logging

_logger = logging.getLogger(__name__)

class HrPayslip(models.Model):
    _inherit = 'hr.payslip'

    def get_indicadores(self):
        url = 'https://www.previred.com/indicadores-previsionales/'
        response = requests.get(url)

        if response.status_code != 200:
            return

        soup = BeautifulSoup(response.text, 'html.parser')
        tablas = soup.find_all('table')

        datos = {
            'mes': 0,
            'uf_abril': 0,
            'uf_marzo':0,
            'utm_abril': 0,
            'uta_abril': 0,
            'af_afp': 0,
            'af_ips': 0,
            'seg_cesantia': 0,
            't_dep_indep': 0,
            'men_18_may_65': 0,
            't_casa': 0,
            'no_remun': 0,
            'a_tope_mens': 0,
            'a_tope_anual': 0,
            'd_tope_anual': 0,
            'ccaf': 0,
            'fonasa': 0
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

        for tabla in tablas:
            for fila in tabla.find_all('tr'):
                texto_raw = fila.get_text(strip=True)
                texto = normalizar(texto_raw)
                _logger.info('texto %s'%(texto))
                _logger.info('texto_raw %s'%(texto_raw))

                if ('uf abril' in texto or '30 de abril del 2025' in texto) and datos['uf_abril'] == 0:
                    datos['uf_abril'] = extraer_monto(texto_raw)
                
                if ('uf mayo' in texto or ' Al 31 de mayo del 2025' in texto) and datos['uf_marzo'] == 0:
                    datos['uf_marzo'] = extraer_monto(texto_raw)

                if ('utm abril' in texto or 'abril 2025' in texto) and datos['utm_abril'] == 0:
                    datos['utm_abril'] = extraer_monto(texto_raw)

                if ('uta abril' in texto or 'abril 2025' in texto) and datos['uta_abril'] == 0:
                    datos['uta_abril'] = extraer_monto(texto_raw)

                if 'para afiliados a una afp' in texto and datos['af_afp'] == 0:
                    datos['af_afp'] = extraer_monto(texto_raw)

                if ('ips' in texto or 'para afiliados a ips' in texto) and datos['af_ips'] == 0:
                    datos['af_ips'] = extraer_monto(texto_raw)

                if 'cesantia' in texto and datos['seg_cesantia'] == 0:
                    datos['seg_cesantia'] = extraer_monto(texto_raw)

                if 'dependientes e independientes' in texto and datos['t_dep_indep'] == 0:
                    datos['t_dep_indep'] = extraer_monto(texto_raw)

                if 'menores de 18 y mayores de 65' in texto and datos['men_18_may_65'] == 0:
                    datos['men_18_may_65'] = extraer_monto(texto_raw)

                if 'casa particular' in texto and datos['t_casa'] == 0:
                    datos['t_casa'] = extraer_monto(texto_raw)

                if 'no remuneracionales' in texto and datos['no_remun'] == 0:
                    datos['no_remun'] = extraer_monto(texto_raw)

                if 'tope mensual' in texto and '50' in texto and datos['a_tope_mens'] == 0:
                    datos['a_tope_mens'] = extraer_monto(texto_raw)

                if 'tope anual' in texto and '600' in texto and datos['a_tope_anual'] == 0:
                    datos['a_tope_anual'] = extraer_monto(texto_raw)

                if 'tope anual (900 uf)' in texto and datos['d_tope_anual'] == 0:
                    datos['d_tope_anual'] = extraer_monto(texto_raw)
                
                if 'ccaf' in texto and datos['ccaf'] == 0:
                    datos['ccaf'] = extraer_monto(texto_raw)
                
                if 'fonasa' in texto and datos['fonasa'] == 0:
                    datos['fonasa'] = extraer_monto(texto_raw)

        datos['mes'] = 202505
        indicador = self.env['hr.indicadores2'].create(datos)

        #tablas = soup.find_all('table')

        def normalizar(texto):
            texto = unicodedata.normalize('NFKD', texto)
            return ''.join(c for c in texto if not unicodedata.combining(c)).lower()

        def extraer_monto(texto):
            match = re.search(r'\$\s*(\d[\d\.\,]*)', texto)
            if not match:
                match = re.search(r'(\d[\d\.\,]*)', texto)
            return float(match.group(1).replace('.', '').replace(',', '.')) if match else 0.0

        for tabla in tablas:
            encabezado = normalizar(tabla.get_text())
            if 'asignacion familiar' in encabezado:
                for fila in tabla.find_all('tr')[1:]:
                    celdas = fila.find_all('td')
                    if len(celdas) >= 2:
                        tramo = celdas[0].get_text(strip=True)
                        monto = extraer_monto(celdas[1].get_text(strip=True))
                        self.env['hr.asignacion.familiar'].create({
                            'renta_ingresada': 0.0, 
                            'tramo': tramo,
                            'monto': monto,
                            'indicador_id': indicador.id
                        })

        for tabla in tablas:
            encabezado = normalizar(tabla.get_text())
            if 'seguro de cesantia' in encabezado or 'afc' in encabezado:
                for fila in tabla.find_all('tr')[1:]:
                    celdas = fila.find_all('td')
                    if len(celdas) >= 3:
                        contrato = celdas[0].get_text(strip=True)
                        empleador = extraer_monto(celdas[1].get_text(strip=True))
                        trabajador = extraer_monto(celdas[2].get_text(strip=True))


                        self.env['hr.seguro.cesantia'].create({
                            'contrato': contrato,
                            'empleador': empleador,
                            'trabajador': trabajador,
                            'seguro_id': indicador.id
                        })
                
    
        #tablas = soup.find_all('table')

        for tabla in tablas:
            encabezado = normalizar(tabla.get_text())
            if 'tasa cotización obligatorio afp' in encabezado or 'afp' in encabezado:
                for fila in tabla.find_all('tr')[1:]: 
                    celdas = fila.find_all('td')
                    if len(celdas) >= 4:  
                        tipo_afp = celdas[0].get_text(strip=True)
                        tasa_afp = extraer_monto(celdas[1].get_text(strip=True))  
                        tasa_sis = extraer_monto(celdas[2].get_text(strip=True))  
                        tasa_afp3 = extraer_monto(celdas[3].get_text(strip=True))  

                        # Crear el registro en el modelo
                        self.env['hr.cotizacion.obligatoria.afp'].create({
                            'tipo_afp': tipo_afp,
                            'tasa_afp': tasa_afp,
                            'sis': tasa_sis,
                            'tasa_afp3': tasa_afp3,
                            'indicador_afp_id': indicador.id
                        })

        #tablas = soup.find_all('table')

        def extraer_porcentaje(texto):
            match = re.search(r'(\d{1,2},\d{1,2})\s*%', texto)
            if match:
                return match.group(1).replace(',', '.') + '%'
            return texto.strip()

        for tabla in tablas:
            encabezado = normalizar(tabla.get_text())
            if 'trabajo pesado' in encabezado or 'trabajos menos pesados' in encabezado:
                for fila in tabla.find_all('tr')[1:]:
                    celdas = fila.find_all('td')
                    if len(celdas) >= 3:
                        puesto = celdas[0].get_text(strip=True)
                        empleador = extraer_porcentaje(celdas[1].get_text(strip=True))
                        trabajador = extraer_porcentaje(celdas[2].get_text(strip=True))


                        self.env['hr.cotizacion_trabajos_pesados'].create({
                            'puesto_trabajo': puesto,
                            'financ_empleador': empleador,
                            'financ_trabajador': trabajador,
                            'trabajos_id': indicador.id
                        })
                