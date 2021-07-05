# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import base64
from collections import OrderedDict
import json
import base64
from collections import OrderedDict
from datetime import datetime

from odoo import http
from odoo.exceptions import AccessError, MissingError
from odoo.http import request, Response
from odoo.tools import image_process
from odoo.tools.translate import _
from odoo.addons.portal.controllers.portal import pager as portal_pager, CustomerPortal
from odoo.addons.web.controllers.main import Binary
import pdb
from datetime import datetime,timedelta
import datetime
from datetime import datetime


class CustomerPortal(CustomerPortal):
    def _prepare_home_portal_values(self, counters):
        values = super()._prepare_home_portal_values(counters)
        if 'purchase_line_count' in counters:
            values['purchase_line_count'] = request.env['purchase.order.line'].search_count([
                ('state', 'in', ['purchase', 'done', 'cancel'])
            ]) if request.env['purchase.order.line'].check_access_rights('read', raise_exception=False) else 0
        return values

    def _purchase_order_get_page_view_values(self, order, access_token, **kwargs):
        #
        def resize_to_48(b64source):
            if not b64source:
                b64source = base64.b64encode(Binary.placeholder())
            return image_process(b64source, size=(48, 48))

        values = {
            'order': order,
            'resize_to_48': resize_to_48,
        }
        return self._get_page_view_values(order, access_token, values, 'my_purchases_history', False, **kwargs)


    @http.route(['/my/purchase/line', '/my/purchase/line/page/<int:page>'], type='http', auth="user", website=True)
    def portal_my_purchase_order_lines(self, page=1, date_begin=None, date_end=None, sortby=None, filterby=None, **kw):
        values = self._prepare_portal_layout_values()
        PurchaseOrder = request.env['purchase.order.line']

        domain = []

        if date_begin and date_end:
            domain += [('create_date', '>', date_begin), ('create_date', '<=', date_end)]

        searchbar_sortings = {
            'date': {'label': _('Newest'), 'order': 'create_date desc, id desc'},
            'name': {'label': _('Name'), 'order': 'name asc, id asc'},
            'amount_total': {'label': _('Total'), 'order': 'amount_total desc, id desc'},
        }
        # default sort by value
        if not sortby:
            sortby = 'date'
        order = searchbar_sortings[sortby]['order']

        searchbar_filters = {
            'all': {'label': _('All'), 'domain': [('state', 'in', ['purchase', 'done', 'cancel'])]},
            'purchase': {'label': _('Purchase Order Line'), 'domain': [('state', '=', 'purchase')]},
            'cancel': {'label': _('Cancelled'), 'domain': [('state', '=', 'cancel')]},
            'done': {'label': _('Locked'), 'domain': [('state', '=', 'done')]},
        }
        # default filter by value
        if not filterby:
            filterby = 'all'
        domain += searchbar_filters[filterby]['domain']

        # count for pager
        purchase_line_count = PurchaseOrder.search_count(domain)
        # make pager
        pager = portal_pager(
            url="/my/purchase/line",
            url_args={'date_begin': date_begin, 'date_end': date_end, 'sortby': sortby, 'filterby': filterby},
            total=purchase_line_count,
            page=page,
            step=self._items_per_page
        )
        # search the purchase orders to display, according to the pager data
        orders = PurchaseOrder.search(
            domain,
            order=order,
            limit=self._items_per_page,
            offset=pager['offset']
        )
        request.session['my_purchases_history'] = orders.ids[:100]
        values.update({
            'date': date_begin,
            'orders': orders,
            'page_name': 'purchase',
            'pager': pager,
            'searchbar_sortings': searchbar_sortings,
            'sortby': sortby,
            'searchbar_filters': OrderedDict(sorted(searchbar_filters.items())),
            'filterby': filterby,
            'default_url': '/my/purchase/line',
        })
        return request.render("custom_purchase.portal_my_purchase_order_lines", values)

    @http.route(['/my/purchase/line<int:order_id>'], type='http', auth="public", website=True)
    def portal_my_purchase_order_line(self, order_id=None, access_token=None, **kw):
        try:
            order_sudo = self._document_check_access('purchase.order.line', order_id, access_token=access_token)
        except (AccessError, MissingError):
            return request.redirect('/my')

        report_type = kw.get('report_type')
        if report_type in ('html', 'pdf', 'text'):
            return self._show_report(model=order_sudo, report_type=report_type, report_ref='purchase.action_report_purchase_order', download=kw.get('download'))

        confirm_type = kw.get('confirm')
        if confirm_type == 'reminder':
            order_sudo.confirm_reminder_mail(kw.get('confirmed_date'))
        if confirm_type == 'reception':
            order_sudo._confirm_reception_mail()

        values = self._purchase_order_get_page_view_values(order_sudo, access_token, **kw)
        update_date = kw.get('update')
