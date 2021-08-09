# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import base64
import io

from collections import defaultdict
from dateutil.relativedelta import relativedelta
from lxml import etree

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from odoo.modules.module import get_resource_path
from odoo.tools.misc import xlsxwriter
from odoo.tools.mimetypes import guess_mimetype

class SKUTemplateXl(models.TransientModel):
    _name = 'sku.tempalate.xl'
    _description = 'SKU Template Xl'
    
    xls_file = fields.Binary(string="XLS file")
    xls_filename = fields.Char()


    def action_generate_xls(self):
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        worksheet = workbook.add_worksheet('SKU Template')
        worksheet.set_column(1, 1, 25)
        style_highlight = workbook.add_format({'bold': True, 'pattern': 1, 'bg_color': '#E0E0E0', 'align': 'center'})
        style_highlight.set_font_size(8)
        style_highlight.set_border(style=1)
        style_normal = workbook.add_format({'align': 'center'})
        style_normal.set_font_size(8)
        style_normal.set_border(style=2)
        row = 0
        col = 0
        active_ids = self._context['active_ids']            
        if active_ids:
            for rec in active_ids:                
                order = self.env['sale.order'].browse(rec)
                data = {'context': {'tz': 'Asia/Kolkata', 'uid': 2, 'allowed_company_ids': [1]}, 'report_type': 'pdf'}
                cost = 0.0
                rows = []
                foot = []
                merge_format = workbook.add_format({
                'bold': 1,
                'border': 1,
                'align': 'center',
                'valign': 'vcenter',
                })
                merge_format.set_font_size(9)
                style_normal.set_border(style=1)
                worksheet.merge_range('A1:B1', 'Merged Range', merge_format)
                col = 0
                worksheet.write(row, col, order.company_id.name, merge_format)
                col += 1
                worksheet.merge_range('D1:E1', 'Merged Range', merge_format)
#                 worksheet.write(row, col, order.date_order.strftime('%m/%d/%Y'), merge_format)
#                 col += 2
                worksheet.merge_range('D1:E1', order.date_order.strftime('%m/%d/%Y'), merge_format)
                worksheet.write(row, col, 'DIA  &  GEMSTONE  INFO', merge_format)
                worksheet.merge_range('H1:N1', 'DIA  &  GEMSTONE  INFO', merge_format)
                headers =[
                    "Vendor SKU",
                    "IMAGE  (if Avail)",
                    "METAL Type",
                    "Plating type",
                    "Metal Gram Weight",
                    "*Min gram Wt. Use smallest Size",
                    "MFG Country of Origin",
                    "Gem Type",
                    "Specify Treatment Type",
                    "MM Size and Shape",
                    "Stone Count",
                    "Min Carat Weight",
                    "Color and Dia CTWs",
                    "Stone Country of Origin",
                    "QTY Avail",
                    "JTV COST",
                    "P1",
                    "COMMENTS",
                    "Time needed to ship",
                ] 
                
                
                row = 1
                col = 0
                for header in headers:
                    worksheet.write(row, col, header, style_highlight)
                    worksheet.set_column(col, col, 8)
                    col += 1
        
                row += 1
                for line in order.order_line:
                    col = 0
                    worksheet.set_row(row, 25)
                    worksheet.write(row, col, line.product_id.default_code,style_normal)
                    col += 1
                    binary_data = line.product_id.image_1920
                    mimetype = guess_mimetype(base64.b64decode(binary_data))
                    file_path = ""
                    if mimetype == 'image/png':
                        file_path = "/home/rminds/temporary_files/" + str(line.product_id.name) + ".png"
                    elif mimetype == 'image/jpeg':
                        file_path = "/home/rminds/temporary_files/" + str(line.product_id.name) + ".jpeg"
                
                    if file_path:
                        with open(file_path, "wb") as imgFile:
                            imgFile.write(base64.b64decode(binary_data))
                    image_width = 140.0
                    image_height = 182.0
                    
                    cell_width = 64.0
                    cell_height = 20.0
                    
                    x_scale = cell_width/image_width
                    y_scale = cell_height/image_height
                    worksheet.insert_image(row, col, file_path, {'x_scale': x_scale, 'y_scale': y_scale})
                    col += 1
                    if line.product_id.bom_id_line:
                        metal = line.product_id.bom_id_line.filtered(lambda b: b.bom_line_type_id.name == 'Metal')
                        if metal:
                            metal = metal[0]
                            worksheet.write(row, col, metal.product_id.finess.code,style_normal)
                            col += 1
                            worksheet.write(row, col, metal.product_id.plating.code,style_normal)
                            col += 1
                            worksheet.write(row, col, metal.product_qty,style_normal)
                            col += 1
                            worksheet.write(row, col, metal.min_weight,style_normal)
                            col += 1
                    center_stone = line.product_id.bom_id_line.filtered(lambda b: b.bom_line_type_id.name == 'Center Stone')
                    if center_stone:
                        cstone = cstonetrt = csshape = cs_origin = cs_minw = ''
                        stone_count = ''
                        for cs in center_stone:
                            cstone += cs.product_id.stone_name_id.name + '\n'
                            cstonetrt += cs.product_id.treatment.name + '\n'
                            cs_origin += cs.product_id.stone_origin_id.name + '\n'
                            csshape += str(cs.product_id.size_length) + '*' + str(cs.product_id.size_width) + ' '+str(cs.product_id.stone_shape_id.code) + '\n'
                            cs_minw += str(cs.sec_quantity) + '\n'
                            stone_count += str(cs.product_qty) + '\n'
                        worksheet.write(row, col, line.product_id.country_origin.name, style_normal)    
                        col += 1
                        worksheet.write(row, col, cstone, style_normal)
                        col += 1
                        worksheet.write(row, col, cstonetrt, style_normal)
                        col += 1
                        worksheet.write(row, col, csshape, style_normal)
                        col += 1
                        worksheet.write(row, col, stone_count, style_normal)
                        col += 1
                        worksheet.write(row, col, '', style_normal)
                        col += 1
                        worksheet.write(row, col, cs_minw, style_normal)
                        col += 1
                        worksheet.write(row, col, cs_origin, style_normal)
                        col += 1
                    worksheet.write(row, col, str(line.product_uom_qty), style_normal)
                    col += 1    
                    worksheet.write(row, col, str(line.price_unit), style_normal)
                    col += 1    
                    worksheet.write(row, col, '', style_normal)
                    col += 1    
                    col += 1    
                    worksheet.write(row, col, str((order.date_order - order.expected_date).days), style_normal)
                    row += 1

        workbook.close()
        xlsx_data = output.getvalue()

        self.xls_file = base64.encodebytes(xlsx_data)
        self.xls_filename = "SKU_Template.xlsx"

        return {
            'type': 'ir.actions.act_window',
            'res_model': self._name,
            'view_mode': 'form',
            'res_id': self.id,
            'views': [(False, 'form')],
            'target': 'new',
        }

    
