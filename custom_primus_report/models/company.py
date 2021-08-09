# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from datetime import datetime, time


class Company(models.Model):
    _inherit = 'res.company'
    
    code = fields.Char("Code #")
    fax = fields.Char("Fax")
    
class Users(models.Model):
    _inherit = 'res.users'
    
    sign = fields.Binary("Signature")
    
    