# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools
from odoo.addons import decimal_precision as dp
from datetime import datetime, time
import pdb

import itertools
import logging
from collections import defaultdict

from odoo import api, fields, models, tools, _, SUPERUSER_ID
from odoo.exceptions import ValidationError, RedirectWarning, UserError
from odoo.osv import expression

_logger = logging.getLogger(__name__)

class Product_Master_Creation(models.Model):
    _inherit = 'product.template'
    
    bom_ids = fields.One2many('mrp.bom', 'product_tmpl_id', 'Bill of Materials', copy=True)
    products_types = fields.Selection([
        ('stone', 'Stone'),
        ('metal', 'Metal'),
        ('certification', 'Certification'),
        ('is_jewellery', 'Finished Jewelry'),
        ('finding','Findings'),
        ('mold', 'Mold'),
        ('design', 'Design Work')], string='Product type to map')
    diacolorgrade = fields.Many2one('stone.diacolorgrade',string='Dia Color Grade')
    diaclaritygrade = fields.Many2one('stone.diaclaritygrade',string='Dia Clarity Grade')
    gemstonecolorgrade=fields.Many2one('stone.gemstonecolorgrade', string='Gemstone Color Grade')
    gemstoneclaritygrade=fields.Many2one('stone.gemstoneclaritygrade', string='Gemstone Clarity Grade')
    dimension=fields.Char(string='Dimension')
    # stone_skew=fields.Many2one('stone.skew',string='Stone Skew')
    stone_class=fields.Many2one('stone.class',string='Stone Class')
    stone_name_id=fields.Many2one('stone.name', string='Stone Name')
    stone_shape_id=fields.Many2one('stone.shape',string='Shape')
    stone_type_id = fields.Many2one('stone.type',string='Type')
    size=fields.Char(string='Size')
    stone_color_id=fields.Many2one('stone.color',string='Color')
    stone_cutting_id=fields.Many2one('stone.cutting',string='Cutting')
    quality=fields.Char(string='Quality')

    stone_origin_id=fields.Many2one('res.country',string='Origin')
    treatment=fields.Many2one('stone.treatment',string='Treatment')
    certification_no=fields.Char(string='Certification No')
    certification_name=fields.Char(string='Certification Remarks')
    certification_lab=fields.Many2one('certification.lab',string='Certification Lab')
    certification_type = fields.Many2one('certification.type',string='Certification Type')
    min_weight=fields.Float(string='Min Weight', digits = (12,3))
    avg=fields.Float(string='Average', digits = (12,3), compute='_compute_avg', store=True)
    # vendor=fields.Many2one('res.partner',string='Vendor')
    finess=fields.Many2one('metal.finess',string='Fineness')
    plating=fields.Many2one('metal.plating',string='Plating')
    jfiness=fields.Many2one('metal.finess',string='J Fineness')
    jplating=fields.Many2one('metal.plating',string='J Plating')
    thickness=fields.Many2one('metal.thickness',string='M Thickness')
    plating_fitness_id=fields.Many2one('metal.platingfiness',string='M Plating Fineness')
    # vendor=fields.Many2one('vendor',string='Vendor')
    # uom=fields.Char(string='UOM')
    avg_cost=fields.Char(string='Average Cost')
    last_revised_cost=fields.Char(string='Last Revised Cost')
    # is_jewellery = fields.Boolean(string="Is a Jewellery")
    item_number = fields.Char(string='Item Number')
    status = fields.Selection([
        ('active', 'Active'),
        ('inactive', 'Inactive')], string='Status')
    style = fields.Char('Style')
    jtype = fields.Selection([('earring', 'Earring'),
                             ('pendant', 'Pendant'),
                             ('bracelet', 'Bracelet'),
                             ('ring', 'Ring'),
                             ('necklace', 'Necklace'),
                             ('brooche', 'Brooche'),
                             ('bangle', 'Bangle'),
                             ('cuff', 'Cuff')],'Jewelry Type')
    collection = fields.Many2one('collection','Collection')
    country_origin = fields.Many2one('res.country',string='Country of Manufacture')
    # vendor_id = fields.Many2one('res.partner','Vendor')
    vendor_model = fields.Many2one('res.partner','Vendor Model')
    tag_price_multiplier = fields.Float('Tag Price Multiplier')
    avg_cost = fields.Float('Average Cost')
    last_received_cost = fields.Float('Last Received Cost')
    received_date = fields.Char('Last Received Data & Bill')
    selling_price = fields.Float('Selling Price')
    markup = fields.Float('MarkUp(%)')
    customer_markup = fields.Float('Customer Markup(%)')
    trademark = fields.Many2one('trademark','Trademark')
    brand_id = fields.Many2one('brand.master','Brand')
    sub_brand_id = fields.Many2one('sub.brand.master','Sub Brand')
    child_sub_brand_id = fields.Many2one('child.sub.brand.master','Sub Sub Brand')
    dia=fields.Boolean(string='Is a Diamond', compute='enable_diamond', related='stone_name_id.diamond')
    gem=fields.Boolean(string='Is a Gemstone', compute='enable_gem', related='stone_name_id.gemstone')
    
    earring_drop_length = fields.Float("E Drop Length (Inch)")
    earring_drop_width = fields.Float("Drop Width (Inch)")
    ear_clasp = fields.Many2one('clasp', "Ear Clasp", domain="[('type','=','earring')]")
    inside_dia = fields.Float("Inside DIA (Inch)")
    
    chain = fields.Selection([('yes', 'Yes'), ('no', 'No')], "Chain")
    chain_length = fields.Float("Chain Length (Inch)")
    chain_clasp = fields.Many2one('clasp', "Chain Clasp", domain="[('type','=','pendant')]")
    chain_drop_length = fields.Float("C Drop Length (Inch)")
    chain_type = fields.Many2one('chain.type', "Chain Type")
    
    bracelet_length = fields.Float("Bracelet Length (Inch)")
    bracelet_clasp = fields.Many2one('clasp', "Bracelet Clasp", domain="[('type','=','bracelet')]")
    bracelet_safety = fields.Many2one('bracelet.safety', "Safety")
    bracelet_extender = fields.Selection([('yes', 'Yes'), ('no', 'No')], "B Extender")
    bracelet_extender_length = fields.Float("Br Extender Length (Inch)")
    
    undergallery = fields.Selection([('yes', 'Yes'), ('no', 'No')], "Undergallery")
    shank_width = fields.Float("Shank Width (Inch)")
    
    necklace_extender = fields.Selection([('yes', 'Yes'), ('no', 'No')], "N Extender")
    necklace_extender_length = fields.Float("N Extender Length (Inch)")
    
    cuff_length = fields.Float("Length (Inch)")
    
    bangle_length = fields.Float("Length (Inch)")
    bangle_clasp = fields.Many2one('clasp', "Bangle Clasp", domain="[('type','=','bangle')]")
    
    brooche_desc = fields.Text("Brooche Description")
    size_width = fields.Float("Size Width")
    size_length = fields.Float("Size length")
    rseq = fields.Char("R Seq")
    jewel_seq = fields.Integer("Jewel Seq", copy=False)
    birth_stone = fields.Selection([('january', 'January'),
                             ('february', 'February'),
                             ('march', 'March'),
                             ('april', 'April'),
                             ('may', 'May'),
                             ('june', 'June'),
                             ('july', 'July'),
                             ('august', 'August'),
                             ('september', 'September'),
                             ('october', 'October'),
                             ('november', 'November'),
                             ('december', 'December')],'Birth Stone')
    
    motif = fields.Many2many('motif', 'motif_product_rel', 'motif_id', 'product_id', "Motif")
    mold = fields.Selection(([('yes', 'Yes'), ('no', 'No')]),"Mold", default='no', readonly=True)
    certificate = fields.Selection(([('yes', 'Yes'), ('no', 'No')]),"Certificate", default='no', readonly=True)
    jewel_mold = fields.Selection(([('yes', 'Yes'), ('no', 'No')]),"Design Work", default='no')
    mold_ids = fields.One2many('mold', 'product_id', 'Design Molds')
    mold_type_id = fields.Many2one('mold.type',  'Mold Type')
    mold_part_id = fields.Many2one('mold.part',  'Mold Part (Not Used)')
    appraisal_value = fields.Float("Appraisal Value")
    appraisal = fields.Boolean("Appraisal")
    product_tags = fields.Many2many('product.tags', 'pro_product_tags_rel', 'pro_id', 'tag_id', "Tags")
    finding_type_id = fields.Many2one('finding.type',  'Finding Type')
    finding_subtype_id = fields.Many2one('finding.sub.type', "Sub Type")
    finding_fineness_id = fields.Many2one('metal.finess',  'F Fineness')
    finding_plating_id = fields.Many2one('metal.plating',  'F Plating')
    finding_Thickness_id = fields.Many2one('metal.thickness',  'F Thickness')
    finding_plating_thickness_id = fields.Many2one('metal.platingfiness',  'F Plating Fineness')
    finding_dimension = fields.Char("F Dimensions")
    cstone_name_id = fields.Many2one('stone.name', string='Stone')
    jstone_name_id = fields.Many2one('stone.name', string='Center stone')
    stone_weight = fields.Float("Stone Weight")
    certificate_date = fields.Date("Certificate Date")
    jsize = fields.Float("Stone Size")
    mold_line_part_id = fields.Many2one('mold.line.part',  'Mold Part')
    mold_dimension = fields.Char("M Dimension")
    mold_weight = fields.Float("Mold Weight")
    mold_material_id = fields.Many2one('mold.material', "Material")
    mold_condition = fields.Char("Condition")
    jewel_size = fields.Many2one('jewel.size',"Jewel Size")
    mold_product_ids = fields.Many2many('product.template','product_mold_rel', 'product_id', 'mold_id', "Mold Products")
    design_product_ids = fields.Many2many('product.template','product_design_rel', 'product_id', 'design_id', "Design Products")
    design_product_id = fields.Many2one('product.template', "Design Product")
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company)
    jewel_product_ids = fields.Many2many('product.template','product_jewel_rel', 'product_id', 'design_id', "Jewel Products")
    qty_available = fields.Float('Quantity On Hand', compute='_compute_quantities', search='_search_qty_available', compute_sudo=False, digits=(12,3))
    ir_attachment_ids = fields.One2many('ir.attachment', 'product_tmpl_id', "Files")
    center_color_stone_id = fields.Many2one('center.color.stone', "Center Stone Color")
    provided_by = fields.Selection([('vendor','Vendor'),('factory','Factory')], "Provided By") 
    stone_applicable = fields.Boolean("Stone Applicable", default=True)
    certificate_product_ids = fields.Many2many('product.product','product_certificates_rel', 'product_id', 'certificate_id', "Certificate Products")
    certificate_origin_product_ids = fields.Many2many('product.product','product_certificates_origin_rel', 'product_id', 'certificate_id', "Certificate Origin Products")
    jtypes = fields.Many2one('jewel.tags', "Jewel Type")
    
    @api.onchange('jtype')
    def onchange_jtype(self):
        jt = False
        if self.jtype:
            if self.jtype == 'earring':                
                jt = self.env['jewel.tags'].search([('name', '=', 'Earring')])
            if self.jtype == 'pendant':                
                jt = self.env['jewel.tags'].search([('name', '=', 'Pendant')])
            if self.jtype == 'bracelet':                
                jt = self.env['jewel.tags'].search([('name', '=', 'Bracelet')])
            if self.jtype == 'ring':                
                jt = self.env['jewel.tags'].search([('name', '=', 'Ring')])
            if self.jtype == 'necklace':                
                jt = self.env['jewel.tags'].search([('name', '=', 'Necklace')])
            if self.jtype == 'brooche':                
                jt = self.env['jewel.tags'].search([('name', '=', 'Brooche')])
            if self.jtype == 'bangle':                
                jt = self.env['jewel.tags'].search([('name', '=', 'Bangle')])
            if self.jtype == 'bangle':                
                jt = self.env['jewel.tags'].search([('name', '=', 'Bangle')])
            if self.jtype == 'cuff':                
                jt = self.env['jewel.tags'].search([('name', '=', 'Cuff')])
            self.jtypes =  jt
    
    @api.onchange('default_code')
    def onchange_default_code(self):
        if self.default_code:
            self.barcode =  self.default_code
    
    @api.depends('qty_available', 'secondary_qty')
    def _compute_avg(self):
        for rec in self:
            if rec.secondary_qty != 0.0:
                rec.avg = rec.qty_available / rec.secondary_qty
        
    
    @api.onchange('mold_part_id')
    def onchange_mold_part_id(self):
        mold_list = []
        if self.mold_part_id:
            if self.mold_ids:
                for rec in self.mold_ids:
