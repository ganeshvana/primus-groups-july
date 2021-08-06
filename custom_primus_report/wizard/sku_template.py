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
        style_highlight = workbook.add_format({'bold': True, 'pattern': 1, 'bg_color': '#E0E0E0', 'align': 'center'})
        style_normal = workbook.add_format({'align': 'right'})
        style_footer = workbook.add_format({'bold': True, 'align': 'right'})
        row = 0
        col = 0
        active_ids = self._context['active_ids']            
        if active_ids:
            for rec in active_ids:                
                move = self.env['account.move'].browse(rec)
                data = {'context': {'tz': 'Asia/Kolkata', 'uid': 2, 'allowed_company_ids': [1]}, 'report_type': 'pdf'}
                cost = 0.0
                rows = []
                foot = []
                headers =[
                    "Vendor SKU",
                    "IMAGE  (if Avail)",
                    "METAL Type",
                    "Plating type",
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
                col = 0
                worksheet.write(row, col, "SKU Template", style_highlight)
                for header in headers:
                    worksheet.write(row, col, header, style_highlight)
                    worksheet.set_column(col, col, 30)
                    col += 1
        
                row = 1
                for line in move.invoice_line_ids:
                    col = 0
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
                    worksheet.write(row, col, line.product_id.default_code,style_normal)
                    col += 1
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

    
