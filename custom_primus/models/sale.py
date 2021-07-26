# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from datetime import datetime, time


class SaleOrder(models.Model):
    _inherit = 'sale.order'
    _order = 'priority desc'

    priority = fields.Selection([('0', 'Very Low'), ('1', 'Low'), ('2', 'Normal'), ('3', 'High')], string='Priority')
    sale_type_id = fields.Many2one('sale.type', "Sale Type")
    buying_group_id = fields.Many2one('buying.group', "Buying Group")
    discount = fields.Float("Discount")
    ordered_by = fields.Char("Ordered by")
    
    @api.onchange('discount')
    def onchange_discount(self):
        if self.discount:
            if self.order_line:
                for line in self.order_line:
                    line.discount = self.discount

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'
    
    bom_ids = fields.One2many(related='product_id.bom_ids', string="BOM")    
    
#     @api.model
#     def default_get(self, fields):
#         print(self._context, "------------")
#         rec = super(SaleOrderLine, self).default_get(fields) 
#         if 'params' in self._context:
#             sale_id = self._context['params']['id']
#             sale = self.env['sale.order'].browse(sale_id)
#             print(sale, "-----------")
#             if sale:
#                 print(self._context,"===============")
#                 rec['discount'] = sale.discount
#         print(rec, "rec===========")
#         return rec
    
class Product(models.Model):
    _inherit = 'product.template'
    
    bom_id = fields.Many2one('mrp.bom', compute='compute_bom_id_main', string="BOM", store=True)
    bom_id_line = fields.One2many('mrp.bom.line', 'pro_tmp_id')
    product_qty = fields.Float(compute='compute_bom_id', store=True)
    code = fields.Char(compute='compute_bom_id', string="Reference", store=True)
    bom_type = fields.Selection([
        ('normal', 'Manufacture this product'),
        ('phantom', 'Kit'),
        ('subcontract', 'Subcontracting')], 'BoM Type',
        default='normal', compute='compute_bom_id', store=True)
    consumption = fields.Selection([
        ('flexible', 'Allowed'),
        ('warning', 'Allowed with warning'),
        ('strict', 'Blocked')],
        help="Defines if you can consume more or less components than the quantity defined on the BoM:\n"
             "  * Allowed: allowed for all manufacturing users.\n"
             "  * Allowed with warning: allowed for all manufacturing users with summary of consumption differences when closing the manufacturing order.\n"
             "  * Blocked: only a manager can close a manufacturing order when the BoM consumption is not respected.",
        default='warning',
        string='Flexible Consumption',
        compute='compute_bom_id', store=True)
    ready_to_produce = fields.Selection([
        ('all_available', ' When all components are available'),
        ('asap', 'When components for 1st operation are available')], string='Manufacturing Readiness',
        default='asap', help="Defines when a Manufacturing Order is considered as ready to be started", compute='compute_bom_id', store=True)
    picking_type_id = fields.Many2one('stock.picking.type', 'Operation Type', compute='compute_bom_id', store=True)
    bom_operation_ids = fields.One2many('mrp.routing.workcenter', related='bom_id.operation_ids',inverse_name='bom_id', store=True)
    bom_company_id = fields.Many2one('res.company', "Company", compute='compute_bom_id', store=True)
    
    @api.depends('bom_ids')
    def compute_bom_id_main(self):
        for rec in self:
            if rec.bom_ids:
                bom = rec.bom_ids[0]
                self.bom_id = bom.id
                
                    
    @api.depends('bom_ids','bom_id', 'bom_id.product_qty', 'bom_id.code', 'bom_id.type', 'bom_id.consumption', 'bom_id.ready_to_produce', 'bom_id.picking_type_id','bom_id.company_id', 'bom_id.bom_line_ids')
    def compute_bom_id(self):
        for rec in self:
            if rec.bom_id:
                bom = rec.bom_id
                self.product_qty = bom.product_qty
                self.code = bom.code
                self.bom_type = bom.type
                self.consumption = bom.consumption
                self.ready_to_produce = bom.ready_to_produce
                self.picking_type_id = bom.picking_type_id.id
                self.bom_company_id = bom.company_id.id
                for line in bom.bom_line_ids:
                    line.pro_tmp_id = rec.id
                    if line.pro_pro_id:
                        line.pro_tmp_id = False
                    
