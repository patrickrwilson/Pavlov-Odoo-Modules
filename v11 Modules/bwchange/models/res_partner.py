from odoo import models, fields

class Partner(models.Model):
    _inherit = 'res.partner'

    bandwidth_changes = fields.One2many('bwchange.change',
                                        'partner_id',
                                        string="Bandwidth Changes")