#         if update_date == 'True':
#             return request.render("purchase.portal_my_purchase_order_update_date", values)
        return request.render("custom_purchase.portal_my_purchase_order_line", values)
    
    def _bom_get_page_view_values(self, order, access_token, **kwargs):
        #
        def resize_to_48(b64source):
            if not b64source:
                b64source = base64.b64encode(Binary.placeholder())
            return image_process(b64source, size=(48, 48))

        values = {
            'order': order,
            'resize_to_48': resize_to_48,
        }
        return self._get_page_view_values(order, access_token, values, 'my_purchases_history', False, **kwargs)
    
    @http.route(['/my/bom/<int:order_id>'], type='http', auth="public", website=True)
    def portal_my_bom_line(self, order_id=None, access_token=None, **kw):
        try:
            order_sudo = self._document_check_access('purchase.order.line', order_id, access_token=access_token)
        except (AccessError, MissingError):
            return request.redirect('/my')

        report_type = kw.get('report_type')
        if report_type in ('html', 'pdf', 'text'):
            return self._show_report(model=order_sudo, report_type=report_type, report_ref='purchase.action_report_purchase_order', download=kw.get('download'))

        confirm_type = kw.get('confirm')
        if confirm_type == 'reminder':
            order_sudo.confirm_reminder_mail(kw.get('confirmed_date'))
        if confirm_type == 'reception':
            order_sudo._confirm_reception_mail()

        values = self._purchase_order_get_page_view_values(order_sudo, access_token, **kw)
        update_date = kw.get('update')

        return request.render("custom_purchase.portal_my_bom_line", values)
    
    @http.route('/purchase_order_line_get_details', type='http', auth="public", website=True)
    def purchase_order_line_get(self, **kw):
        results = []
        if 'wid' in kw:
            pline_id = kw.get("wid")            
            p_ref = request.env['purchase.order.line'].sudo().browse(int(pline_id))
            qty = str(p_ref.product_qty)  
            bqty = str(p_ref.balance_to_ship) 
            if p_ref.date_planned:
                ddate = str(p_ref.date_planned)
                ddate_ref = datetime.strptime(ddate, '%Y-%m-%d %H:%M:%S')
                res = ddate_ref.strftime('%d/%m/%Y %H:%M:%S')
                ddate = str(res)
            else:
                ddate = None
            product = p_ref.name
            bom = request.env['mrp.bom'].sudo().search([('product_tmpl_id', '=', p_ref.product_id.product_tmpl_id.id)], limit=1)
            
