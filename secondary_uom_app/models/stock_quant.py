# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class StockQuant(models.Model):
	_inherit = 'stock.quant'

	secondary_uom_id = fields.Many2one('uom.uom', compute='_quantity_secondary_compute', string="Secondary UOM", store=True)
	secondary_quantity = fields.Float('Secondary Qty',  digits='Product Unit of Measure', store=True)
# compute='_quantity_secondary_compute',

	@api.model
	def _get_inventory_fields_create(self):       
		return ['product_id', 'location_id', 'lot_id', 'package_id', 'owner_id', 'inventory_quantity', 'secondary_uom_id', 'secondary_quantity', 'available_quantity', 'on_hand', 'product_uom_id', 'quantity', 'reserved_quantity', 'value', 'currency_id', 'display_name', 'in_date', 'product_tmpl_id', 'tracking']
       
    
	@api.model
	def _get_inventory_fields_write(self):
	    return ['product_id', 'location_id', 'lot_id', 'package_id', 'owner_id', 'inventory_quantity', 'secondary_uom_id', 'secondary_quantity', 'available_quantity', 'on_hand', 'product_uom_id', 'quantity', 'reserved_quantity', 'value', 'currency_id', 'display_name', 'in_date', 'product_tmpl_id', 'tracking']
       
	@api.depends('product_id', 'quantity', 'product_uom_id')
	def _quantity_secondary_compute(self):
		for quant in self:
			if quant.product_id.is_secondary_uom:
# 				uom_quantity = quant.product_id.uom_id._compute_quantity(quant.quantity, quant.product_id.secondary_uom_id, rounding_method='HALF-UP')
				quant.secondary_uom_id = quant.product_id.secondary_uom_id
# 				quant.secondary_quantity = uom_quantity
	def create(self, vals):
		res = super(StockQuant, self).create(vals)
		qty = 0
		for quant in res:
			if quant.product_id.is_secondary_uom:
				move_line = self.env['stock.move.line'].search([('lot_id', '=', res.lot_id.id)])
				if move_line:
					for line in move_line:
						qty += line.secondary_done_qty
					uom_quantity = qty
				quant.secondary_quantity = uom_quantity