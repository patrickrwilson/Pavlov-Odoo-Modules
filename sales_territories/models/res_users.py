from odoo import models, fields

class Users(models.Model):
    _inherit = 'res.users'

    salesterritories = fields.Many2many('sales_territories.salesterritories', string="Sales Territory")
