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
import os.path
from os import path
from pathlib import Path
from pdf2docx import Converter

class SKUTemplateXl(models.TransientModel):
    _name = 'sku.tempalate.xl'
    _description = 'SKU Template Xl'
    
    xls_file = fields.Binary(string="XLS file")
    xls_filename = fields.Char()


    def action_generate_xls(self):
        home = str(Path.home())
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        worksheet = workbook.add_worksheet('SKU Template')
        worksheet.set_column(1, 1, 25)
        style_highlight = workbook.add_format({'bold': True, 'pattern': 1, 'bg_color': '#FFFFFF', 'align': 'center'})
        style_highlight.set_font_size(6)
        style_highlight.set_border(style=1)
        style_normal = workbook.add_format({'align': 'center'})
        style_normal.set_font_size(8)
        style_normal.set_border(style=2)
        row = 0
        col = 0
        cstone = cstonetrt = csshape = cs_origin = cs_minw = ''
        stone_count = ''
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
                'bg_color': '#34EBCD',
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
                merge_format2 = workbook.add_format({
                'bold': 1,
                'border': 1,
                'align': 'center',
                'valign': 'vcenter',
                'bg_color': '#34EB89',
                })
                merge_format2.set_font_size(8)
                row = 1
                hd_data = 'Column F should be filled in once selections are made and a buy proposal is sent to you.  Metal Gram Wts (Column E) are for pricing purposes. Minimum gram weights (Column F) are for SKU creation.  If a SKU comes in fingersizes or lengths, the minimum weight of the smallest size or length must be listed in column F.  Column M is the CT/CTW for pricing purposes, Column L is the lowest CT/CTW for Sku Creation purposes. '
                worksheet.set_row(row, 30)
                worksheet.write(row, col, hd_data, merge_format2)
                worksheet.merge_range('A2:S2', hd_data, merge_format2)
                row = 2
                col = 0
                
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
                
                for header in headers:
                    worksheet.write(row, col, header, style_highlight)
                    worksheet.set_column(col, col, 8)
                    col += 1
        
                row = 3
                col = 0
                merge_format3 = workbook.add_format({
                'bold': 1,
                'border': 1,
                'align': 'center',
                'valign': 'vcenter',
                'bg_color': '#34EBCD',
                })
                merge_format3.set_font_size(10)
                worksheet.write(row, col, 'Color', merge_format3)
                row = 4
                for line in order.order_line:
                    col = 0
                    worksheet.set_row(row, 50)
                    worksheet.write(row, col, line.product_id.default_code,style_normal)
                    col += 1
                    if line.product_id.image_1920:
                        binary_data = line.product_id.image_1920
                        mimetype = guess_mimetype(base64.b64decode(binary_data))
                        file_path = ""
                        if not os.path.exists(home + '/temp_files'):
                            os.makedirs(home + '/temp_files') 
                        if mimetype == 'image/png':
                            file_path = home + '/temp_files/' + str(line.product_id.name) + ".png"
                        elif mimetype == 'image/jpeg':
                            file_path = home + '/temp_files/' + str(line.product_id.name) + ".jpeg"
                    
                        if file_path:
                            with open(file_path, "wb") as imgFile:
                                imgFile.write(base64.b64decode(binary_data))
                        image_width = 150.0
                        image_height = 120.0
                        
                        cell_width = 75.0
                        cell_height = 60.0
                        
                        x_scale = cell_width/image_width
                        y_scale = cell_height/image_height
                        worksheet.insert_image(row, col, file_path, {'x_scale': x_scale, 'y_scale': y_scale})
                    col += 1
                    if line.product_id.bom_id_line:
                        qty = 0.0
                        metal = line.product_id.bom_id_line.filtered(lambda b: b.bom_line_type_id.name == 'Metal')
                        if metal:
                            for m in metal:
                                qty += metal.product_qty
                            metal = metal[0]
                            worksheet.write(row, col, metal.product_id.finess.code,style_normal)
                            col += 1
                            worksheet.write(row, col, metal.product_id.plating.code,style_normal)
                            col += 1
                            worksheet.write(row, col, qty,style_normal)
                            col += 1
                            worksheet.write(row, col, metal.min_weight,style_normal)
                            col += 1
                    center_stone = line.product_id.bom_id_line.filtered(lambda b: b.bom_line_type_id.name in ['Center Stone', 'Accent Stone 1', 'Accent Stone 2', 'Accent Stone 3', 'Accent Stone 4', 'Accent Stone 5', 'Accent Stone 6'])
                    stones = []
                    treatments = [] 
                    sorigins = []
                    shape = []
                    if center_stone:
                        center_stone_main = center_stone
                        cstone = cstonetrt = csshape = cs_origin = cs_minw = ''
                        stone_count = ''
                        for cs in center_stone:
                            if cs.product_id.stone_name_id not in stones:
                                stones.append(cs.product_id.stone_name_id)
                        for a in center_stone:
                            if a.product_id.stone_shape_id not in shape:
                                shape.append(a.product_id.stone_shape_id)
                        for sn in stones:   
                            center_stone = center_stone_main.filtered(lambda b: b.product_id.stone_name_id == sn)  
                            
                            if center_stone: 
                                cstone += sn.name + '\n'
                                cstonetrt += center_stone[0].product_id.treatment.name + '\n'
                                cs_origin += center_stone[0].product_id.stone_origin_id.name + '\n'
                                if len(shape) == 1:
                                    csshape += str(center_stone[0].product_id.size_length) + '*' + str(center_stone[0].product_id.size_width) + ' '+str(center_stone[0].product_id.stone_shape_id.code) + '\n'
                                else:
                                    csshape = 'Mix'
                                pq = sq = 0.0
                                for cs in center_stone:
                                    pq += cs.product_qty
                                    sq += cs.sec_quantity
                                cs_minw += str(sq) + '\n'
                                stone_count += str(pq) + '\n'
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
                    stones = treatments = sorigins = []
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
        