class ProductProduct(models.Model):
    _inherit = 'product.product'
    
    bom_id = fields.Many2one('mrp.bom', string="BOM", store=True)
    bom_id_line = fields.One2many('mrp.bom.line', 'pro_pro_id')
    code = fields.Char(compute='compute_bom_id', string="Reference", store=True)
    product_desc = fields.Text("Detailed Description", compute='compute_product_desc', store=True)
    
    @api.depends('bom_id_line','bom_id_line.bom_line_type_id', 'bom_id_line.product_qty', 'bom_id_line.product_id')
    def compute_product_desc(self):
        cs_qty = as_qty = as_qty2 = as_qty3 = 0.0
        accent_stone = []
        center_stone_name = accent_stone_name = Jewel = accent_stone_name2 = accent_stone_name3 = ''
        description = ''
        for rec in self:
            if rec.bom_id_line:
                center_stone = rec.bom_id_line.filtered(lambda b: b.bom_line_type_id.name == 'Center Stone')
                if center_stone:
                    for cs in center_stone:
                        cs_qty += cs.product_qty
                    csn = center_stone[0].product_id.name.split() 
                    if csn:
                        center_stone_name = csn[2] 
                    description += str("%.2f" % cs_qty) + ' Cts ' + center_stone_name 
                accent_stone = rec.bom_id_line.filtered(lambda b: b.bom_line_type_id.name == 'Accent Stone 1')
                if accent_stone:
                    for ast in accent_stone:
                        as_qty += ast.product_qty
                    asn = accent_stone[0].product_id.name.split() 
                    if asn:
                        accent_stone_name = asn[3] + ' ' + asn[4]
                    description += ' and ' + str("%.2f" % as_qty) + ' Cts ' + accent_stone_name
                if rec.jtype == 'ring':
                    Jewel = 'Ring'
                if rec.jtype == 'earring':
                    Jewel = 'Earring'
                if rec.jtype == 'pendant':
                    Jewel = 'Pendant'
                if rec.jtype == 'bracelet':
                    Jewel = 'Bracelet'
                if rec.jtype == 'necklace':
                    Jewel = 'Necklace'
                if rec.jtype == 'brooche':
                    Jewel = 'Brooche'
                if rec.jtype == 'bangle':
                    Jewel = 'Bangle'
                if rec.jtype == 'cuff':
                    Jewel = 'Cuff'
                description += ' ' + Jewel +  ' ' +str(rec.jfiness.code) + ' ' + str(rec.jplating.code)
                accent_stone2 = rec.bom_id_line.filtered(lambda b: b.bom_line_type_id.name == 'Accent Stone 2')
                if accent_stone2:
                    for ast in accent_stone2:
                        as_qty2 += ast.product_qty
                    asn2 = accent_stone2[0].product_id.name.split() 
                    if asn2:
                        accent_stone_name2 = asn2[3] + ' ' + asn2[4]
                    description += '\n' + str("%.2f" % as_qty2) + ' Cts ' + accent_stone_name2
                accent_stone3 = rec.bom_id_line.filtered(lambda b: b.bom_line_type_id.name == 'Accent Stone 3')
                if accent_stone3:
                    for ast in accent_stone3:
                        as_qty3 += ast.product_qty
                    asn3 = accent_stone2[0].product_id.name.split() 
                    if asn3:
                        accent_stone_name3 = asn3[2] + asn3[3]
                    description += '\n' + str("%.2f" % as_qty3) + ' Cts ' + accent_stone_name3
                metal = rec.bom_id_line.filtered(lambda b: b.bom_line_type_id.name == 'Metal')
                if metal[0]:
                    description += '\n' + str("%.2f" % metal.product_qty) + ' Grams'
            rec.product_desc = description
    
    @api.depends('bom_ids','bom_id', 'bom_id.code', 'bom_id.bom_line_ids')
    def compute_bom_id(self):
        for rec in self:
            if rec.bom_id:
                bom = rec.bom_id
                self.code = bom.code
                for line in bom.bom_line_ids:
                    line.pro_pro_id = rec.id
                    line.pro_tmp_id = False
    
class MrpBomLine(models.Model):
    _inherit = 'mrp.bom.line'
    
    pro_tmp_id = fields.Many2one('product.template', "Product Template",copy=False)
    pro_pro_id = fields.Many2one('product.product', "Product",copy=False)
    s_no = fields.Integer("S.No.")
    bom_line_type_id = fields.Many2one('bom.line.type', "Type")
    sku_number = fields.Char("SKU Number")
    description = fields.Char("Description")
    unit_cost = fields.Float("Unit Cost", compute='compute_unit_cost', store=True)
    total = fields.Float("Total", compute='compute_total', store=True)  
    provided_by = fields.Selection([('vendor','Vendor'),('factory','Factory')], "Provided By") 
    min_weight = fields.Float("Min weight")
    prototype = fields.Char("Prototype")
    product_id = fields.Many2one('product.product', 'Component', required=False, check_company=True)
    sec_quantity = fields.Float("Secondary Qty")
    secondary_uom_id = fields.Many2one('uom.uom', string="Secondary UOM")
    
    @api.depends('product_id', 'product_id.standard_price')
    def compute_unit_cost(self):
        for rec in self:
            if rec.product_id:
                rec.unit_cost = rec.product_id.standard_price
    
    @api.depends('unit_cost', 'product_qty')
    def compute_total(self):
        for rec in self:
            if rec.unit_cost and rec.product_qty:
                rec.total = rec.unit_cost * rec.product_qty
                
    @api.model
    def create(self, vals):
        res = super(MrpBomLine, self).create(vals)
        if res.product_id.provided_by:
            res.provided_by = res.product_id.provided_by
        return res
    
    def write(self, vals):
        res = super(MrpBomLine, self).write(vals)
        if 'product_id' in vals:
            for rec in self:
                if rec.product_id.provided_by:
                    rec.provided_by = rec.product_id.provided_by
        return res
                
    @api.onchange('product_id')
    def onchange_product_id(self):
        if self.product_id:
            self.product_uom_id = self.product_id.uom_id.id
            self.sku_number = self.product_id.default_code
            self.unit_cost = self.product_id.standard_price
            self.secondary_uom_id = self.product_id.secondary_uom_id.id
            self.provided_by = self.product_id.provided_by
            self.min_weight = self.product_id.min_weight
            