#                     rec.sudo().unlink()
                    rec.product_id = False
            x = range(self.mold_part_id.parts)
            for n in x:                
                mold = self.env['mold'].create(
                            {
                             'name': '/',
                             'product_id': self.id,
                             })
                mold_list.append(mold.id)
                self.mold_ids = [(6,0, mold_list)]
                
    @api.onchange('design_product_id')
    def onchange_design_product_id(self):
        mold_list = []
        if self.design_product_id:
            for rec in self.mold_ids:
#                     rec.sudo().unlink()
                rec.product_id = False
            if self.design_product_id.mold_product_ids:
                for rec in self.design_product_id.mold_product_ids:
                    mold = self.env['mold'].create(
                                {
                                'mold_product_id': rec.id,
                                'mold_line_part_id' : rec.mold_line_part_id.id,
                                'mold_dimension': rec.mold_dimension,
                                'mold_weight': rec.mold_weight,
                                'mold_material_id': rec.mold_material_id.id,
                                'mold_condition': rec.mold_condition,
                                'name': rec.default_code, 
                                'product_id': self.id,
                                 })
                    mold_list.append(mold.id)
                self.mold_ids = [(6,0, mold_list)]
#             self.products_types = self.design_product_id.products_types
            self.jtype = self.design_product_id.jtype
            self.jfiness = self.design_product_id.jfiness.id
            self.jplating = self.design_product_id.jplating.id
            self.jewel_size = self.design_product_id.jewel_size.id
            self.motif = [(6,0, self.design_product_id.motif.ids)]
            self.collection = self.design_product_id.collection.id
            self.trademark = self.design_product_id.trademark.id
            self.jstone_name_id = self.design_product_id.jstone_name_id.id
            self.country_origin = self.design_product_id.country_origin.id
            self.brand_id = self.design_product_id.brand_id.id
            self.sub_brand_id = self.design_product_id.sub_brand_id.id
            self.child_sub_brand_id = self.design_product_id.child_sub_brand_id.id
            self.earring_drop_length = self.design_product_id.earring_drop_length
            self.earring_drop_width = self.design_product_id.earring_drop_width
            self.ear_clasp = self.design_product_id.ear_clasp.id
            self.inside_dia = self.design_product_id.inside_dia
            self.product_tags = [(6,0, self.design_product_id.product_tags.ids)]
            self.size = self.design_product_id.size
            self.size_length = self.design_product_id.size_length
            self.size_width = self.design_product_id.size_width
            self.jsize = self.design_product_id.jsize
            self.chain = self.design_product_id.chain
            self.chain_length = self.design_product_id.chain_length
            self.chain_clasp = self.design_product_id.chain_clasp.id
            self.chain_drop_length = self.design_product_id.chain_drop_length
            self.chain_type = self.design_product_id.chain_type.id
            self.birth_stone = self.design_product_id.birth_stone
            self.undergallery = self.design_product_id.undergallery
            self.dimension = self.design_product_id.dimension
            self.min_weight = self.design_product_id.min_weight
            
    
    @api.depends('dia', 'products_types')
    def enable_diamond(self):
        if self.stone_name_id.diamond == True:
            self.dia = True
        else:
            self.dia = False
        if self.products_types != 'stone':
            self.dia = False

    @api.depends('gem', 'products_types')
    def enable_gem(self):
        if self.stone_name_id.gemstone == True:
            self.gem = True
        else:
            self.gem = False
        if self.products_types != 'stone':
            self.dia = False
            
    @api.onchange('stone_name_id', 'stone_shape_id', 'stone_cutting_id', 'size_length', 'size_width')
    def onchange_stone_name_id(self):
        sshape = scut = sname = ''
        if not self.rseq:
            self.rseq =  ''  
        stone_rec = self.env['product.template'].search_count([('products_types', '=', 'stone'),('stone_name_id', '=', self.stone_name_id.id),
                                                               ('stone_shape_id', '=', self.stone_shape_id.id),('stone_cutting_id', '=', self.stone_cutting_id.id),
                                                               ('size_width', '=', self.size_width),('size_length', '=', self.size_length)])
        stone_rec += 1
        if stone_rec < 10:
            self.rseq = '0' + str(stone_rec)
        else:
            self.rseq =  str(stone_rec)            
        if self.stone_name_id:
            self.birth_stone = self.stone_name_id.birth_stone
            sname = self.stone_name_id.code
        if self.stone_shape_id:
            sshape = self.stone_shape_id.code
        if self.stone_cutting_id:
            scut = self.stone_cutting_id.code 
        length = width = ''
        if self.size_length < 10:
            length = '0'+ str(self.size_length)
        else:
            length = str(self.size_length)
        if len(length) == 4:
            length = length + '0'
        
        if self.size_width < 10:
            width = '0'+ str(self.size_width)            
        else:
            width = str(self.size_width)
        if len(width) == 4:
            width = width + '0'
            
        sku = str(sname) + length + width + str(sshape) + str(scut) + self.rseq
        sku = sku.replace('False', '')
        sku = sku.replace('.','')
        self.default_code = sku
            
    @api.onchange('stone_name_id', 'stone_shape_id', 'stone_cutting_id', 'size_length', 'size_width', 'gemstonecolorgrade', 'gemstoneclaritygrade', 'dia', 'gem', 'diacolorgrade', 'diaclaritygrade')
    def onchange_stone(self):
        product = ''
        if self.products_types == 'stone':
            length = width = ''
            if self.size_length < 10:
                length = '0'+ str(self.size_length)
            else:
                length = str(self.size_length)
            if len(length) == 4:
                length = length + '0'
            
            if self.size_width < 10:
                width = '0'+ str(self.size_width)            
            else:
                width = str(self.size_width)
            if len(width) == 4:
                width = width + '0'
            product += length + 'x' + width + 'mm' 
            if self.stone_shape_id:
                product += ' ' + self.stone_shape_id.name 
            if self.stone_name_id:
               product += ' ' + self.stone_name_id.name 
            if self.stone_cutting_id:
               product += ' ' + self.stone_cutting_id.name 
            if self.gem:
                if self.gemstonecolorgrade and self.gemstoneclaritygrade:
                    product += ' ' + self.gemstonecolorgrade.name + '/' + self.gemstoneclaritygrade.name 
                else:
                    if self.gemstonecolorgrade:
                        product += ' ' + self.gemstonecolorgrade.name 
                    if self.gemstoneclaritygrade:
                        product+= ' ' + self.gemstoneclaritygrade.name 
            if self.dia:
                if self.diacolorgrade and self.diaclaritygrade:
                    product += ' ' + self.diacolorgrade.name + '/' + self.diaclaritygrade.name
                else:
                    if self.diacolorgrade:
                        product += ' ' + self.diacolorgrade.name 
                    if self.diaclaritygrade:
                        product += ' ' +self.diaclaritygrade.name
#             self.name = product
            
    @api.onchange('products_types')
    def onchange_products_types(self):
        sshape = scut = sname = ''
        fineness = plating = ''
        if not self.rseq:
            self.rseq =  ''  
        if self.products_types != 'stone':
            self.stone_name_id = False
        if self.products_types != 'is_jewellery':
            self.jtype = None
        if self.products_types == 'stone':
            uom = self.env['uom.uom'].search([('name', '=', 'Ctw')],limit=1)
            self.tracking = 'lot'
            if uom:
                self.uom_id = uom.id
            if self.stone_name_id:
                sname = self.stone_name_id.code
            if self.stone_shape_id:
                sshape = self.stone_shape_id.code
            if self.stone_cutting_id:
                scut = self.stone_cutting_id.code 
            length = width = ''
            if self.size_length < 10:
                length = '0'+ str(self.size_length)
            else:
                length = str(self.size_length)
                
            if len(length) == 4:
                length = length + '0'
            
            if self.size_width < 10:
                width = '0'+ str(self.size_width)
            else:
                width = str(self.size_width)
                
            if len(width) == 4:
                width = width + '0'
            sku = str(sname) + length + width + str(sshape) + str(scut) + self.rseq
            sku = sku.replace('False', '')
            sku = sku.replace('.','')
            self.default_code = sku
            self.finess = False
            self.plating = False
            self.certification_lab = False
            self.certification_type = False
            self.certification_no = False
        if self.products_types == 'metal':
            uom = self.env['uom.uom'].search([('name', '=', 'Grams')],limit=1)
            if uom:
                self.uom_id = uom.id
            if self.finess:
                fineness = self.finess.code
            if self.plating:
                plating = self.plating.code            
            sku = 'M' + str(fineness) + str(plating) + self.rseq
            sku = sku.replace('False', '')
            sku = sku.replace('.','')
            self.default_code = sku
            self.certification_lab = False
            self.certification_type = False
            self.certification_no = False
            self.stone_name_id = False
            self.stone_cutting_id = False
            self.stone_shape_id = False
        if self.products_types == 'certification':
            uom = self.env['uom.uom'].search([('name', '=', 'Pcs')],limit=1)
            if uom:
                self.uom_id = uom.id
            lab = type = no = ''
            if self.certification_lab.code:
                lab = self.certification_lab.code
            if self.certification_type.code:
                type = self.certification_type.code
            if self.certification_no:
                no = self.certification_no[-5:] 
            
            sku = str(lab) + str(type) + str(no)
            sku = sku.replace('False', '')
            sku = sku.replace('.','')
            self.default_code = sku
            self.finess = False
            self.plating = False
            self.stone_name_id = False
            self.stone_cutting_id = False
            self.stone_shape_id = False
        if self.products_types == 'is_jewellery':
            uom = self.env['uom.uom'].search([('name', '=', 'Pcs')],limit=1)
            if uom:
                self.uom_id = uom.id
        if self.products_types == 'finding':
            uom = self.env['uom.uom'].search([('name', '=', 'Pcs')],limit=1)
            if uom:
                self.uom_id = uom.id
        if self.products_types == 'mold':
            uom = self.env['uom.uom'].search([('name', '=', 'Pcs')],limit=1)
            if uom:
                self.uom_id = uom.id
            
    @api.onchange('finess', 'plating', 'plating_fitness_id', 'thickness')
    def onchange_finess(self):   
        fineness = plating = ''
        if not self.rseq:
            self.rseq =  ''   
        if self.finess:
            fineness = self.finess.code
        if self.plating:
            plating = self.plating.code             
        sku = 'M' + str(fineness) + str(plating) + self.rseq
        sku = sku.replace('False', '')
        sku = sku.replace('.','')
        self.default_code = sku
        pfiness = fineness = plating = thick = ''
        if self.finess:
            fineness = self.finess.name
        if self.plating_fitness_id:
            pfiness = self.plating_fitness_id.name
        if self.plating:
            plating = self.plating.name
        if self.thickness:
            thick = self.thickness.name
