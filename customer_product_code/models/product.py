# -*- coding: utf-8 -*-
###############################################################################
#
#   customer_product_code for Odoo
#   Copyright (C) 2004-today OpenERP SA (<http://www.openerp.com>)
#   Copyright (C) 2016-today Geminate Consultancy Services (<http://geminatecs.com>).
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU Affero General Public License as
#   published by the Free Software Foundation, either version 3 of the
#   License, or (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#   GNU Affero General Public License for more details.
#
#   You should have received a copy of the GNU Affero General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
###############################################################################

from odoo import _, api, fields, models, SUPERUSER_ID
import pdb
import json
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

class ProductTemplate(models.Model):
    _inherit = "product.template"
    _order = "default_code, name"

    product_customer_code_ids = fields.One2many('product.customer.code',
        'product_id', 'Customer Codes')
    
    product_add_mode = fields.Selection([
        ('configurator', 'Product Configurator'),
        ('matrix', 'Order Grid Entry'),
    ], string='Add product mode', default='matrix', help="Configurator: choose attribute values to add the matching \
        product variant to the order.\nGrid: add several variants at once from the grid of attribute values")

#     default_code = fields.Char(related='product_variant_ids.default_code',
#         string='Internal Reference', store=True)

class Product(models.Model):
    _inherit = "product.product"
    _order = "default_code, name"

    product_customer_code_ids = fields.One2many('product.customer.code',
        'prod_id', 'Customer Codes')

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'
    
    customer_code = fields.Char("SKU number")
    customer_desc = fields.Char("Description")
    pimage = fields.Binary(related='product_id.image_1024', store=True)
    
#     @api.onchange('product_template_id', 'product_id')
#     def product_template_id_change(self):
#         if self.product_template_id:            
#             if 'partner_id' in self._context:
#                 print(self.product_id, "self.product_id-----", self.product_template_id, "self.product_template_id----")
#                 code_present = self.product_template_id.product_customer_code_ids.filtered(lambda line: line.partner_id.id == self._context['partner_id'])
#                 if code_present:
#                     self.customer_code = code_present.product_code
#                     self.customer_desc = code_present.product_name
#                 else:
#                     self.customer_code = self.product_template_id.default_code
#                     self.customer_desc = self.product_template_id.name
#                 if self.product_id.product_customer_code_ids:
#                     code_present = self.product_id.product_customer_code_ids.filtered(lambda line: line.partner_id.id == self._context['partner_id'])
#                     if code_present:
#                         self.customer_code = code_present.product_code
#                         self.customer_desc = code_present.product_name
#                     else:
#                         self.customer_code = self.product_id.default_code
#                         self.customer_desc = self.product_id.name
#                     
#             else:
#                 self.customer_code = self.product_template_id.default_code
#                 self.customer_desc = self.product_template_id.name
    
#     @api.onchange('product_id')
#     def product_id_change(self):
#         res = super(SaleOrderLine, self).product_id_change()
#         if self.product_id:
#             if 'partner_id' in self._context:
#                 if self.product_id.product_customer_code_ids:
#                     code_present = self.product_id.product_customer_code_ids.filtered(lambda line: line.partner_id.id == self._context['partner_id'])
#                     if code_present:
#                         self.customer_code = code_present.product_code
#                         self.customer_desc = code_present.product_name
#                     else:
#                         self.customer_code = self.product_id.default_code
#                         self.customer_desc = self.product_id.name
#                
#             else:
#                 self.customer_code = self.product_id.default_code
#                 self.customer_desc = self.product_id.name
#         return res
    
    
    
    def _prepare_invoice_line(self, **optional_values):
        """
        Prepare the dict of values to create the new invoice line for a sales order line.

        :param qty: float quantity to invoice
        :param optional_values: any parameter that should be added to the returned invoice line
        """
        self.ensure_one()
        res = {
            'display_type': self.display_type,
            'sequence': self.sequence,
            'name': self.name,
            'product_id': self.product_id.id,
            'product_uom_id': self.product_uom.id,
            'quantity': self.qty_to_invoice,
            'customer_code': self.customer_code,
            'customer_desc': self.customer_desc,
            'discount': self.discount,
            'price_unit': self.price_unit,
            'tax_ids': [(6, 0, self.tax_id.ids)],
            'analytic_account_id': self.order_id.analytic_account_id.id,
            'analytic_tag_ids': [(6, 0, self.analytic_tag_ids.ids)],
            'sale_line_ids': [(4, self.id)],
        }
        if optional_values:
            res.update(optional_values)
        if self.display_type:
            res['account_id'] = False
        return res
    