#             bom_liness = bom.bom_line_ids
#             bom_lines = []
#             for bom in bom_liness:
#                 dict = {'bproduct': bom.product_id.name,
#                         'bqty': bom.product_qty,
#                         'id': bom.id}
#                 bom_lines.append(dict)
            results.append({    'plineid': p_ref.id,
                                'purchase_order_id': p_ref.order_id.name,                                
                                'purchase_line_desc':p_ref.name,
                                'ordered_qty':qty,
                                'date_planned': ddate,
                                'bal_to_ship': bqty,
                            })
        return json.dumps(results)
    
    @http.route('/bom_line_get_details', type='http', auth="public", website=True)
    def bom_line_get(self, **kw):
        results = []
        if 'wid' in kw:
            pline_id = kw.get("wid")            
            p_ref = request.env['purchase.order.line'].sudo().browse(int(pline_id))
            bom = request.env['mrp.bom'].sudo().search([('product_tmpl_id', '=', p_ref.product_id.product_tmpl_id.id)], limit=1)
            bom_liness = bom.bom_line_ids
            bom_lines = []
            for bom in bom_liness:
                dict = {'bproduct': bom.product_id.name,
                        'bqty': bom.product_qty,
                        'id': bom.id}
                bom_lines.append(dict)
            if p_ref.product_id.product_tmpl_id.bracelet_extender == 'yes':
                extender = 'Yes'
            else:
                extender = 'No'
            if p_ref.product_id.product_tmpl_id.jtype == 'bracelet':
                jtype = 'Bracelet'
            if p_ref.product_id.product_tmpl_id.jtype == 'earring':
                jtype = 'Earring'
            if p_ref.product_id.product_tmpl_id.jtype == 'ring':
                jtype = 'Ring'
            if p_ref.product_id.product_tmpl_id.jtype == 'pendant':
                jtype = 'Pendant'
            if p_ref.product_id.product_tmpl_id.jtype == 'necklace':
                jtype = 'Necklace'
            if p_ref.product_id.product_tmpl_id.jtype == 'bangle':
                jtype = 'Bangle'
            if p_ref.product_id.product_tmpl_id.jtype == 'brooche':
                jtype = 'Brooche'
            results.append({    
                                'product': p_ref.name,
                                'polineid': p_ref.id,
                                'eprodid': p_ref.product_id.id,
                                'jtype': jtype,
                                'ejtype': jtype,
                                'rjtype': jtype,
                                'bracelet_clasp': p_ref.product_id.product_tmpl_id.bracelet_clasp.name,
                                'safety': p_ref.product_id.product_tmpl_id.bracelet_safety.name,
                                'extender': extender,
                                'bracelet_extender_length': p_ref.product_id.product_tmpl_id.bracelet_extender_length,
                                'trademark' : p_ref.product_id.product_tmpl_id.trademark.name,
                                'ear_clasp': p_ref.product_id.product_tmpl_id.ear_clasp.name,
                                'inside_dia': p_ref.product_id.product_tmpl_id.inside_dia,
                                'earring_drop_length': p_ref.product_id.product_tmpl_id.earring_drop_length,
                                'earring_drop_width': p_ref.product_id.product_tmpl_id.earring_drop_width,
                                'etrademark' : p_ref.product_id.product_tmpl_id.trademark.name,
                                'rtrademark' : p_ref.product_id.product_tmpl_id.trademark.name,
                                'eproduct': p_ref.product_id.name,
                                'rproduct': p_ref.name,
                                'shank_width': p_ref.product_id.product_tmpl_id.shank_width,
                                'pchain_length': p_ref.product_id.product_tmpl_id.chain_length,
                                'pchain_drop_length': p_ref.product_id.product_tmpl_id.chain_drop_length,
                                'pchain_type': p_ref.product_id.product_tmpl_id.chain_type.name,
                                'necklace_extender_length': p_ref.product_id.product_tmpl_id.necklace_extender_length,
                                'bangle_clasp': p_ref.product_id.product_tmpl_id.bangle_clasp.name,
                                'brooche_desc': p_ref.product_id.product_tmpl_id.brooche_desc,
#                                 'bom_lines': bom_lines
                            })
        return json.dumps(results)
    
    @http.route('/portal/purchaseline/get', type='http', auth="public", website=True, csrf=False)
    def save_purchase_line(self, **post):
        results = []
        values = {}
        pline_id = post['plineid']
        purchase_line = request.env['purchase.order.line'].sudo().browse(int(pline_id))
        if purchase_line:
            purchase_line.sudo().write({'qty_to_ship': post['qty_to_ship'], 'shipping_number': post['shipping_number']})
            if purchase_line.move_ids:
                for move in purchase_line.move_ids:
                    if move.state == 'assigned':
                        move.shipped_qty = post['qty_to_ship']
                        move.shipping_number = post['shipping_number']
            purchase_line.sudo().write({'qty_to_ship': 0.0, 'shipping_number': False})
        return self.portal_my_purchase_order_lines(page=1, date_begin=None, date_end=None, sortby=None, filterby=None, **post)