#         self.name = fineness + ' ' + pfiness + ' ' + plating + ' ' +thick
        
    @api.onchange('jplating')
    def onchange_jplating(self):
        if self.jplating:
            new_lines = []
            attribute = self.env['product.attribute'].search([('name', '=', 'Plating')])
            exist = self.attribute_line_ids.filtered(lambda ptal: ptal.attribute_id.id == attribute.id)
            if not exist:
                att_val = self.env['product.attribute.value'].search([('name', '=', self.jplating.name),('attribute_id', '=', attribute.id)])
                new_lines.append((0, 0, dict(
                        attribute_id = attribute.id,
                        value_ids=att_val.ids)
                    ))
                if new_lines:
                    self.update(dict(attribute_line_ids=new_lines))
            if exist:
                att_val = self.env['product.attribute.value'].search([('name', '=', self.jplating.name),('attribute_id', '=', attribute.id)])
                exist.value_ids = [(6,0,[att_val.id])]
                
    @api.onchange('jfiness')
    def onchange_jfiness1(self):
        if self.jfiness:
            new_lines = []
            attribute = self.env['product.attribute'].search([('name', '=', 'Fineness')])
            exist = self.attribute_line_ids.filtered(lambda ptal: ptal.attribute_id.id == attribute.id)
            if not exist:
                att_val = self.env['product.attribute.value'].search([('name', '=', self.jfiness.name),('attribute_id', '=', attribute.id)])
                new_lines.append((0, 0, dict(
                        attribute_id = attribute.id,
                        value_ids=att_val.ids)
                    ))
                if new_lines:
                    self.update(dict(attribute_line_ids=new_lines))
            if exist:
                att_val = self.env['product.attribute.value'].search([('name', '=', self.jfiness.name),('attribute_id', '=', attribute.id)])
                exist.value_ids = [(6,0,[att_val.id])]
                
    @api.onchange('jstone_name_id')
    def onchange_jstone_name_id(self):
        if self.jstone_name_id:
            new_lines = []
            attribute = self.env['product.attribute'].search([('name', '=', 'Center stone')])
            exist = self.attribute_line_ids.filtered(lambda ptal: ptal.attribute_id.id == attribute.id)
            if not exist:
                att_val = self.env['product.attribute.value'].search([('name', '=', self.jstone_name_id.name),('attribute_id', '=', attribute.id)])
                new_lines.append((0, 0, dict(
                        attribute_id = attribute.id,
                        value_ids=att_val.ids)
                    ))
                if new_lines:
                    self.update(dict(attribute_line_ids=new_lines))
            if exist:
                att_val = self.env['product.attribute.value'].search([('name', '=', self.jstone_name_id.name),('attribute_id', '=', attribute.id)])
                exist.value_ids = [(6,0,[att_val.id])]
                
    @api.onchange('jewel_size')
    def onchange_jewel_size(self):
        if self.jewel_size:
            new_lines = []
            attribute = self.env['product.attribute'].search([('name', '=', 'Jewel Size')])
            exist = self.attribute_line_ids.filtered(lambda ptal: ptal.attribute_id.id == attribute.id)
            if not exist:
                att_val = self.env['product.attribute.value'].search([('name', '=', self.jewel_size.name),('attribute_id', '=', attribute.id)])
                new_lines.append((0, 0, dict(
                        attribute_id = attribute.id,
                        value_ids=att_val.ids)
                    ))
                if new_lines:
                    self.update(dict(attribute_line_ids=new_lines))
            if exist:
                att_val = self.env['product.attribute.value'].search([('name', '=', self.jewel_size.name),('attribute_id', '=', attribute.id)])
                exist.value_ids = [(6,0,[att_val.id])]
                
    @api.onchange('center_color_stone_id')
    def onchange_center_color_stone_id(self):
        if self.center_color_stone_id:
            new_lines = []
            attribute = self.env['product.attribute'].search([('name', '=', 'Center Stone Color')])
            exist = self.attribute_line_ids.filtered(lambda ptal: ptal.attribute_id.id == attribute.id)
            if not exist:
                att_val = self.env['product.attribute.value'].search([('name', '=', self.center_color_stone_id.name),('attribute_id', '=', attribute.id)])
                new_lines.append((0, 0, dict(
                        attribute_id = attribute.id,
                        value_ids=att_val.ids)
                    ))
                if new_lines:
                    self.update(dict(attribute_line_ids=new_lines))
            if exist:
                att_val = self.env['product.attribute.value'].search([('name', '=', self.center_color_stone_id.name),('attribute_id', '=', attribute.id)])
                exist.value_ids = [(6,0,[att_val.id])]
            
    @api.onchange('jfiness', 'jtype', 'jplating','jewel_size', 'jstone_name_id')
    def onchange_jfiness(self):   
        fineness = plating = jsize = sname = ''
        if not self.rseq:
            self.rseq = ''
        if self.products_types in ['is_jewellery', 'design']:
            self.style = False
            self.default_code = False
            new_lines = []
            if self.jfiness:
                fineness = self.jfiness.jewel_code
            if self.jplating:
                plating = self.jplating.jewel_code
            Jewel = ''
            if self.jtype == 'ring':
                Jewel = 'R'
            if self.jtype == 'earring':
                Jewel = 'E'
            if self.jtype == 'pendant':
                Jewel = 'P'
            if self.jtype == 'bracelet':
                Jewel = 'B'
            if self.jtype == 'necklace':
                Jewel = 'N'
            if self.jtype == 'brooche':
                Jewel = 'BR'
            if self.jtype == 'bangle':
                Jewel = 'BA'
            if self.jtype == 'cuff':
                Jewel = 'C'
            if self.jewel_size:
                jsize = self.jewel_size.code
            if self.jstone_name_id:
                sname = self.jstone_name_id.code
            year = str(datetime.now().year)[-2:]
            sku = Jewel + sname + str(fineness) + str(plating) + str(year) + self.rseq + jsize
            sku = sku.replace('False', '')
            sku = sku.replace('.','')
            self.default_code = sku   
                  
            
            
    @api.onchange('certification_lab', 'certification_type', 'certification_no', 'stone_weight', 'cstone_name_id')
    def onchange_certification_lab(self):   
        lab = type = no = cert_rec = ''
        product = ''
        
        if self.products_types == 'certification':
            cert_rec = self.env['product.template'].search_count([('products_types', '=', 'certification'),('certification_lab', '=', self.certification_lab.id),
                                                                 ('certification_type', '=', self.certification_type.id),
                                                                 ('certification_no', '=', self.certification_no)])
            if cert_rec + 1 < 10:
                    self.rseq = '0' + str(cert_rec)
            else:
                self.rseq =  str(cert_rec)
            if self.certification_lab:
                lab = self.certification_lab.code
            if self.certification_type:
                type = self.certification_type.code
            if self.certification_no:
                no = self.certification_no[-5:]        
            sku = str(lab) + str(type) + str(no) + self.rseq
            sku = sku.replace('False', '')
            sku = sku.replace('.','')
            self.default_code = sku  
            if self.certification_type:
                if self.certification_type.name == 'Appraisal':
                    self.appraisal = True
                else:
                    self.appraisal = False
            weight = ''
            if self.stone_weight < 10:
                weight = '0'+ str(self.stone_weight)
            else:
                weight = str(self.stone_weight)
                
            if len(weight) == 4:
                weight = weight + '0'        
            if weight:
                product += weight + ' Ctw'
            if self.cstone_name_id:
                product += ' '+ self.cstone_name_id.name
            if self.certification_lab:
                product += ' ' + self.certification_lab.code
            if self.certification_type:
                product += ' ' + self.certification_type.name
#             self.name = product   
    
    @api.onchange('finding_type_id', 'finding_subtype_id', 'finding_fineness_id', 'finding_plating_id', 'finding_Thickness_id', 'finding_plating_thickness_id')
    def onchange_finding(self):
        
        if not self.rseq:
            self.rseq = ''
        year = str(datetime.now().year)[-2:]
        type = find = stype = finess = pfine = plating = thick = ''
        find = 'F'
        if self.finding_type_id:
            find += self.finding_type_id.code + year + self.rseq
            self.default_code = find
        if self.finding_type_id:
            type = self.finding_type_id.code  
        if self.finding_subtype_id:
            stype = self.finding_subtype_id.name
        if self.finding_fineness_id:
            finess = self.finding_fineness_id.name
        if self.finding_plating_id:
            plating = self.finding_plating_id.name
        if self.finding_Thickness_id:
            thick = self.finding_Thickness_id.name
        if self.finding_plating_thickness_id:
            pfine = self.finding_plating_thickness_id.name
#         self.name = stype + ' ' + type + ' in ' + ' ' + finess + ' ' + pfine + ' ' + plating + ' ' + thick
    
    @api.onchange('mold_line_part_id', 'mold_material_id')
    def onchange_mold(self):
        mlp = mat = ''
        if self.products_types == 'mold':
            if self.mold_line_part_id:
                mlp = self.mold_line_part_id.name
            if self.mold_material_id:
                mat = self.mold_material_id.name            
#             self.name = mlp + ' ' + mat + ' ' + 'Mold'
    
    @api.model
    def create(self, vals):
        fineness = plating = ''
        sshape = scut = sname = ''
        product = ''
        res = super(Product_Master_Creation, self).create(vals)
        res.rseq = ''
        year = str(datetime.now().year)[-2:]
        if res.products_types == 'stone':
            sname = res.stone_name_id.code
            sshape = res.stone_shape_id.code
            scut = res.stone_cutting_id.code
            stone_rec = self.env['product.template'].search_count([('products_types', '=', 'stone'),('stone_name_id', '=', res.stone_name_id.id),
                                                                   ('stone_shape_id', '=', res.stone_shape_id.id),('stone_cutting_id', '=', res.stone_cutting_id.id),
                                                                   ('size_width', '=', res.size_width),('size_length', '=', res.size_length)])
            if stone_rec < 10:
                res.rseq = '0' + str(stone_rec)
            else:
                res.rseq =  str(stone_rec)
            length = width = ''
            if res.size_length < 10:
                length = '0'+ str(res.size_length)
            else:
                length = str(res.size_length)
                
            if len(length) == 4:
                length = length + '0'
            
            if res.size_width < 10:
                width = '0'+ str(res.size_width)
            else:
                width = str(res.size_width)
                
            if len(width) == 4:
                width = width + '0'
            
            sku = str(sname) + length + width + str(sshape) + str(scut) + res.rseq
            sku = sku.replace('False', '')
            sku = sku.replace('.','')
            res.default_code = sku
        if res.products_types == 'metal':
            fineness = res.finess.code
            plating = res.plating.code
            metal_rec = self.env['product.template'].search_count([('products_types', '=', 'metal'),('finess','=',res.finess.id),('plating','=',res.plating.id)])
            if metal_rec < 10:
                res.rseq = '0' + str(metal_rec)
            else:
                res.rseq =  str(metal_rec)
            sku = 'M' + str(fineness) + str(plating) + res.rseq
            sku = sku.replace('False', '')
            sku = sku.replace('.','')
            res.default_code = sku
            pfiness = fineness = plating = thick = ''
            if res.finess:
                fineness = res.finess.name
            if res.plating_fitness_id:
                pfiness = res.plating_fitness_id.name
            if res.plating:
                plating = res.plating.name
            if res.thickness:
                thick = res.thickness.name
