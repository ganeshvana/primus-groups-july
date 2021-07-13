from odoo import api, fields, models
import logging
from openerp.osv import fields, osv
import requests, json

_logger = logging.getLogger(__name__)


class solt_http_test(osv.osv):
    _name = 'solt.http.test'
    _columns = {
        'name': fields.char('URL', size=1024),
        'method': fields.selection([('post', 'POST'), ('get', 'GET'), ('put', 'PUT'), ('patch', 'PATCH'), ('delete', 'DELETE')], string='HTTP Method'),
    	'response': fields.text('Response'),
    }

    def action_request(self,response):
    	base_currency = 'USD'
    	symbol = 'USD'
    	endpoint = 'latest'
    	access_key = '2lgetx246ms21loy4luiv1k0pt4wz2vvrdz94f9avofigy9254qljilkbhsl'

    	headers = {'Content-Type': 'application/json', 'Accept': 'application/json'}
    	response = requests.get('https://metals-api.com/api/'+endpoint+'?access_key='+access_key+'&base='+base_currency+'&symbols='+symbol,headers=headers)
    	_logger.info("Responce : resp = %s" %response)
    	if response.status_code != 200:
    		# This means something went wrong
    		raise ApiError('GET /'+endpoint+'/ {}'.format(response.status_code))
    	response= response.json()
    	rates = response['rates']
    	price_inr = rates['INR']
    	_logger.info("price : Price = %s" %price_inr)
    	return True
solt_http_test()

# button action_request


# class salesorderinherit(models.Model):
#     _inherit = "sale.order"

#     Gold_Currency  = fields.Selection([
#         ('USD', 'USD'),
#         ('INR', 'INR'),
#     ], required=True, default='INR')
#     Price_gold24  = fields.Float(string='Total-Price')
#     Price_gold22  = fields.Float(string='Total-Price')
#     Price_gold18  = fields.Float(string='Total-Price')
#     Price_gold14  = fields.Float(string='Total-Price')
#     Price_gold10  = fields.Float(string='Total-Price')
#     Price_Silver  = fields.Float(string='Total-Price')
#     Price_Platinum  = fields.Float(string='Total-Price')

    
#     def generate_button(self,context=None):
#         if context is None:
#             context = 12
            
#             headers = {'Connection': 'keep-alive','sec-ch-ua': '^\\^',
#                 'Accept': '*/*',
#                 'sec-ch-ua-mobile': '?0',
#                 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.101 Safari/537.36',
#                 'Origin': 'https://www.kitco.com',
#                 'Sec-Fetch-Site': 'same-site',
#                 'Sec-Fetch-Mode': 'cors',
#                 'Sec-Fetch-Dest': 'empty',
#                 'Referer': 'https://www.kitco.com/charts/livegold.html',
#                 'Accept-Language': 'en-GB,en-US;q=0.9,en;q=0.8',
#             }

#             params = (
#                 ('market', '4'),
#                 ('currency', 'USD,INR'),
#                 ('unit', 'gram'),
#                 ('df', '2'),
#                 ('tf', '2'),
#                 ('symbol', 'AU'),
#             )
#             proxy  = "http://10.10.1.10:3128"

#             response = requests.get('https://proxy.kitco.com/getPM', headers=headers, params=params)
#             res = response.text
            
#             gold_inr = re.search(r'AU,INR.*?\d+:\d+,(\d+.*?),\d+',res).group(1)
#             gold_usd = re.search(r'AU,USD.*?\d+:\d+,(\d+.*?),\d+',res).group(1)



#             inr24 = gold_inr;self.Price_gold24 = inr24
#             inr22 = float(gold_inr) * 22/24;self.Price_gold22 = inr22
#             inr18 = float(gold_inr) * 18/24;self.Price_gold18 = inr18
#             inr14 = float(gold_inr) * 14/24;self.Price_gold14 = inr14
#             inr10 = float(gold_inr) * 10/24;self.Price_gold10 = inr10

#             ca24 = gold_usd;self.Price_gold24 = ca24
#             ca22 = float(gold_usd) * 22/24;self.Price_gold22 = ca22
#             ca18 = float(gold_usd) * 18/24;self.Price_gold18 = ca18
#             ca14 = float(gold_usd) * 14/24;self.Price_gold14 = ca14
#             ca10 = float(gold_usd) * 10/24;self.Price_gold10 = ca10

#         return True
        
   


	    