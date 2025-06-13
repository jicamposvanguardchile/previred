from odoo import api, models


class payslip_report(models.AbstractModel):
    #_inherit = 'pways.hr.payroll.report'

    @api.model
    def _get_report_values(self, docids, data=None):
        payslips = super(payslip_report, self)._get_report_values(docids, data)
        #payslips.update({
#        	'get_payslip_lines': self.get_payslip_lines(),
#            #'convert': self.convert(),
#            'get_leave':self.get_leave(),
#        })
        return payslips

    def convert(self,amount, cur):
        amt_en = cur.amount_to_text(amount)
        return amt_en

    def get_payslip_lines(self):
        payslip_line = self.env['hr.payslip.line']
        res = []
        ids = []
        for rec in self:
            if rec.appears_on_payslip is True:
                ids.append(rec.id)
        if ids:
            res = payslip_line.browse(ids)
        return res

    def get_leave(self, obj):
        res = []
        ids = []
        for rec in self:
            if rec.type == 'leaves':
                ids.append(rec.id)
            payslip_line = self.env['hr.payslip.line']
            if ids:
                res = payslip_line.browse(ids)
        return res