#             res.name = fineness + ' ' + pfiness + ' ' + plating + ' ' +thick
            
        if res.products_types == 'certification':
            lab = ''
            type = ''
            no = ''
            if res.certification_lab.code:
                lab = res.certification_lab.code
            if res.certification_type.code:
                type = res.certification_type.code
            if res.certification_no:
                no = res.certification_no[-5:]
            cert_rec = self.env['product.template'].search_count([('products_types', '=', 'certification'),('certification_lab', '=', res.certification_lab.id),
                                                                 ('certification_type', '=', res.certification_type.id),
                                                                 ('certification_no', '=', res.certification_no)])
            if cert_rec + 1 < 10:
                res.rseq = '0' + str(cert_rec)
            else:
                res.rseq =  str(cert_rec)
            sku = str(lab) + str(type) + str(no) + res.rseq
            sku = sku.replace('False', '')
            sku = sku.replace('.','')
            res.default_code = sku
            weight = ''
            if res.stone_weight < 10:
                weight = '0'+ str(res.stone_weight)
            else:
                weight = str(res.stone_weight)
                
            if len(weight) == 4:
                weight = weight + '0'        
            if weight:
                product += weight + ' Ctw'
            if res.cstone_name_id:
                product += ' '+ res.cstone_name_id.name
            if res.certification_lab:
                product += ' ' + res.certification_lab.code
            if res.certification_type:
                product += ' ' + res.certification_type.name
#             res.name = product   
        if res.products_types == 'stone':
            product = ''
            length = width = ''
            if res.size_length < 10:
                length = '0'+ str(res.size_length)
            else:
                length = str(res.size_length)
            if len(length) == 4:
                length = length + '0'
            
            if res.size_width < 10:
                width = '0'+ str(res.size_width)            
            else:
                width = str(res.size_width)
            if len(width) == 4:
                width = width + '0'
            product += length + 'x' + width + 'mm' 
            if res.stone_shape_id:
                product += ' ' + res.stone_shape_id.name 
            if res.stone_name_id:
               product += ' ' + res.stone_name_id.name 
            if res.stone_cutting_id:
               product += ' ' + res.stone_cutting_id.name 
            if res.gem:                
                if res.gemstonecolorgrade and res.gemstoneclaritygrade:
                    product+= ' ' + res.gemstonecolorgrade.name + '/'  + res.gemstoneclaritygrade.name
                else:
                    if res.gemstonecolorgrade:
                        product += ' ' + res.gemstonecolorgrade.name 
                    if res.gemstoneclaritygrade:
                        product+= ' ' + res.gemstoneclaritygrade.name 
                
            if res.dia:
                if res.diacolorgrade and res.diaclaritygrade:
                    product += ' ' + res.diacolorgrade.name + '/' + res.diaclaritygrade.name
                else:                    
                    if res.diacolorgrade:
                        product += ' ' + res.diacolorgrade.name
                    if res.diaclaritygrade:
                        product += ' ' +res.diaclaritygrade.name
#             res.name = product
        if res.products_types == 'mold':
            if not res.rseq:
                res.rseq = ''
#             seq = self.env['ir.sequence'].next_by_code('mold')
            mold_rec = self.env['product.template'].search_count([('products_types', '=', 'mold')])
            if mold_rec < 10:
                res.rseq = '00' + str(mold_rec)
            if mold_rec >= 10:
                res.rseq = '0' + str(mold_rec)
            if mold_rec  >= 100:
                res.rseq =  str(mold_rec)
            Jewel = mlp = mat = ''            
            if res.mold_line_part_id:
                mlp = res.mold_line_part_id.name
            year = str(datetime.now().year)[-2:]
            if res.mold_material_id:
                mat = res.mold_material_id.name  
                Jewel = res.mold_line_part_id.code          
            res.default_code = 'M' + Jewel + year + res.rseq
#             res.name = mlp + ' ' + mat + ' ' + ' Mold'
        if res.products_types == 'is_jewellery':
            if res.jewel_mold == 'no' and 'style' in vals and vals['style'] == False:
#                 seq = self.env['ir.sequence'].next_by_code('style')
                seq = ''
                seqrec = self.env['product.template'].search([('jtype', '=', res.jtype),('jfiness', '=', res.jfiness.id),
                                                              ('jplating', '=', res.jplating.id),('jstone_name_id', '=', res.jstone_name_id.id),
                                                              ('jewel_size', '=', res.jewel_size.id),('center_color_stone_id', '=', res.center_color_stone_id.id)])
                seq = len(seqrec) + 1
                res.jewel_seq = seq
                if int(seq) < 10:
                    seq = '00' + str(seq)
                if int(seq) < 100:
                    seq = '0' + str(seq)
                Jewel = jsize = ''
                if res.jtype == 'ring':
                    Jewel = 'R'
                if res.jtype == 'earring':
                    Jewel = 'E'
                if res.jtype == 'pendant':
                    Jewel = 'P'
                if res.jtype == 'bracelet':
                    Jewel = 'B'
                if res.jtype == 'necklace':
                    Jewel = 'N'
                if res.jtype == 'brooche':
                    Jewel = 'BR'
                if res.jtype == 'bangle':
                    Jewel = 'BA'
                if res.jtype == 'cuff':
                    Jewel = 'C'
                year = str(datetime.now().year)[-2:]
                res.style = Jewel + year + seq            
            sname = fineness = plating = ''
            sname = res.jstone_name_id.code
            fineness = res.jfiness.jewel_code
            plating = res.jplating.jewel_code
            if res.jewel_size:
                jsize = res.jewel_size.code
            else:
                jsize = ''
            jewel_rec = self.env['product.template'].search_count([('jtype', '=', res.jtype),('jfiness', '=', res.jfiness.id),
                                                              ('jplating', '=', res.jplating.id),('jstone_name_id', '=', res.jstone_name_id.id),
                                                              ('jewel_size', '=', res.jewel_size.id),('center_color_stone_id', '=', res.center_color_stone_id.id)])
            if jewel_rec < 10:
                res.rseq = '0' + str(jewel_rec)
            else:
                res.rseq =  str(jewel_rec)
            Jewel = ''
            if res.jtype == 'ring':
                Jewel = 'R'
            if res.jtype == 'earring':
                Jewel = 'E'
            if res.jtype == 'pendant':
                Jewel = 'P'
            if res.jtype == 'bracelet':
                Jewel = 'B'
            if res.jtype == 'necklace':
                Jewel = 'N'
            if res.jtype == 'brooche':
                Jewel = 'BR'
            if res.jtype == 'bangle':
                Jewel = 'BA'
            if res.jtype == 'cuff':
                Jewel = 'C'
            year = str(datetime.now().year)[-2:]
            if not sname:
                sname = ''
            sku = Jewel + sname + str(fineness) + str(plating) + str(year) + res.rseq + jsize
            sku = sku.replace('False', '')
            sku = sku.replace('.','')
            res.default_code = sku
        if res.products_types == 'design':
#             seq = self.env['ir.sequence'].next_by_code('style')
            seq = ''
            seqrec = self.env['product.template'].search([('jtype', '=', res.jtype)])
            seq = len(seqrec) + 1
            res.jewel_seq = seq
            if int(seq) < 10:
                seq = '00' + str(seq)
            if int(seq) < 100:
                seq = '0' + str(seq)
            Jewel = jsize = ''
            if res.jtype == 'ring':
                Jewel = 'R'
            if res.jtype == 'earring':
                Jewel = 'E'
            if res.jtype == 'pendant':
                Jewel = 'P'
            if res.jtype == 'bracelet':
                Jewel = 'B'
            if res.jtype == 'necklace':
                Jewel = 'N'
            if res.jtype == 'brooche':
                Jewel = 'BR'
            if res.jtype == 'bangle':
                Jewel = 'BA'
            if res.jtype == 'cuff':
                Jewel = 'C'
            year = str(datetime.now().year)[-2:]
            res.default_code = Jewel + year + seq
        if res.products_types == 'finding':            
            type = find = stype = finess = pfine = plating = thick = ''
            if res.finding_type_id:
                type = res.finding_type_id.code            
            find_rec = self.env['product.template'].search_count([('products_types', '=', 'finding'), ('finding_type_id', '=', res.finding_type_id.id)])
            if find_rec < 10:
                res.rseq = '0' + str(find_rec)
            else:
                res.rseq =  str(find_rec)
            res.default_code  = 'F' + type + year + res.rseq 
            if res.finding_subtype_id:
                stype = res.finding_subtype_id.name
            if res.finding_fineness_id:
                finess = res.finding_fineness_id.name
            if res.finding_plating_id:
                plating = res.finding_plating_id.name
            if res.finding_Thickness_id:
                thick = res.finding_Thickness_id.name
            if res.finding_plating_thickness_id:
                pfine = res.finding_plating_thickness_id.name
#             res.name = stype + ' '+type + ' in ' + ' ' + finess + ' ' + pfine + ' ' + plating + ' ' + thick
        if 'design_product_id' in vals and vals['design_product_id'] != False:
            if res.design_product_id.bom_ids:
                for bom in res.design_product_id.bom_ids:
                    newbom = bom.copy()
                    newbom.product_tmpl_id = res.id
            if res.design_product_id:
                res.design_product_id.jewel_product_ids = [(4,res.id)]
        if res.products_types == 'mold':
            if 'design_product_ids' in vals:
                if res.design_product_ids:
                    for rec in res.design_product_ids:
                        rec.mold_product_ids = [(4,res.id)]
                        rec.mold = 'yes'
        if res.default_code:
            res.barcode = res.default_code
        return res
    
    def write(self, vals):        
        result = super(Product_Master_Creation, self).write(vals)
        for pt in self:
            if 'name' in vals:
                if pt.product_variant_ids:
                    for va in pt.product_variant_ids:
                        va.name = pt.name
            if 'design_product_id' in vals:
                if pt.design_product_id.bom_ids:
                    for bom in pt.design_product_id.bom_ids:
                        newbom = bom.copy()
                        newbom.product_tmpl_id = pt.id
    
            if pt.products_types == 'mold':
                if 'design_product_ids' in vals:
                    for rec in pt.design_product_ids:
                        rec.mold_product_ids = [(4,pt.id)]
                        rec.mold = 'yes'
#             if 'certificate_origin_product_ids' in vals:
#                 if pt.certificate_origin_product_ids:
#                     for rec in pt.certificate_origin_product_ids:
#                         pr_ids = rec.certificate_product_ids.ids
#                         pr_ids.append(pt.id)
#                         rec.certificate_product_ids = [(6,0,pr_ids)]
#                         rec.certificate = 'yes'
            if pt.products_types == 'is_jewellery':
                if 'design_product_id' in vals:
                    if pt.design_product_id:
                        pt.design_product_id.jewel_product_ids = [(4,pt.id)]
