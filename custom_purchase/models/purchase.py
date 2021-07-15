# -*- coding: utf-8 -*-

from odoo import api, fields, models, _ , tools
from odoo.exceptions import UserError
import base64
import pdb
 
class PurchaseOrder(models.Model):
    _inherit = 'purchase.order.line'
    
    shipped_qty = fields.Float("Shipped Qty", compute='compute_shipped_qty', store=True)
    qty_to_ship = fields.Float("Qty. to Ship", copy=False)
    shipping_number = fields.Char("Ship Number", copy=False)
    balance_to_ship = fields.Float("Bal. to Ship", compute='compute_balance_to_ship', store=True)
    jtype = fields.Selection(related='product_id.product_tmpl_id.jtype')
    bom_id_line = fields.One2many(related='product_id.bom_id_line')
    
    @api.depends('product_qty','shipped_qty', 'qty_received')
    def compute_balance_to_ship(self):
        total = 0.0
        for rec in self:
            rec.balance_to_ship = rec.product_qty - rec.qty_received
    
    @api.depends('move_ids', 'move_ids.shipped_qty')
    def compute_shipped_qty(self):
        total = 0.0
        for rec in self:
            if rec.move_ids:
                total = 0.0
                for move in rec.move_ids:
                    if move.purchase_line_id.id == rec.id:
                        total += move.shipped_qty
            rec.shipped_qty = total
    
class StockMove(models.Model):
    _inherit = 'stock.move'
    
    shipped_qty = fields.Float("Shipped Qty", copy=False)
    shipping_number = fields.Char("Ship Number", copy=False)
    pimage = fields.Binary(related='product_id.image_1024', store=True)
    
class StockMoveLine(models.Model):
    _inherit = 'stock.move.line'

    pimage = fields.Binary(related='product_id.image_1024', store=True)
    
class PurchaseReport(models.Model):
    _inherit = "purchase.report"

    effective_date = fields.Datetime(string="Effective Date")
    
    def _select(self):
        return super(PurchaseReport, self)._select() + ", spt.warehouse_id as picking_type_id, po.effective_date as effective_date"

    def _from(self):
        return super(PurchaseReport, self)._from() + " left join stock_picking_type spt on (spt.id=po.picking_type_id)"

    def _group_by(self):
        return super(PurchaseReport, self)._group_by() + ", spt.warehouse_id, effective_date"
    