class DisclosureDoc(models.TransientModel):
    _name = 'disclosure.docx'
    _description = 'Disclosure Doc'
    
    def generate_disclosure_doc(self):
        home = str(Path.home())
        active_ids = self._context['active_ids']            
        if active_ids:
            for rec in active_ids:                
                invoice = self.env['account.move'].browse(rec)
                ir_action_report_obj = self.env['ir.actions.report']
                ir_action_report_ids = ir_action_report_obj.search([('report_name','=','custom_primus_report.report_treatment_disclosure_main')])
                model_ref = self.env['ir.model.data'].search([('res_id','=',ir_action_report_ids.id),('model','=','ir.actions.report')])
                pdf = self.env.ref(model_ref.module+"."+model_ref.name)._render_qweb_pdf(invoice.id)
                b64_pdf = base64.b64encode(pdf[0])
                file_name = ''                    
                # save pdf as attachment
                ATTACHMENT_NAME = 'INV' + '.pdf'
                str(ATTACHMENT_NAME).replace('/', '_')
                pdf_file =  self.env['ir.attachment'].create({
                    'name': ATTACHMENT_NAME,
                    'type': 'binary',
                    'datas': b64_pdf,
                    'res_model': self._name,
                    'res_id': self.id,
                    'mimetype': 'application/pdf',
                })
                file_path = ""
                if not os.path.exists(home + '/temp_files'):
                    os.makedirs(home + '/temp_files') 
                decoded = base64.b64decode(pdf_file.datas)
                temp_file_path = home + '/temp_files'
                file_path = temp_file_path+'/'+ ATTACHMENT_NAME
                temp_file = open(temp_file_path+'/'+ ATTACHMENT_NAME , 'wb')
                temp_file.write(decoded)
                temp_file.close()  
                pdf_fp = file_path.replace('pdf','docx')
#                 os.system('libreoffice --headless -convert-to -docx --outdir '+home + '/temporary_files'+ ' ' +file_path)
                pdf_file = '/path/to/sample.pdf'
                docx_file = temp_file_path+'/'+ 'INV.docx'
                
                # convert pdf to docx
                cv = Converter(file_path)
                cv.convert(docx_file)      # all pages by default
                cv.close()
                abspath = pdf_fp
                file = open(docx_file, "rb")
                out = file.read()
                datas = base64.b64encode(out)
                att_name = pdf_fp.split('/')
                att_name = invoice.name + '.docx'
                docx_files =  self.env['ir.attachment'].create({
                            'name': att_name[4],
                            'type': 'binary',
                            'datas': datas,
                            'res_model': self._name,
                            'res_id': self.id,
                        })
                
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')                 
        if base_url and docx_files:
            download_url = base_url + '/web/content/' + str(docx_files.id) + '?download=true'

        return {
            'type': 'ir.actions.act_url',
            'target': 'current',
            'url': download_url
            }
    
    

    