#         if self.products_types == 'design':
#             if 'mold_product_ids' in vals:
#                 for rec in self.mold_product_ids:
#                     rec.design_product_ids = [(4,self.id)]
        return result
    
    def _create_variant_ids(self):
        self.flush()
        Product = self.env["product.product"]

        variants_to_create = []
        variants_to_activate = Product
        variants_to_unlink = Product

        for tmpl_id in self:
            lines_without_no_variants = tmpl_id.valid_product_template_attribute_line_ids._without_no_variant_attributes()

            all_variants = tmpl_id.with_context(active_test=False).product_variant_ids.sorted(lambda p: (p.active, -p.id))

            current_variants_to_create = []
            current_variants_to_activate = Product

            # adding an attribute with only one value should not recreate product
            # write this attribute on every product to make sure we don't lose them
            single_value_lines = lines_without_no_variants.filtered(lambda ptal: len(ptal.product_template_value_ids._only_active()) == 1)
            if single_value_lines:
                for variant in all_variants:
                    combination = variant.product_template_attribute_value_ids | single_value_lines.product_template_value_ids._only_active()
                    # Do not add single value if the resulting combination would
                    # be invalid anyway.
                    if (
                        len(combination) == len(lines_without_no_variants) and
                        combination.attribute_line_id == lines_without_no_variants
                    ):
                        variant.product_template_attribute_value_ids = combination

            # Set containing existing `product.template.attribute.value` combination
            existing_variants = {
                variant.product_template_attribute_value_ids: variant for variant in all_variants
            }

            # Determine which product variants need to be created based on the attribute
            # configuration. If any attribute is set to generate variants dynamically, skip the
            # process.
            # Technical note: if there is no attribute, a variant is still created because
            # 'not any([])' and 'set([]) not in set([])' are True.
            if not tmpl_id.has_dynamic_attributes():
                # Iterator containing all possible `product.template.attribute.value` combination
                # The iterator is used to avoid MemoryError in case of a huge number of combination.
                all_combinations = itertools.product(*[
                    ptal.product_template_value_ids._only_active() for ptal in lines_without_no_variants
                ])
                # For each possible variant, create if it doesn't exist yet.
                for combination_tuple in all_combinations:
                    combination = self.env['product.template.attribute.value'].concat(*combination_tuple)
                    if combination in existing_variants:
                        current_variants_to_activate += existing_variants[combination]
                    else:
                        current_variants_to_create.append({
                            'product_tmpl_id': tmpl_id.id,
                            'product_template_attribute_value_ids': [(6, 0, combination.ids)],
                            'active': tmpl_id.active,
                        })
                        if len(current_variants_to_create) > 1000:
                            raise UserError(_(
                                'The number of variants to generate is too high. '
                                'You should either not generate variants for each combination or generate them on demand from the sales order. '
                                'To do so, open the form view of attributes and change the mode of *Create Variants*.'))
                variants_to_create += current_variants_to_create
                variants_to_activate += current_variants_to_activate

            else:
                for variant in existing_variants.values():
                    is_combination_possible = self._is_combination_possible_by_config(
                        combination=variant.product_template_attribute_value_ids,
                        ignore_no_variant=True,
                    )
                    if is_combination_possible:
                        current_variants_to_activate += variant
                variants_to_activate += current_variants_to_activate

            variants_to_unlink += all_variants - current_variants_to_activate
        if variants_to_activate:
            variants_to_activate.write({'active': True})
            if not variants_to_activate.bom_id and self.bom_ids:
                bom = self.bom_ids[0]
                dbom = bom.copy()
                dbom.product_id = variants_to_activate.id
                variants_to_activate.bom_id = dbom.id
                for l in dbom.bom_line_ids:
                    l.pro_pro_id = variants_to_activate.id
        if variants_to_create:
            variants = Product.create(variants_to_create)
            if self.bom_ids:
                for variant in variants:
                    if not variant.bom_id:
                        bom = self.bom_ids[0]
                        dbom = bom.copy()
                        dbom.product_id = variant.id
                        variant.bom_id = dbom.id
                        for l in dbom.bom_line_ids:
                            l.pro_pro_id = variant.id
        if variants_to_unlink:
            variants_to_unlink._unlink_or_archive()

        # prefetched o2m have to be reloaded (because of active_test)
        # (eg. product.template: product_variant_ids)
        # We can't rely on existing invalidate_cache because of the savepoint
        # in _unlink_or_archive.
        self.flush()
        self.invalidate_cache()
        return True

    
class ProductProduct(models.Model):
    _inherit = 'product.product'   
    
    name = fields.Char("Name") 
    metal = fields.Char("Metal") 
    weight_jewel = fields.Float('Gross Weight', help= "Gross Weight")
    net_weight = fields.Float('Net Weight', )
    stone_weight = fields.Float('Stone Weight', help= "Weight of the stone in the Ornament")
    touch = fields.Float('Purity',help= "Purity")
    wastage = fields.Float("Wastage")
    jewel_seq = fields.Integer("Jewel Seq")
    jfiness = fields.Many2one('metal.finess',string='Fineness', store=True)
    jewel_size = fields.Many2one('jewel.size',"Jewel Size", store=True)
    jplating = fields.Many2one('metal.plating',string='Plating', store=True)
    jstone_name_id = fields.Many2one('stone.name', string='J Center stone', store=True)
    finding_type_id = fields.Many2one('finding.type',  'Finding Type', store=True)
    finding_subtype_id = fields.Many2one('finding.sub.type', "Sub Type", store=True)
    finding_fineness_id = fields.Many2one('metal.finess',  'F Fineness', store=True)
    finding_plating_id = fields.Many2one('metal.plating',  'F Plating', store=True)
    finding_Thickness_id = fields.Many2one('metal.thickness',  'Thickness', store=True)
    finding_plating_thickness_id = fields.Many2one('metal.platingfiness',  'Plating Fineness', store=True)
    center_color_stone_id = fields.Many2one('center.color.stone', "Center Stone Color")
    provided_by = fields.Selection([('vendor','Vendor'),('factory','Factory')], "Provided By") 
    ir_attachment_ids = fields.One2many('ir.attachment', 'product_id', "Files")
    
    @api.onchange('default_code')
    def onchange_default_code(self):
        if self.default_code:
            self.barcode =  self.default_code
    
    @api.model
    def create(self, vals):
        fineness = plating = ''
        sshape = scut = sname = ''
        product = ''
        res = super(ProductProduct, self).create(vals)
#         pdb.set_trace()
        res.rseq = ''
        year = str(datetime.now().year)[-2:]
        if not res.name:
            res.name = res.product_tmpl_id.name
        if not res.provided_by:
            res.provided_by = res.product_tmpl_id.provided_by
        if res.products_types == 'stone':
            sname = res.stone_name_id.code
            sshape = res.stone_shape_id.code
            scut = res.stone_cutting_id.code
            stone_rec = self.env['product.product'].search_count([('products_types', '=', 'stone'),('stone_name_id', '=', res.stone_name_id.id),
                                                                   ('stone_shape_id', '=', res.stone_shape_id.id),('stone_cutting_id', '=', res.stone_cutting_id.id),
                                                                   ('size_width', '=', res.size_width),('size_length', '=', res.size_length)])
            if stone_rec < 10:
                res.rseq = '0' + str(stone_rec)
            else:
                res.rseq =  str(stone_rec)
            length = width = ''
            if res.size_length < 10:
                length = '0'+ str(res.size_length)
            else:
                length = str(res.size_length)
                
            if len(length) == 4:
                length = length + '0'
            
            if res.size_width < 10:
                width = '0'+ str(res.size_width)
            else:
                width = str(res.size_width)
                
            if len(width) == 4:
                width = width + '0'
            
            sku = str(sname) + length + width + str(sshape) + str(scut) + res.rseq
            sku = sku.replace('False', '')
            sku = sku.replace('.','')
            res.default_code = sku
        if res.products_types == 'metal':
            fineness = res.finess.code
            plating = res.plating.code
            metal_rec = self.env['product.product'].search_count([('products_types', '=', 'metal'),('finess','=',res.finess.id),('plating','=',res.plating.id)])
            if metal_rec < 10:
                res.rseq = '0' + str(metal_rec)
            else:
                res.rseq =  str(metal_rec)
            sku = 'M' + str(fineness) + str(plating) + res.rseq
            sku = sku.replace('False', '')
            sku = sku.replace('.','')
            res.default_code = sku
            pfiness = fineness = plating = thick = ''
            if res.finess:
                fineness = res.finess.name
            if res.plating_fitness_id:
                pfiness = res.plating_fitness_id.name
            if res.plating:
                plating = res.plating.name
            if res.thickness:
                thick = res.thickness.name
#             res.name = fineness + ' ' + pfiness + ' ' + plating + ' ' +thick
            
        if res.products_types == 'certification':
            lab = ''
            type = ''
            no = ''
            if res.certification_lab.code:
                lab = res.certification_lab.code
            if res.certification_type.code:
                type = res.certification_type.code
            if res.certification_no:
                no = res.certification_no[-5:]
            cert_rec = self.env['product.product'].search_count([('products_types', '=', 'certification'),('certification_lab', '=', res.certification_lab.id),
                                                                 ('certification_type', '=', res.certification_type.id),
                                                                 ('certification_no', '=', res.certification_no)])
            if cert_rec < 10:
                res.rseq = '0' + str(cert_rec)
            else:
                res.rseq =  str(cert_rec)
            sku = str(lab) + str(type) + str(no) + res.rseq
            sku = sku.replace('False', '')
            sku = sku.replace('.','')
            res.default_code = sku
            weight = ''
            if res.stone_weight < 10:
                weight = '0'+ str(res.stone_weight)
            else:
                weight = str(res.stone_weight)
                
            if len(weight) == 4:
                weight = weight + '0'        
            if weight:
                product += weight + ' Ctw'
            if res.cstone_name_id:
                product += ' '+ res.cstone_name_id.name
            if res.certification_lab:
                product += ' ' + res.certification_lab.code
            if res.certification_type:
                product += ' ' + res.certification_type.name
#             res.name = product   
        if res.products_types == 'stone':
            product = ''
            length = width = ''
            if res.size_length < 10:
                length = '0'+ str(res.size_length)
            else:
                length = str(res.size_length)
            if len(length) == 4:
                length = length + '0'
            
            if res.size_width < 10:
                width = '0'+ str(res.size_width)            
            else:
                width = str(res.size_width)
            if len(width) == 4:
                width = width + '0'
            product += length + 'x' + width + 'mm' 
            if res.stone_shape_id:
                product += ' ' + res.stone_shape_id.name 
            if res.stone_name_id:
               product += ' ' + res.stone_name_id.name 
            if res.stone_cutting_id:
               product += ' ' + res.stone_cutting_id.name 
            if res.gem:                
                if res.gemstonecolorgrade and res.gemstoneclaritygrade:
                    product+= ' ' + res.gemstonecolorgrade.name + '/'  + res.gemstoneclaritygrade.name
                else:
                    if res.gemstonecolorgrade:
                        product += ' ' + res.gemstonecolorgrade.name 
                    if res.gemstoneclaritygrade:
                        product+= ' ' + res.gemstoneclaritygrade.name 
                
            if res.dia:
                if res.diacolorgrade and res.diaclaritygrade:
                    product += ' ' + res.diacolorgrade.name + '/' + res.diaclaritygrade.name
                else:                    
                    if res.diacolorgrade:
                        product += ' ' + res.diacolorgrade.name
                    if res.diaclaritygrade:
                        product += ' ' +res.diaclaritygrade.name
#             res.name = product
        if res.products_types == 'mold':
#             seq = self.env['ir.sequence'].next_by_code('mold')
            if not res.rseq:
                res.rseq = ''
#             seq = self.env['ir.sequence'].next_by_code('mold')
            mold_rec = self.env['product.template'].search_count([('products_types', '=', 'mold')])
            if mold_rec < 10:
                res.rseq = '00' + str(mold_rec)
            if mold_rec >= 10:
                res.rseq = '0' + str(mold_rec)
            if mold_rec  >= 100:
                res.rseq =  str(mold_rec)
            Jewel = mlp = mat = ''            
            if res.mold_line_part_id:
                mlp = res.mold_line_part_id.name
            year = str(datetime.now().year)[-2:]
            if res.mold_material_id:
                mat = res.mold_material_id.name  
                Jewel = res.mold_line_part_id.code          
            res.default_code = 'M' + Jewel + year + res.rseq
