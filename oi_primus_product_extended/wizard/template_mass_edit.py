# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError
import pdb

class TemplateMassEdit(models.TransientModel):
    _name = 'template.mass.edit'
    _description = "Template Mass Edit"   
    
    @api.model
    def default_get(self, vals):
        context = self._context
        active_ids = context['active_ids']  
        res = super(TemplateMassEdit, self).default_get(vals)
        if active_ids:
            for rec in active_ids:                
                product = self.env['product.product'].search([('product_tmpl_id', 'in', active_ids)])      
        res['prod_ids'] = [(6, 0, product.ids)]
        return res  
    
    prod_ids = fields.Many2many('product.product', 'mass_edit_variant_rel', 'product_id', 'edit_id',string='Product Variant',)
    code_ids = fields.One2many('product.customer.code.line', 'mass_edit_id', "Lines")
                
    def create_product_codes(self):        
        context = self._context
        active_ids = context['active_ids']  
        if active_ids:
            for rec in active_ids:                
                product = self.env['product.template'].browse(rec)
                for rec in self.code_ids:
                    self.env['product.customer.code'].create({
                        'product_code': rec.product_code,
                        'product_name': rec.product_name,
                        'product_id': product.id,
                        'prod_id': rec.prod_id.id,
                        'partner_id': rec.partner_id.id,
                        })     
                                
                                
                                
class ProductCustomerCodeLine(models.TransientModel):
    _name = "product.customer.code.line"
    _description = "Add Code and Name of customer's product"
    _rec_name = 'product_code'

    product_code = fields.Char(string='Customer Product Code', help="""This
        customer's product code will be used when searching into a request for
        quotation.""")
    product_name = fields.Char(string='Customer Product Name', help="""This
        customer's product name will be used when searching into a request for
        quotation.""")
    product_id = fields.Many2one('product.template', string='Product Template',
        )
    prod_id = fields.Many2one('product.product', string='Product Variant',
        )
    partner_id = fields.Many2one('res.partner', string='Customer', required=True)
    mass_edit_id = fields.Many2one('template.mass.edit', 'Mass edit')
    
class BOMBulk(models.TransientModel):
    _name = 'product.bom.bulk'
    _description = "Bulk BOM"   
    
    bom_type = fields.Selection([('normal', 'Manufacture this product'), ('phantom', 'Kit')], "Type", default='normal')
    bulk_bom_ids = fields.One2many('product.bom.bulk.line', 'bulk_bom_id', "Bom" )
    
    def create_bom(self):
        context = self._context
        active_ids = context['active_ids']  
        bom = False
        if active_ids:
            for rec in active_ids:                
                product = self.env['product.product'].browse(rec)
                bom = False
                if product.bom_id:
                    bom = product.bom_id
                if not product.bom_id and product.bom_ids:
                    bom = product.bom_ids[0]
                if not bom:
                    bom = self.env['mrp.bom'].create({
                        'product_id': product.id,
                        'product_tmpl_id': product.product_tmpl_id.id,
                        'type': self.bom_type,
                        'company_id': self.env.company.id
                        })
                for line in self.bulk_bom_ids:
                    if bom.bom_line_ids:
                        exist = bom.bom_line_ids.filtered(lambda ptal: ptal.product_id.id == line.product_id.id)
                        if not exist:
                            bomline = self.env['mrp.bom.line'].create({
                                'pro_pro_id': product.id,
                                'bom_line_type_id': line.bom_line_type_id.id,
                                'sku_number': line.sku_number,
                                'product_id': line.product_id.id,
                                'product_qty': line.product_qty,
                                'product_uom_id': line.product_uom_id.id,
                                'sec_quantity': line.sec_quantity,
                                'min_weight': line.min_weight,
                                'unit_cost': line.unit_cost,
                                'total': line.total,
                                'provided_by': line.provided_by.id,
                                'bom_id': bom.id
                                })
                    if not bom.bom_line_ids:
                        bomline = self.env['mrp.bom.line'].create({
                            'pro_pro_id': product.id,
                            'bom_line_type_id': line.bom_line_type_id.id,
                            'sku_number': line.sku_number,
                            'product_id': line.product_id.id,
                            'product_qty': line.product_qty,
                            'product_uom_id': line.product_uom_id.id,
                            'sec_quantity': line.sec_quantity,
                            'min_weight': line.min_weight,
                            'unit_cost': line.unit_cost,
                            'total': line.total,
                            'provided_by': line.provided_by.id,
                            'bom_id': bom.id
                            })
                
                product.bom_id = bom.id
        return True
        
    
class BOMBulk(models.TransientModel):
    _name = 'product.bom.bulk.line'    
    
    pro_tmp_id = fields.Many2one('product.template', "Product Template",copy=False)
    pro_pro_id = fields.Many2one('product.product', "Product",copy=False)
    bom_line_type_id = fields.Many2one('bom.line.type', "Type")
    sku_number = fields.Char("SKU Number")
    unit_cost = fields.Float("Unit Cost")
    total = fields.Float("Total")  
    provided_by = fields.Many2one('res.partner', "Provided By") 
    min_weight = fields.Float("Min weight")
    prototype = fields.Char("Prototype")
    product_id = fields.Many2one('product.product', 'Description', required=False)
    sec_quantity = fields.Float("Secondary Qty")
    product_qty = fields.Float("Qty")
    product_uom_id = fields.Many2one('uom.uom', string="UOM")
    bulk_bom_id = fields.Many2one('product.bom.bulk', "Bulk")
    secondary_uom_id = fields.Many2one('uom.uom', string="Secondary UOM")
    
    @api.onchange('product_id')
    def onchange_product_id(self):
        if self.product_id:
            self.product_uom_id = self.product_id.uom_id.id
            self.sku_number = self.product_id.default_code
            self.unit_cost = self.product_id.standard_price
            self.secondary_uom_id = self.product_id.secondary_uom_id.id
            self.min_weight = self.product_id.min_weight
            self.total = self.unit_cost * self.product_qty
            self.provided_by = self.product_id.provided_by.id
    