{
    'name': 'Liquidación',
    'version': '1.1',
    'summary': 'Calcula liquidación según días trabajados',
    'category': 'Human Resources',
    'depends': ['pways_hr_payroll'],
    'data': [
        'views/payslip_liquidacion_view.xml',
        'security/ir.model.access.csv'
    ],
    'installable': True,
}