#             res.name = mlp + ' ' + mat + ' ' + ' Mold'
        if res.products_types == 'is_jewellery':
            if res.jewel_mold == 'no' and 'style' in vals and vals['style'] == False:
                seq = ''
                seqrec = self.env['product.product'].search([('jtype', '=', res.jtype)])
                seq = len(seqrec) + 1
                res.jewel_seq = seq
                if int(seq) < 10:
                    seq = '00' + str(seq)
                if int(seq) < 100:
                    seq = '0' + str(seq)
                Jewel = jsize = ''
                if res.jtype == 'ring':
                    Jewel = 'R'
                if res.jtype == 'earring':
                    Jewel = 'E'
                if res.jtype == 'pendant':
                    Jewel = 'P'
                if res.jtype == 'bracelet':
                    Jewel = 'B'
                if res.jtype == 'necklace':
                    Jewel = 'N'
                if res.jtype == 'brooche':
                    Jewel = 'BR'
                if res.jtype == 'bangle':
                    Jewel = 'BA'
                if res.jtype == 'cuff':
                    Jewel = 'C'
                year = str(datetime.now().year)[-2:]
#                 res.style = Jewel + year + seq            
            sname = fineness = plating = jsize = ''
            sname = res.jstone_name_id.code
            sname = fineness = plating = jsize = ccs = ''
            fine = plate = jewels = stone = False
            ccs = False
            if res.product_template_attribute_value_ids:
                for tempvar in res.product_template_attribute_value_ids:
#                     stone = res.product_tmpl_id.jstone_name_id.id
#                     jewels = res.product_tmpl_id.jewel_size.id
#                     plate = res.product_tmpl_id.jplating.id
#                     fine = res.product_tmpl_id.jfiness.id
                    res.jstone_name_id = False
                    res.jewel_size = False
                    res.jplating = False
                    res.jfiness = False
                    res.center_color_stone_id = False
                    if tempvar.attribute_id.name == 'Fineness':
                        fineness = tempvar.product_attribute_value_id.code
                        fines = self.env['metal.finess'].search([('name', '=', tempvar.product_attribute_value_id.name)])
                        if fines:
                            fine = fines.id
                        else:
                            fines = self.env['metal.finess'].create({
                                'name': tempvar.product_attribute_value_id.name,
                                'jewel_code': tempvar.product_attribute_value_id.code})
                            fine = fines.id
                    if tempvar.attribute_id.name == 'Center Stone Color':
                        center_stone = self.env['center.color.stone'].search([('name', '=', tempvar.product_attribute_value_id.name)])
                        if center_stone:
                            ccs = center_stone.id
                        else:
                            center_stone = self.env['center.color.stone'].create({
                                'name': tempvar.product_attribute_value_id.name,
                                'code': tempvar.product_attribute_value_id.code})
                            ccs = center_stone.id
                    if tempvar.attribute_id.name == 'Plating':
                        plating = tempvar.product_attribute_value_id.code
                        plates = self.env['metal.plating'].search([('name', '=', tempvar.product_attribute_value_id.name)])
                        if plates:
                            plate = plates.id
                        else:
                            plates = self.env['metal.plating'].create({
                                'name': tempvar.product_attribute_value_id.name,
                                'jewel_code': tempvar.product_attribute_value_id.code})
                            plate = plates.id
                    if tempvar.attribute_id.name == 'Jewel Size':
                        jewelss = False
                        jsize = tempvar.product_attribute_value_id.code
                        jewelss = self.env['jewel.size'].search([('name', '=', tempvar.product_attribute_value_id.name)])
                        if jewelss:
                            for j in jewelss:
                                if j.jtypes:
                                    for js in j.jtypes.ids:
                                        if js in tempvar.product_attribute_value_id.jtypes.ids:
                                            jewelss = j
                            jewels = jewelss.id
                        else:
                            jewelss = self.env['jewel.size'].create({
                                'name': tempvar.product_attribute_value_id.name,
                                'code': tempvar.product_attribute_value_id.code,
                                'jtypes': [(6, 0, tempvar.product_attribute_value_id.jtypes.ids)]
                                })
                            jewels = jewelss.id
                    if tempvar.attribute_id.name == 'Center stone':
                        sname = tempvar.product_attribute_value_id.code
                        stones = self.env['stone.name'].search([('name', '=', tempvar.product_attribute_value_id.name)])
                        if stones:
                            stone = stones.id
                        else:
                            stones = self.env['stone.name'].create({
                                'name': tempvar.product_attribute_value_id.name,
                                'code': tempvar.product_attribute_value_id.code,
                                'code2': tempvar.product_attribute_value_id.code2,
                                'gemstone': tempvar.product_attribute_value_id.gemstone,
                                'diamond': tempvar.product_attribute_value_id.diamond,
                                'birth_stone': tempvar.product_attribute_value_id.birth_stone
                                })
                            stone = stones.id
                    
#             fineness = res.jfiness.jewel_code
#             plating = res.jplating.jewel_code
#             jsize = res.jewel_size.code
            jewel_rec = self.env['product.product'].search_count([('products_types', '=', 'is_jewellery'), ('jtype', '=', res.jtype),('active', '=', True)])            
            if jewel_rec < 10:
                res.rseq = '0' + str(jewel_rec)
            else:
                res.rseq =  str(jewel_rec)
            Jewel = ''
            if res.jtype == 'ring':
                Jewel = 'R'
            if res.jtype == 'earring':
                Jewel = 'E'
            if res.jtype == 'pendant':
                Jewel = 'P'
            if res.jtype == 'bracelet':
                Jewel = 'B'
            if res.jtype == 'necklace':
                Jewel = 'N'
            if res.jtype == 'brooche':
                Jewel = 'BR'
            if res.jtype == 'bangle':
                Jewel = 'BA'
            if res.jtype == 'cuff':
                Jewel = 'C'
            year = str(datetime.now().year)[-2:]
            if not sname:
                sname = ''
            sku = Jewel + sname + str(fineness) + str(plating) + str(year) + res.rseq + jsize
            sku = sku.replace('False', '')
            sku = sku.replace('.','')
            res.write({
                'default_code': sku,
                'jstone_name_id': stone,
                'jfiness': fine,
                'jplating': plate,
                'jewel_size': jewels,
                'center_color_stone_id': ccs 
                })
        if res.products_types == 'finding':            
            type = ftype =find = stype = fine = pfine = plate = thick = False
            ft = st = fn = pl = tn = pf = ''
            if res.product_template_attribute_value_ids:
                for tempvar in res.product_template_attribute_value_ids:
                    res.finding_type_id = False
                    res.finding_subtype_id = False
                    res.finding_plating_id = False
                    res.finding_fineness_id = False
                    res.finding_Thickness_id = False
                    res.finding_plating_thickness_id = False
                    if tempvar.attribute_id.name == 'Finding Type':
                        type = tempvar.product_attribute_value_id.code
                        ft = tempvar.product_attribute_value_id.name
                        findtype = self.env['finding.type'].search([('name', '=', tempvar.product_attribute_value_id.name)])
                        if findtype:
                            ftype = findtype.id
                        else:
                            findtype = self.env['finding.type'].create({
                                'name': tempvar.product_attribute_value_id.name,
                                'code': tempvar.product_attribute_value_id.code})
                            ftype = fines.id
                    if tempvar.attribute_id.name == 'Sub Type':
                        st = tempvar.product_attribute_value_id.name
                        subtype = self.env['finding.sub.type'].search([('name', '=', tempvar.product_attribute_value_id.name)])
                        if subtype:
                            stype = subtype.id
                        else:
                            subtype = self.env['finding.sub.type'].create({
                                'name': tempvar.product_attribute_value_id.name,
                                })
                            stype = subtype.id
                    if tempvar.attribute_id.name == 'Fineness':
                        fn = tempvar.product_attribute_value_id.name
                        fines = self.env['metal.finess'].search([('name', '=', tempvar.product_attribute_value_id.name)])
                        if fines:
                            fine = fines.id
                        else:
                            fines = self.env['metal.finess'].create({
                                'name': tempvar.product_attribute_value_id.name,
                                'code': tempvar.product_attribute_value_id.code})
                            fine = fines.id
                    if tempvar.attribute_id.name == 'Plating':
                        pl = tempvar.product_attribute_value_id.name
                        plates = self.env['metal.plating'].search([('name', '=', tempvar.product_attribute_value_id.name)])
                        if plates:
                            plate = plates.id
                        else:
                            plates = self.env['metal.plating'].create({
                                'name': tempvar.product_attribute_value_id.name,
                                'code': tempvar.product_attribute_value_id.code})
                            plate = plates.id
                    if tempvar.attribute_id.name == 'Thickness':
                        tn = tempvar.product_attribute_value_id.name
                        thickness = self.env['metal.thickness'].search([('name', '=', tempvar.product_attribute_value_id.name)])
                        if thickness:
                            thick = thickness.id
                        else:
                            thickness = self.env['metal.thickness'].create({
                                'name': tempvar.product_attribute_value_id.name,
                                })
                            thick = thickness.id
                    if tempvar.attribute_id.name == 'Plating Fineness':
                        pf = tempvar.product_attribute_value_id.name
                        pfiness = self.env['metal.platingfiness'].search([('name', '=', tempvar.product_attribute_value_id.name)])
                        if pfiness:
                            pfine = pfiness.id
                        else:
                            pfiness = self.env['metal.platingfiness'].create({
                                'name': tempvar.product_attribute_value_id.name,
#                                 'code': tempvar.product_attribute_value_id.code
                                })
                            pfine = pfiness.id
            
#             if res.finding_type_id:
#                 type = res.finding_type_id.code            
            find_rec = self.env['product.product'].search_count([('products_types', '=', 'finding'), ('finding_type_id', '=', res.finding_type_id.id)])
            if find_rec < 10:
                res.rseq = '0' + str(find_rec)
            else:
                res.rseq =  str(find_rec)
            if not type:
                type = ''
            if not res.rseq:
                res.rseq = '01'
            sku  = 'F' + type + year + res.rseq 
            name = str(st) + ' '+ str(ft) + ' in ' + ' ' + str(fn) + ' ' + str(pf) + ' ' + str(pl) + ' ' + str(tn)
            res.write({
                'default_code': sku,
                'name': name,
                'finding_subtype_id': stype,
                'finding_fineness_id': fine,
                'finding_type_id': ftype,
                'finding_plating_id': plate,
                'finding_Thickness_id': thick,
                'finding_plating_thickness_id': pfine
                })
        if res.default_code:
            res.barcode = res.default_code
        if 'certificate_product_ids' in vals:
            if res.certificate_product_ids:
                for rec in res.certificate_product_ids:
                    rec.certificate_origin_product_ids = [(4,res.id)]
                    rec.certificate = 'yes'
        if 'certificate_origin_product_ids' in vals:
            if res.certificate_origin_product_ids:
                for rec in res.certificate_origin_product_ids:
                    pr_ids = rec.certificate_product_ids.ids
                    pr_ids.append(res.id)
                    rec.certificate_product_ids = [(6,0,pr_ids)]
                    rec.certificate = 'yes'
        return res
    
    def write(self, vals):  
        result = super(ProductProduct, self).write(vals)
        if 'jfiness' in vals and vals['jfiness'] != False:
            self.env.cr.execute("Update product_product set jfiness = %s WHERE id=%s", (vals['jfiness'],self.id,))
        if 'jplating' in vals and vals['jplating'] != False:
            self.env.cr.execute("Update product_product set jplating = %s WHERE id=%s", (vals['jplating'],self.id,))
        if 'jstone_name_id' in vals and vals['jstone_name_id'] != False:
            self.env.cr.execute("Update product_product set jstone_name_id = %s WHERE id=%s", (vals['jstone_name_id'],self.id,))
        if 'center_color_stone_id' in vals and vals['center_color_stone_id'] != False and vals['center_color_stone_id'] != '':
            self.env.cr.execute("Update product_product set center_color_stone_id = %s WHERE id=%s", (vals['center_color_stone_id'],self.id,))
        if 'finding_subtype_id' in vals and vals['finding_subtype_id'] != False:
            self.env.cr.execute("Update product_product set finding_subtype_id = %s WHERE id=%s", (vals['finding_subtype_id'],self.id,))
        if 'finding_fineness_id' in vals and vals['finding_fineness_id'] != False:
            self.env.cr.execute("Update product_product set finding_fineness_id = %s WHERE id=%s", (vals['finding_fineness_id'],self.id,))
        if 'finding_type_id' in vals and vals['finding_type_id'] != False:
            self.env.cr.execute("Update product_product set finding_type_id = %s WHERE id=%s", (vals['finding_type_id'],self.id,))
        if 'finding_plating_id' in vals and vals['finding_plating_id'] != False:
            self.env.cr.execute("Update product_product set finding_plating_id = %s WHERE id=%s", (vals['finding_plating_id'],self.id,))
