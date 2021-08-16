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
    
    option = fields.Selection([('bom', 'BoM'), ('cost', 'Cost'),('markup', 'Markup'),('tag', 'Tag Multiplier')])    
    bom_type = fields.Selection([('normal', 'Manufacture this product'), ('phantom', 'Kit'),('subcontract', 'Subcontracting')], "Type", default='normal')
    bulk_bom_ids = fields.One2many('product.bom.bulk.line', 'bulk_bom_id', "Bom" )
    percentage = fields.Float("Percentage")
    multiplier = fields.Float('Multiplier')
    
    def create_bom(self):
        context = self._context
        active_ids = context['active_ids']  
        no_bom = []
        with_bom = []
        pq = 0.0
        if active_ids:
            products = self.env['product.product'].search([('id', 'in', active_ids)])
#             no_bom = products.filtered(lambda p: p.bom_id == False)
#             with_bom = products.filtered(lambda p: p.bom_id != False)   
            for rec in products:
                if rec.bom_id:
                    with_bom.append(rec)
            for wb in with_bom: 
                for line in self.bulk_bom_ids:
                    if wb.bom_id.bom_line_ids:
                        exist = wb.bom_id.bom_line_ids.filtered(lambda ptal: ptal.product_id.id == line.product_id.id)
                        if not exist:
                            bomline = self.env['mrp.bom.line'].create({
                                'pro_pro_id': wb.id,
                                'bom_line_type_id': line.bom_line_type_id.id,
                                'sku_number': line.sku_number,
                                'product_id': line.product_id.id,
                                'product_qty': line.product_qty,
                                'product_uom_id': line.product_uom_id.id,
                                'sec_quantity': line.sec_quantity,
                                'min_weight': line.min_weight,
                                'unit_cost': line.unit_cost,
                                'total': line.total,
                                'provided_by': line.provided_by,
                                'bom_id': wb.bom_id.id
                                })
                        if exist:
                            exist.bom_line_type_id = line.bom_line_type_id.id,
                            exist.write({'bom_line_type_id': line.bom_line_type_id.id,
                                         'product_qty': line.product_qty,
                                         'sec_quantity': line.sec_quantity,
                                         'unit_cost': line.unit_cost,
                                         'provided_by': line.provided_by})
                            exist.provided_by = line.provided_by
                    if not wb.bom_id.bom_line_ids:
                        bomline = self.env['mrp.bom.line'].create({
                            'pro_pro_id': wb.id,
                            'bom_line_type_id': line.bom_line_type_id.id,
                            'sku_number': line.sku_number,
                            'product_id': line.product_id.id,
                            'product_qty': line.product_qty,
                            'product_uom_id': line.product_uom_id.id,
                            'sec_quantity': line.sec_quantity,
                            'min_weight': line.min_weight,
                            'unit_cost': line.unit_cost,
                            'total': line.total,
                            'provided_by': line.provided_by,
                            'bom_id': wb.bom_id.id
                            })
            for rec in products:
                if not rec.bom_id:
                    no_bom.append(rec)
            for nb in no_bom:
                bom = self.env['mrp.bom'].create({
                        'product_id': nb.id,
                        'product_tmpl_id': nb.product_tmpl_id.id,
                        'type': self.bom_type,
                        'company_id': self.env.company.id
                        })
                nb.bom_id = bom.id
                for line in self.bulk_bom_ids:
                    bomline = self.env['mrp.bom.line'].create({
                                'pro_pro_id': nb.id,
                                'bom_line_type_id': line.bom_line_type_id.id,
                                'sku_number': line.sku_number,
                                'product_id': line.product_id.id,
                                'product_qty': line.product_qty,
                                'product_uom_id': line.product_uom_id.id,
                                'sec_quantity': line.sec_quantity,
                                'min_weight': line.min_weight,
                                'unit_cost': line.unit_cost,
                                'total': line.total,
                                'provided_by': line.provided_by,
                                'bom_id': bom.id
                                })
        return True
    
    def update_cost(self):
        context = self._context
        active_ids = context['active_ids']  
        no_bom = []
        with_bom = []
        perc_amt = 0.0
        if active_ids:
            products = self.env['product.product'].search([('id', 'in', active_ids)])
            for rec in products:
                if rec.standard_price > 0.0:
                    perc_amt = rec.standard_price * (self.percentage / 100)
                    rec.standard_price += perc_amt
                    
    def update_markup(self):
        context = self._context
        active_ids = context['active_ids']  
        no_bom = []
        with_bom = []
        perc_amt = markupval = 0.0
        if active_ids:
            products = self.env['product.product'].search([('id', 'in', active_ids)])
            for rec in products:
                if rec.product_price > 0.0:
                    markupval = (self.percentage/100) + 1
                    rec.markup_percentage = self.percentage
                    rec.markup_value = markupval
                    perc_amt = rec.product_price * markupval
                    rec.lst_price = perc_amt
                    
    def update_multipier(self):
        context = self._context
        active_ids = context['active_ids']  
        no_bom = []
        with_bom = []
        perc_amt = markupval = 0.0
        if active_ids:
            products = self.env['product.product'].search([('id', 'in', active_ids)])
            for rec in products:
                rec.lst_price = rec.lst_price * self.multiplier
        
    
class BOMBulk(models.TransientModel):
    _name = 'product.bom.bulk.line'    
    
    pro_tmp_id = fields.Many2one('product.template', "Product Template",copy=False)
    pro_pro_id = fields.Many2one('product.product', "Product",copy=False)
    bom_line_type_id = fields.Many2one('bom.line.type', "Type")
    sku_number = fields.Char("SKU Number")
    unit_cost = fields.Float("Unit Cost")
    total = fields.Float("Total")  
    provided_by = fields.Selection([('vendor','Vendor'),('factory','Factory')], "Provided By") 
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
            self.provided_by = self.product_id.provided_by
    