class MrpBom(models.Model):
    """ Defines bills of material for a product or a product template """
    _inherit = 'mrp.bom'

    @api.model
    def _bom_find_domain(self, product_tmpl=None, product=None, picking_type=None, company_id=False, bom_type=False):
        if product:
            if not product_tmpl:
                product_tmpl = product.product_tmpl_id
            domain = ['|', ('product_id', '=', product.id), '&', ('product_id', '=', False), ('product_tmpl_id', '=', product_tmpl.id)]
        elif product_tmpl:
            domain = [('product_tmpl_id', '=', product_tmpl.id)]
#         else:
#             # neither product nor template, makes no sense to search
#             raise UserError(_('You should provide either a product or a product template to search a BoM'))
        if picking_type:
            domain += ['|', ('picking_type_id', '=', picking_type.id), ('picking_type_id', '=', False)]
        if company_id or self.env.context.get('company_id'):
            domain = domain + ['|', ('company_id', '=', False), ('company_id', '=', company_id or self.env.context.get('company_id'))]
        if bom_type:
            domain += [('type', '=', bom_type)]
        # order to prioritize bom with product_id over the one without
        return domain
    
class Quant(models.Model):
    _inherit = 'stock.quant'
    
    @api.onchange('product_id')
    def onchange_quant_product_id(self):
        if self.product_id:
            seq = self.env['ir.sequence'].next_by_code('quant.lot') 
            year = str(datetime.now().year)[-2:]
            month = str(datetime.now().month)    
            lot = 'LOT' + str(year) + '0' + str(month) + seq
            stock_lot = self.env['stock.production.lot'].create({'name': lot, 'product_id': self.product_id.id,
                                                                 'company_id': self.env.company.id
                                                                 })
            self.lot_id = stock_lot.id
            
class Procurement(models.Model):
    _inherit = 'procurement.group'
    
    origin_product_id = fields.Many2one('product.product', "Subcontract Product")
              
class Pick(models.Model):
    _inherit = 'stock.picking'
    
    origin_product_id = fields.Many2one(related='group_id.origin_product_id', string="Subcontract Product", store=True)
    
    def button_validate(self):
        if self.picking_type_code == 'incoming':
            if self.move_line_ids:
                for line in self.move_line_ids:
                    if line.product_id.tracking == 'lot':
                        new_lines = []
                        seq = self.env['ir.sequence'].next_by_code('quant.lot') 
                        year = str(datetime.now().year)[-2:]
                        month = str(datetime.now().month)    
                        lot = 'LOT' + str(year) + '0' + str(month) + seq
                        line.lot_name = lot
                        line.qty_done = line.product_uom_qty
        res = super(Pick, self).button_validate()
        return res
    
    
        
        
    def action_view_delivery(self):
        self.ensure_one()
        action = self.env.ref('stock.action_picking_tree_all').read()[0]
        action['domain'] = [('name','=', self.origin),('picking_type_code', '=', 'incoming')]
        return action
    
    def action_view_purchase(self):
        self.ensure_one()
        action = self.env.ref('purchase.purchase_rfq').read()[0]
        action['domain'] = [('name','=', self.origin)]
        return action
    
    def _prepare_subcontract_mo_vals(self, subcontract_move, bom):
        subcontract_move.ensure_one()
        group = self.env['procurement.group'].create({
            'name': self.name,
            'partner_id': self.partner_id.id,
            'origin_product_id': subcontract_move.product_id.id
        })
        product = subcontract_move.product_id
        warehouse = self._get_warehouse(subcontract_move)
        vals = {
            'company_id': subcontract_move.company_id.id,
            'procurement_group_id': group.id,
            'product_id': product.id,
            'product_uom_id': subcontract_move.product_uom.id,
            'bom_id': bom.id,
            'location_src_id': subcontract_move.picking_id.partner_id.with_company(subcontract_move.company_id).property_stock_subcontractor.id,
            'location_dest_id': subcontract_move.picking_id.partner_id.with_company(subcontract_move.company_id).property_stock_subcontractor.id,
            'product_qty': subcontract_move.product_uom_qty,
            'picking_type_id': warehouse.subcontracting_type_id.id,
            'date_planned_start': subcontract_move.date
        }
        return vals

class SaleType(models.Model):
    _name = 'sale.type'
    
    name = fields.Char("Name")   
    
class BuyingGroup(models.Model):
    _name = 'buying.group'
    
    name = fields.Char("Name")    
    
class BomLineType(models.Model):
    _name = 'bom.line.type'
    
    name = fields.Char("Name")  
    
class ProvidedBy(models.Model):
    _name = 'provided.by'
    
    name = fields.Char("Name")  
    
       