#         if 'finding_Thickness_id' in vals and vals['finding_Thickness_id'] != False:
#             self.env.cr.execute("Update product_product set finding_Thickness_id = %s WHERE id=%s", (vals['finding_Thickness_id'],self.id,))
        if 'finding_plating_thickness_id' in vals and vals['finding_plating_thickness_id'] != False:
            self.env.cr.execute("Update product_product set finding_plating_thickness_id = %s WHERE id=%s", (vals['finding_plating_thickness_id'],self.id,))
        pt = self
        if 'certificate_product_ids' in vals:
            if pt.certificate_product_ids:
                for rec in pt.certificate_product_ids:
                    rec.certificate_origin_product_ids = [(4,pt.id)]
                    rec.certificate = 'yes'
#         if 'certificate_origin_product_ids' in vals:
#             if pt.certificate_origin_product_ids:
#                 for rec in pt.certificate_origin_product_ids:
#                     pr_ids = rec.certificate_product_ids.ids
#                     pr_ids.append(pt.id)
#                     rec.certificate_product_ids = [(6,0,pr_ids)]
#                     rec.certificate = 'yes'
        
        return result
    
class ProductAttVal(models.Model):
    _inherit = 'product.attribute.value'     
    
    attribute = fields.Char("Att name", compute='get_attribute', store=True)
    code = fields.Char("Code")
    gemstone = fields.Boolean(string='Is a Gem Stone')
    diamond = fields.Boolean(string='Is a Diamond')
    code2 = fields.Char(string='Code 2')
    jewel_code = fields.Char(string='Jewel Code')
    birth_stone = fields.Selection([('january', 'January'),
                             ('february', 'February'),
                             ('march', 'March'),
                             ('april', 'April'),
                             ('may', 'May'),
                             ('june', 'June'),
                             ('july', 'July'),
                             ('august', 'August'),
                             ('september', 'September'),
                             ('october', 'October'),
                             ('november', 'November'),
                             ('december', 'December')],'Birth Stone')
#     jtype = fields.Selection([('earring', 'Earring'),
#                              ('pendant', 'Pendant'),
#                              ('bracelet', 'Bracelet'),
#                              ('ring', 'Ring'),
#                              ('necklace', 'Necklace'),
#                              ('brooche', 'Brooche'),
#                              ('bangle', 'Bangle'),
#                              ('cuff', 'Cuff')],'Jewelry Type')
    jtypes = fields.Many2many('jewel.tags', 'jewel_tag_product_rel', 'product_id', 'tag_id', "Jewelry Type")
    
    @api.depends('attribute_id')
    def get_attribute(self):
        for rec in self:
            if rec.attribute_id:
                rec.attribute = rec.attribute_id.name
    
    @api.model
    def create(self, vals):  
        tempvar = super(ProductAttVal, self).create(vals)
        if tempvar.attribute_id.name == 'Fineness':
            fines = self.env['metal.finess'].search([('name', '=', tempvar.name)])
            if not fines:
                fines = self.env['metal.finess'].create({
                    'name': tempvar.name,
                    'code': tempvar.code,
                    'jewel_code': tempvar.jewel_code})
        if tempvar.attribute_id.name == 'Center Stone Color':
            center_stone = self.env['center.color.stone'].search([('name', '=', tempvar.name)])
            if not center_stone:
                center_stone = self.env['center.color.stone'].create({
                    'name': tempvar.name,
                    'code': tempvar.code})
        if tempvar.attribute_id.name == 'Plating':
            plates = self.env['metal.plating'].search([('name', '=', tempvar.name)])
            if not plates:
                plates = self.env['metal.plating'].create({
                    'name': tempvar.name,
                    'code': tempvar.code,
                    'code2': tempvar.code2,
                    'jewel_code': tempvar.jewel_code})
        if tempvar.attribute_id.name == 'Jewel Size':
            jewelss = self.env['jewel.size'].search([('name', '=', tempvar.name)])
            if not jewelss:
                jewelss = self.env['jewel.size'].create({
                    'name': tempvar.name,
                    'code': tempvar.code,
                    'jtypes': [(6,0,tempvar.jtypes.ids)]
                    })
        if tempvar.attribute_id.name == 'Center stone':
            stones = self.env['stone.name'].search([('name', '=', tempvar.name)])
            if not stones:
                stones = self.env['stone.name'].create({
                    'name': tempvar.name,
                    'code': tempvar.code,
                    'code2': tempvar.code2,
                    'gemstone': tempvar.gemstone,
                    'diamond': tempvar.diamond,
                    'birth_stone': tempvar.birth_stone
                    })
        if tempvar.attribute_id.name == 'Finding Type':
            findtype = self.env['finding.type'].search([('name', '=', tempvar.name)])
            if not findtype:
                findtype = self.env['finding.type'].create({
                    'name': tempvar.name,
                    'code': tempvar.code})
        if tempvar.attribute_id.name == 'Sub Type':
            subtype = self.env['finding.sub.type'].search([('name', '=', tempvar.name)])
            if not subtype:
                subtype = self.env['finding.sub.type'].create({
                    'name': tempvar.name,
                    })
        if tempvar.attribute_id.name == 'Thickness':
            thickness = self.env['metal.thickness'].search([('name', '=', tempvar.name)])
            if not thickness:
                thickness = self.env['metal.thickness'].create({
                    'name': tempvar.name,
                    })
                thick = thickness.id
        if tempvar.attribute_id.name == 'Plating Fineness':
            pfiness = self.env['metal.platingfiness'].search([('name', '=', tempvar.name)])
            if not pfiness:
                pfiness = self.env['metal.platingfiness'].create({
                    'name': tempvar.name,
                    })
        return tempvar
    
    @api.model
    def write(self, vals):  
        tempvar = self
        if tempvar.attribute_id.name == 'Fineness':
            fines = self.env['metal.finess'].search([('name', '=', tempvar.name)])
            if fines:
                if 'name' in vals:
                    fines.name = vals['name']
                if 'code' in vals:
                    fines.code = vals['code']
                if 'jewel_code' in vals:
                    fines.jewel_code = vals['jewel_code']
        if tempvar.attribute_id.name == 'Center Stone Color':
            center_stone = self.env['center.color.stone'].search([('name', '=', tempvar.name)])
            if center_stone:
                if 'name' in vals:
                    center_stone.name = vals['name']
                if 'code' in vals:
                    center_stone.code = vals['code']
        if tempvar.attribute_id.name == 'Plating':
            plates = self.env['metal.plating'].search([('name', '=', tempvar.name)])
            if plates:
                if 'name' in vals:
                    plates.name = vals['name']
                if 'code' in vals:
                    plates.code = vals['code']
                if 'code2' in vals:
                    plates.code2 = vals['code2']
                if 'jewel_code' in vals:
                    plates.jewel_code = vals['jewel_code']
        if tempvar.attribute_id.name == 'Jewel Size':
            jewelss = self.env['jewel.size'].search([('name', '=', tempvar.name)])
            if jewelss:
                if 'name' in vals:
                    jewelss.name = vals['name']
                if 'code' in vals:
                    jewelss.code = vals['code']
                if 'jtypes' in vals:
                    jewelss.jtypes = vals['jtypes']
        if tempvar.attribute_id.name == 'Center stone':
            stones = self.env['stone.name'].search([('name', '=', tempvar.name)])
            if stones:
                if 'name' in vals:
                    stones.name = vals['name']
                if 'code' in vals:
                    stones.code = vals['code']
                if 'code2' in vals:
                    stones.code2 = vals['code2']
                if 'gemstone' in vals:
                    stones.gemstone = vals['gemstone']
                if 'diamond' in vals:
                    stones.diamond = vals['diamond']
                if 'birth_stone' in vals:
                    stones.birth_stone = vals['birth_stone']
        if tempvar.attribute_id.name == 'Finding Type':
            findtype = self.env['finding.type'].search([('name', '=', tempvar.name)])
            if findtype:
                if 'name' in vals:
                    findtype.name = vals['name']
                if 'code' in vals:
                    findtype.code = vals['code']
        if tempvar.attribute_id.name == 'Sub Type':
            subtype = self.env['finding.sub.type'].search([('name', '=', tempvar.name)])
            if subtype:
                if 'name' in vals:
                    subtype.name = vals['name']
        if tempvar.attribute_id.name == 'Thickness':
            thickness = self.env['metal.thickness'].search([('name', '=', tempvar.name)])
            if thickness:
                if 'name' in vals:
                    thickness.name = vals['name']
        if tempvar.attribute_id.name == 'Plating Fineness':
            pfiness = self.env['metal.platingfiness'].search([('name', '=', tempvar.name)])
            if pfiness:
                if 'name' in vals:
                    pfiness.name = vals['name']
        tempvar = super(ProductAttVal, self).write(vals)
        return tempvar
    
class Attacment(models.Model):
    _inherit = 'ir.attachment'     
     
    product_tmpl_id = fields.Many2one('product.template', "Product")
    product_id = fields.Many2one('product.product', "Product Variant")
    desc = fields.Char("Description")   

class JewelTags(models.Model):
    _name = 'jewel.tags'
    
    name = fields.Char('Name')


class ProductTags(models.Model):
    _name = 'product.tags'
    
    name = fields.Char('Name')
    
class FindingType(models.Model):
    _name = 'finding.type'
    
    name = fields.Char('Name')
    code = fields.Char(string='Code')
    
class FindingSubType(models.Model):
    _name = 'finding.sub.type'
    
    name = fields.Char('Name')
    finding_type_id = fields.Many2one('finding.type', "Finding Type")
    
class FindingFineness(models.Model):
    _name = 'finding.fineness'
    
    name = fields.Char('Name')
    
class FindingPlating(models.Model):
    _name = 'finding.plating'
    
    name = fields.Char('Name')
    
class FindingThickness(models.Model):
    _name = 'finding.thickness'
    
    name = fields.Char('Name')
    
class FindingPlatingThickness(models.Model):
    _name = 'finding.plating.thickness'
    
    name = fields.Char('Name')

class BrandMaster(models.Model):
    _name = 'brand.master'
    
    name=fields.Char('Name')

class MoldType(models.Model):
    _name='mold.type'
    
    name=fields.Char(string='Name')
    code=fields.Char(string='code')
    
class CenterColorStone(models.Model):
    _name='center.color.stone'
    
    name = fields.Char(string='Name')
    code = fields.Char(string='code')
    
