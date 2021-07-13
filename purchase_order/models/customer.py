from odoo import api, fields, models
from openerp import models, fields, api
import logging
import requests, json
_logger = logging.getLogger(__name__)

class sales_details(models.Model):
    _name = "sales.customer"
    _description = "sales details"

    @api.onchange('current_date')
    def dates(self):
        if self.current_date:
            Price = self.env['sales_detail.customers'].search([('current_date', '=', self.current_date),('jewellery_type', '=', self.jewellery_type)])
            self.Price = Price.Price
            # logger.info("Error : Price = %s" %Price)

    @api.onchange('jewellery_type')
    def jewellery(self):
        if self.jewellery_type:
            Price = self.env['sales_detail.customers'].search([('current_date', '=', self.current_date),('jewellery_type', '=', self.jewellery_type)])
            self.Price = Price.Price
            # _logger.info("Error : Price = %s" %Price)
            # _logger.info("Error : current_date = %s" %self.current_date)
            # _logger.info("Error : jewellery_type = %s" %self.jewellery_type)
   
    current_date = fields.Date(string='Date' , default=fields.Date.today)
    Price  = fields.Float(string='Total-Price')
    jewellery_type  = fields.Selection([
        ('Gold', 'Gold'),
        ('Silver', 'Silver'),
        ('Platinum', 'Platinum'),
    ], required=True, default='Gold')




class sales(models.Model):
    _name = "sales_detail.customers"
    current_date = fields.Date(string='Date' , default=fields.Date.today)
    jewellery_type  = fields.Selection([
        ('Gold', 'Gold'),
        ('Silver', 'Silver'),
        ('Platinum', 'Platinum'),
    ], required=True, default='Gold')
    Price  = fields.Float(string='Total-Price')

    