# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools

class Product_Master_Creation(models.Model):
    _inherit='product.template'
    stone=fields.Boolean(string='Is a Stone')
    name=fields.Char(string='Name')
    shape=fields.Char(string='Shape')
    size=fields.Char(string='Size')
    color=fields.Char(string='Color')
    cutting=fields.Char(string='Cutting')
    quality=fields.Char(string='Quality')

    origin=fields.Char(string='Origin')
    treatment=fields.Char(string='Treatment')
    certification_lab=fields.Char(string='Certification Lab')
    min_weight=fields.Float(string='Min Weight')
    avg=fields.Float(string='Average')
    vendor=fields.Char(string='Vendor')

    metal=fields.Boolean(string='Is a Metal')
    finess=fields.Char(string='Fineness')
    plating=fields.Char(string='Plating')
    plating_thickness=fields.Char(string='Plating Thickness')
    vendor=fields.Char(string='Vendor')
    uom=fields.Char(string='UOM')
    avg_cost=fields.Char(string='Average Cost')
    last_revised_cost=fields.Char(string='Last Revised Cost')


class EarClasp(models.Model):
    _name='ear.clasp'
    name=fields.Char(string='Name')

class ChainLength(models.Model):
    _name='chain.length'
    name=fields.Char(string='Name')

class BraceletLength(models.Model):
    _name='bracelet.length'
    name=fields.Char(string='Name')

    
class BraceletClasp(models.Model):
    _name='bracelet.clasp'
    name=fields.Char(string='Name')

class BraceletSafety(models.Model):
    _name='bracelet.safety'
    name=fields.Char(string='Name')

class ExtenderLength(models.Model):
    _name='extender.length'
    name=fields.Char(string=' Name')

class ChainClasp(models.Model):
    _name='chain.clasp'
    name=fields.Char(string='Name')

class EarRing(models.Model):
    _name='ear.ring'
    name=fields.Char(string='Name')
    drop_length=fields.Float(string='Drop Length')
    drop_width=fields.Float(string='Drop Width')
    ear_clasp=fields.Many2one('ear.clasp', string='Ear Clasp')
    inside_dia=fields.Char(string='Inside DIA')

class Pendant(models.Model):
    _name='pendant'
    name=fields.Char(string='Name')
    chain = fields.Selection([('yes', 'Yes'),('no', 'No'),], string='Chain')
    chain_length=fields.Many2one('chain.length', string='Chain Length')
    chain_clasp=fields.Many2one('chain.clasp', string='Chain Clasp')
    drop_length=fields.Float(string='Drop Length')

class Bracelet(models.Model):
    _name='bracelet'
    name=fields.Char(string='Name')
    extender=fields.Char(string='Extender')
    length=fields.Many2one('bracelet.length',string='Length')
    clasp=fields.Many2one('bracelet.clasp', string='Clasp')
    safety=fields.Many2one('bracelet.safety', string='Safety')
    extender_length=fields.Many2one('extender.length', string='Extender Lengths')

class Ring(models.Model):
    _name='ring'
    name=fields.Char(string='Name')
    under_gallery = fields.Selection([('yes', 'Yes'),('no', 'No'),], string='Under Gallery')
    shank_width=fields.Float(string='Shank Width')


class Necklace(models.Model):
    _name='necklace'
    name=fields.Char(string='Name')
    necklace_extender = fields.Selection([('yes', 'Yes'),('no', 'No'),], string='Extender')
    necklace_extender_length = fields.Float(string='Extender Length')

class Cuffs(models.Model):
    _name='cuffs'
    name=fields.Char(string='Name')
    cuffs_length=fields.Many2one('cuffs.length',string='Length')

class CuffsLength(models.Model):
    _name='cuffs.length'
    name=fields.Char(string='Length')

# class Bangles(models.Model):
#     _name='bangles'
#     name=fields.Char(string='Name')
#     bangle_length=fields.Many2one(string='Length')