class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'
    
    customer_code = fields.Char("SKU number")
    customer_desc = fields.Char("Description")
    
    @api.onchange('product_id')
    def _onchange_product_id(self):
        res = super(AccountMoveLine, self)._onchange_product_id()
        if self.product_id:
            if 'default_partner_id' in self._context:
                code_present = self.product_id.product_tmpl_id.product_customer_code_ids.filtered(lambda line: line.partner_id.id == self._context['default_partner_id'])
                if code_present:
                    self.customer_code = code_present.product_code
                    self.customer_desc = code_present.product_name
                else:
                    self.customer_code = self.product_id.product_tmpl_id.default_code
                    self.customer_desc = self.product_id.product_tmpl_id.name
            else:
                self.customer_code = self.product_id.product_tmpl_id.default_code
                self.customer_desc = self.product_id.product_tmpl_id.name
        return res
    
class SaleOrder(models.Model):
    _inherit = 'sale.order'
    
    @api.onchange('grid')
    def _apply_grid(self):
        """Apply the given list of changed matrix cells to the current SO."""
        if self.grid and self.grid_update:
            grid = json.loads(self.grid)
            product_template = self.env['product.template'].browse(grid['product_template_id'])
            dirty_cells = grid['changes']
            Attrib = self.env['product.template.attribute.value']
            default_so_line_vals = {}
            new_lines = []
            for cell in dirty_cells:
                combination = Attrib.browse(cell['ptav_ids'])
                no_variant_attribute_values = combination - combination._without_no_variant_attributes()

                # create or find product variant from combination
                product = product_template._create_product_variant(combination)
                order_lines = self.order_line.filtered(
                    lambda line: line.product_id.id == product.id
                    and line.product_no_variant_attribute_value_ids.ids == no_variant_attribute_values.ids
                )

                # if product variant already exist in order lines
                old_qty = sum(order_lines.mapped('product_uom_qty'))
                qty = cell['qty']
                diff = qty - old_qty
                # TODO keep qty check? cannot be 0 because we only get cell changes ...
                if diff and order_lines:
                    if qty == 0:
                        if self.state in ['draft', 'sent']:
                            # Remove lines if qty was set to 0 in matrix
                            # only if SO state = draft/sent
                            self.order_line -= order_lines
                        else:
                            order_lines.update({'product_uom_qty': 0.0})
                    else:
                        """
                        When there are multiple lines for same product and its quantity was changed in the matrix,
                        An error is raised.

                        A 'good' strategy would be to:
                            * Sets the quantity of the first found line to the cell value
                            * Remove the other lines.

                        But this would remove all business logic linked to the other lines...
                        Therefore, it only raises an Error for now.
                        """
                        if len(order_lines) > 1:
                            raise ValidationError(_("You cannot change the quantity of a product present in multiple sale lines."))
                        else:
                            order_lines[0].product_uom_qty = qty
                            # If we want to support multiple lines edition:
                            # removal of other lines.
                            # For now, an error is raised instead
                            # if len(order_lines) > 1:
                            #     # Remove 1+ lines
                            #     self.order_line -= order_lines[1:]
                elif diff and not order_lines:
                    if not default_so_line_vals:
                        OrderLine = self.env['sale.order.line']
                        default_so_line_vals = OrderLine.default_get(OrderLine._fields.keys())
                    last_sequence = self.order_line[-1:].sequence
                    if last_sequence:
                        default_so_line_vals['sequence'] = last_sequence
                    customer_code = customer_desc = False
                    code_present = product.product_customer_code_ids.filtered(lambda line: line.partner_id.id == self.partner_id.id)
                    if code_present:
                        customer_code = code_present.product_code
                        customer_desc = code_present.product_name
                    else:
                        customer_code = product.default_code
                        customer_desc = product.name
                    new_lines.append((0, 0, dict(
                        default_so_line_vals,
                        product_id=product.id,
                        product_uom_qty=qty,
                        customer_code = customer_code,
                        customer_desc = customer_desc,
                        product_no_variant_attribute_value_ids=no_variant_attribute_values.ids)
                    ))
            if new_lines:
                res = False
                self.update(dict(order_line=new_lines))
                for line in self.order_line.filtered(lambda line: line.product_template_id == product_template):
                    res = line.product_id_change() or res
                    line._onchange_discount()
                    line._onchange_product_id_set_customer_lead()
                return res
         

class ProductProduct(models.Model):
    _inherit = "product.product"