class MoldPart(models.Model):
    _name='mold.part'
    
    name=fields.Char(string='Name')
    code=fields.Char(string='code')
    parts = fields.Integer("Parts")
    
class MoldMaterial(models.Model):
    _name='mold.material'
    
    name=fields.Char(string='Name')
    
class MoldLinePart(models.Model):
    _name='mold.line.part'
    
    name=fields.Char(string='Name')
    code = fields.Char(string='Code')
    
class Mold(models.Model):
    _name='mold'
    _description = "Mold"
    
    name=fields.Char(string='Mold SKU Number')
    code=fields.Char(string='code')
    product_id = fields.Many2one('product.template', 'Product')
    mold_line_part_id = fields.Many2one('mold.line.part',  'Mold Part')
    mold_dimension = fields.Char("Dimension")
    mold_weight = fields.Float("Weight")
    mold_material_id = fields.Many2one('mold.material', "Material")
    mold_condition = fields.Char("Condition")
    mold_product_id = fields.Many2one('product.template', 'Product')
    
    @api.onchange('mold_product_id')
    def onchange_mold_product_id(self):
        if self.mold_product_id:
            self.mold_line_part_id = self.mold_product_id.mold_line_part_id.id
            self.mold_dimension = self.mold_product_id.mold_dimension
            self.mold_weight = self.mold_product_id.mold_weight
            self.mold_material_id = self.mold_product_id.mold_material_id.id
            self.mold_condition = self.mold_product_id.mold_condition
            self.name = self.mold_product_id.default_code

class SubBrandMaster(models.Model):
    _name = 'sub.brand.master'
    name=fields.Char('Name')
    brand_id = fields.Many2one('brand.master','Brand')
    
class JewelSize(models.Model):
    _name='jewel.size'
    _description = "Jewel Size"
    
    name=fields.Char(string='Name')
    code=fields.Char(string='Code')
    jtypes = fields.Many2many('jewel.tags', 'jewel_tag_size_rel', 'product_id', 'tag_id', "Jewelry Type")
    
class ChildSubBrandMaster(models.Model):
    _name = 'child.sub.brand.master'

    name=fields.Char('Name')
    sub_brand_id = fields.Many2one('sub.brand.master','Sub Brand')

class Motif(models.Model):
    _name = 'motif'

    name=fields.Char('Name')
    
class ResPartner(models.Model):
    _inherit = "res.partner"

    first_name = fields.Char('First Name')


class JewelleryType(models.Model):
    _name = 'jewellery.type'
    
    name=fields.Char('Name', required=True)
    type = fields.Selection([('earring', 'Ear Ring'),
                             ('pendant', 'Pendant'),
                             ('bracelet', 'Bracelet'),
                             ('ring', 'Ring'),
                             ('necklace', 'Necklace'),
                             ('brooche', 'Brooche'),
                             ('bangle', 'Bangle'),
                             ('cuff', 'Cuff')], string='Type', required=True)
    
class Clasp(models.Model):
    _name='clasp'
    name=fields.Char(string='Name')
    type = fields.Selection([('earring', 'Ear Ring'),('pendant', 'Pendant'),('bracelet', 'Bracelet'),('bangle', 'Bangle')], string='Type')

class Dimension(models.Model):
    _name='dimension'
    name=fields.Char(string='Name')

class StoneName(models.Model):
    _name='stone.name'
    
    name=fields.Char(string='Name')
    code=fields.Char(string='Code')
    code2 = fields.Char(string='Code 2')
    gemstone=fields.Boolean(string='Is a Gem Stone')
    diamond=fields.Boolean(string='Is a Diamond')
    birth_stone = fields.Selection([('january', 'January'),
                             ('february', 'February'),
                             ('march', 'March'),
                             ('april', 'April'),
                             ('may', 'May'),
                             ('june', 'June'),
                             ('july', 'July'),
                             ('august', 'August'),
                             ('september', 'September'),
                             ('october', 'October'),
                             ('november', 'November'),
                             ('december', 'December')],'Birth Stone')

    # @api.onchange('diamond')
    # def diamond(self):
    #     print ("ppppppppppppppppppppppppppppppppppppp")                                    
    #     if self.diamond == True:
    #         self.env['product.template'].dia=self.diamond
    #         print ("ppppppppppppppppppppppppppppppppppppp")
    #         print (dia)


class StoneShape(models.Model):
    _name='stone.shape'
    name=fields.Char(string='Name')
    code=fields.Char(string='Code')

class StoneColor(models.Model):
    _name='stone.color'
    name=fields.Char(string='Name')

class StoneCutting(models.Model):
    _name='stone.cutting'
    name=fields.Char(string='Name')
    code=fields.Char(string='Code')

class StoneOrigin(models.Model):
    _name='stone.origin'
    name=fields.Char(string='Name')

class StoneType(models.Model):
    _name='stone.type'
    name=fields.Char(string='Name')

class CertificationType(models.Model):
    _name='certification.type'
    
    name = fields.Char(string='Name')
    code = fields.Char(string='Code')

class StoneClass(models.Model):
    _name='stone.class'
    name=fields.Char(string='Name')


class Collection(models.Model):
    _name='collection'
    name=fields.Char(string='Name')


class EarClasp(models.Model):
    _name='ear.clasp'
    name=fields.Char(string='Name')
    # code=fields.Char(string='Code')

class ChainType(models.Model):
    _name='chain.type'
    name=fields.Char(string='Name')
    # code=fields.Char(string='Code')

class Braceletlen(models.Model):
    _name='bracelet.length'
    name=fields.Char(string='Name')
    # code=fields.Char(string='Code')

    
class BraceletClasp(models.Model):
    _name='bracelet.clasp'
    name=fields.Char(string='Name')
    # code=fields.Char(string='Code')

class BraceletSafety(models.Model):
    _name='bracelet.safety'
    name=fields.Char(string='Name')
    # code=fields.Char(string='Code')

class Extenderlen(models.Model):
    _name='extender.length'
    name=fields.Char(string=' Name')
    # code=fields.Char(string='Code')


class EarRing(models.Model):
    _name='ear.ring'
    name=fields.Char(string='Name')
    # code=fields.Char(string='Code')
    drop_length=fields.Float(string='Drop Length')
    drop_width=fields.Float(string='Drop Width')
    ear_clasp=fields.Many2one('ear.clasp', string='Ear Clasp')
    inside_dia=fields.Char(string='Inside DIA')

class Pendant(models.Model):
    _name='pendant'
    name=fields.Char(string='Name')
    # code=fields.Char(string='Code')
    chain = fields.Selection([('yes', 'Yes'),('no', 'No'),], string='Chain')
    chain_length=fields.Many2one('chain.length', string='Chain Length')
    chain_clasp=fields.Many2one('chain.clasp', string='Chain Clasp')
    drop_length=fields.Float(string='Drop Length')

class Bracelet(models.Model):
    _name='bracelet'
    name=fields.Char(string='Name')
    # code=fields.Char(string='Code')
    extender=fields.Char(string='Extender')
    length=fields.Many2one('bracelet.length',string='Length')
    clasp=fields.Many2one('bracelet.clasp', string='Clasp')
    safety=fields.Many2one('bracelet.safety', string='Safety')
    extender_length=fields.Many2one('extender.length', string='Extender Lengths')

class Ring(models.Model):
    _name='ring'
    name=fields.Char(string='Name')
    # code=fields.Char(string='Code')
    under_gallery = fields.Selection([('yes', 'Yes'),('no', 'No'),], string='Under Gallery')
    shank_width=fields.Float(string='Shank Width')


class Necklace(models.Model):
    _name='necklace'
    name=fields.Char(string='Name')
    # code=fields.Char(string='Code')
    necklace_extender = fields.Selection([('yes', 'Yes'),('no', 'No'),], string='Extender')
    necklace_extender_length = fields.Float(string='Extender Length')

class Cuffs(models.Model):
    _name='cuffs'
    name=fields.Char(string='Name')
    # code=fields.Char(string='Code')
    cuffs_length=fields.Many2one('cuffs.length',string='Length')

class Cuffslen(models.Model):
    _name='cuffs.length'
    name=fields.Char(string='Length')
    # code=fields.Char(string='Code')

class Bangles(models.Model):
    _name='bangles'
    name=fields.Char(string='Name')
    # code=fields.Char(string='Code')
    bangles_length=fields.Many2one('bangles.length',string='Length')
    bangles_clasp=fields.Many2one('bangles.clasp',string='Clasp')

class Bangleslen(models.Model):
    _name='bangles.length'
    name=fields.Char(string='Name')
    # code=fields.Char(string='Code')

class BanglesClasp(models.Model):
    _name='bangles.clasp'
    name=fields.Char(string='Name')
    # code=fields.Char(string='Code')


class DiaClarityGrade(models.Model):
    _name='stone.diaclaritygrade'
    
    name=fields.Char(string='Name')
    desc = fields.Char(string='Description')
    
    def name_get(self):
        result = []
        for cla in self:
            if cla.name and cla.desc:
                name = cla.name + ' - ' + cla.desc
                result.append((cla.id, name))
            else:
                name = cla.name
                result.append((cla.id, name))
        return result
    

class DiaColorGrade(models.Model):
    _name='stone.diacolorgrade'
    name=fields.Char(string='Name')
    desc = fields.Char(string='Description')
    
    def name_get(self):
        result = []
        for cla in self:
            if cla.name and cla.desc:
                name = cla.name + ' - ' + cla.desc
                result.append((cla.id, name))
            else:
                name = cla.name
                result.append((cla.id, name))
        return result

class GemstoneClarityGrade(models.Model):
    _name='stone.gemstoneclaritygrade'
    
    name=fields.Char(string='Name')
    desc = fields.Char(string='Description')
    
    def name_get(self):
        result = []
        for cla in self:
            if cla.name and cla.desc:
                name = cla.name + ' - ' + cla.desc
                result.append((cla.id, name))
            else:
                name = cla.name
                result.append((cla.id, name))
        return result

class GemstoneColorGrade(models.Model):
    _name='stone.gemstonecolorgrade'
    name=fields.Char(string='Name')
    desc = fields.Char(string='Description')
    
    def name_get(self):
        result = []
        for cla in self:
            if cla.name and cla.desc:
                name = cla.name + ' - ' + cla.desc
                result.append((cla.id, name))
            else:
                name = cla.name
                result.append((cla.id, name))
        return result

class Treatment(models.Model):
    _name='stone.treatment'
    name=fields.Char(string='Name')

class Group(models.Model):
    _name='stone.group'
    name=fields.Char(string='Name')


class MetalName(models.Model):
    _name='metal.name'
    name=fields.Char(string='Name')


class MetalFiness(models.Model):
    _name='metal.finess'
    name = fields.Char(string='Name')
    code = fields.Char(string='Code')
    jewel_code = fields.Char(string='Jewel Code')

class MetalPlating(models.Model):
    _name='metal.plating'
    name=fields.Char(string='Name')
    code=fields.Char(string='Code')
    code2 = fields.Char(string='Code 2')
    jewel_code = fields.Char(string='Jewel Code')

class MetalPlatingFiness(models.Model):
    _name='metal.platingfiness'
    name=fields.Char(string='Name')


class MetalThickness(models.Model):
    _name='metal.thickness'
    name=fields.Char(string='Name')

class Trademark(models.Model):
    _name='trademark'
    name=fields.Char(string='Trademark')

# class StoneSkew(models.Model):
#     _name='stone.skew'
#     name=fields.Char(string='Stone Skew')

class CertificationLab(models.Model):
    _name='certification.lab'
    name=fields.Char(string='Certification Lab')
    code=fields.Char(string='Code')