#     def _product_partner_ref(self):
#         res = {}
#         for p in self:
#             data = self._get_partner_code_name(p, self._context.get('partner_id', None))
#             if not data['code']:
#                 data['code'] = p.code
#             if not data['name']:
#                 data['name'] = p.name
#             res[p.id] = (data['code'] and ('['+data['code']+'] ') or '') + (data['name'] or '')
#             p.partner_ref = res[p.id]
#         return res
# # 
#     def _get_partner_code_name(self, product, partner_id):
#         if self._context.get('type', False) == 'in_invoice':
#             for supinfo in product.seller_ids:
#                 if supinfo.name.id == partner_id:
#                     return {'code': supinfo.product_code or product.default_code, 'name': supinfo.product_name or product.name}
#         else:
#             for buyinfo in product.product_customer_code_ids:
#                 if buyinfo.partner_id.id == partner_id:
#                     return {'code': buyinfo.product_code or product.default_code, 'name': buyinfo.product_name or product.name}
#         res = {'code': product.default_code, 'name': product.name}
#         return res
#  
#     partner_ref = fields.Char(compute='_product_partner_ref', string='Customer ref')
# 
#     def copy(self, default=None):
#         if not default:
#             default = {}
#         default['product_customer_code_ids'] = False
#         res = super(ProductProduct, self).copy(default=default)
#         return res
# 
#     def name_get(self):
# #         # TDE: this could be cleaned a bit I think
# # 
#         def _name_get(d):
#             name = d.get('name', '')
#             code = self._context.get('display_default_code', True) and d.get('default_code', False) or False
#             base_product = self.browse(d.get('id')) or False
#             if code:
#                 if self._context.get('type', False) == 'out_invoice' and base_product and not d.get('has_customer'):
#                     name = '[%s] %s' % (base_product.default_code, base_product.name)
#                 else:
#                    name = '[%s] %s' % (code, name)
#             return (d['id'], name)
#  
#         partner_id = self._context.get('partner_id')
#         if partner_id:
#             partner_ids = [partner_id, self.env['res.partner'].browse(partner_id).commercial_partner_id.id]
#         else:
#             partner_ids = []
# # 
# #         # all user don't have access to seller and partner
# #         # check access and use superuser
#         self.check_access_rights("read")
#         self.check_access_rule("read")
#         result = []
#         for product in self.sudo():
#             # display only the attributes with multiple possible values on the template
#             variable_attributes = product.attribute_line_ids.filtered(lambda l: len(l.value_ids) > 1).mapped('attribute_id')
#             variant = ' '
#  
#             name = variant and "%s %s" % (product.name, variant) or product.name
#             sellers = []
#             buyers = []
#             if partner_ids:
#                 sellers = [x for x in product.seller_ids if (x.name.id in partner_ids) and (x.product_id == product)]
#                 if not sellers:
#                     sellers = [x for x in product.seller_ids if (x.name.id in partner_ids) and not x.product_id]
#                 buyers = [x for x in product.product_customer_code_ids if (x.partner_id.id == partner_id) and (x.product_id == product.product_tmpl_id)]
#                 if not buyers:
#                     buyers = [x for x in product.product_customer_code_ids if (x.partner_id.id == partner_id) and not x.product_id.product_tmpl_id]
#             
#             if sellers:
#                 for s in sellers:
#                     seller_variant = s.product_name and (
#                         variant and "%s (%s)" % (s.product_name, variant) or s.product_name
#                         ) or False
#                     mydict = {
#                               'id': product.id,
#                               'name': seller_variant or name,
#                               'default_code': s.product_code or product.default_code,
#                               }
#                     temp = _name_get(mydict)
#                     if temp not in result:
#                         result.append(temp)
#             elif buyers:
#                 for b in buyers:
#                     mydict = {
#                               'id': product.id,
#                               'name': b.product_name or product.name,
#                               'default_code': b.product_code or product.default_code,
#                               'product_obj': product,
#                               'has_customer': True
#                               }
#                     result.append(_name_get(mydict))
#             else:
#                 mydict = {
#                           'id': product.id,
#                           'name': name,
#                           'default_code': product.default_code,
#                           }
#                 result.append(_name_get(mydict))
#         return result
#    
#     @api.model
#     def name_search(self, name='', args=None, operator='ilike',limit=80):
#         if not args:
#             args = []
#         res = super(ProductProduct, self).name_search(name, args=args,
#             operator=operator, limit=limit)
#         if not self._context:
#             context = {}
#         product_customer_code_obj = self.env['product.customer.code']
#         if not res:
#             ids = []
#             partner_id = self._context.get('partner_id', False)
#             if partner_id:
#                 id_prod_code = product_customer_code_obj.search([
#                     ('product_code', '=', name), ('partner_id', '=', partner_id)
#                     ], limit=limit)
#                  
#                 for ppu in id_prod_code:
#                     ids.append(ppu.product_id.id)
#             if ids:
#                 res = self.name_get()
#         return res