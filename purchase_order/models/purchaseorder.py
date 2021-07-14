from odoo import api, fields, models
import logging
import requests, json, re

_logger = logging.getLogger(__name__)


class salesorderinherit(models.Model):
	_inherit = "purchase.order"

	Gold_Currency  = fields.Selection([
        ('USD', 'USD'),
        ('INR', 'INR'),
    ], required=True)
	Price_gold24  = fields.Float(string='Total-Price')
	Price_gold22  = fields.Float(string='Total-Price')
	Price_gold18  = fields.Float(string='Total-Price')
	Price_gold14  = fields.Float(string='Total-Price')
	Price_gold10  = fields.Float(string='Total-Price')
	Price_Silver  = fields.Float(string='Total-Price')
	Price_Platinum  = fields.Float(string='Total-Price')
	
	
	symbol  = 'AU,AG,PT'
	headers = {'Connection': 'keep-alive','sec-ch-ua': '^\\^',
		'Accept': '*/*',
		'sec-ch-ua-mobile': '?0',
		'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.101 Safari/537.36',
		'Origin': 'https://www.kitco.com',
		'Sec-Fetch-Site': 'same-site',
		'Sec-Fetch-Mode': 'cors',
		'Sec-Fetch-Dest': 'empty',
		'Accept-Language': 'en-GB,en-US;q=0.9,en;q=0.8',
	}
	params = (
	    ('market', '4'),
	    ('currency', 'USD,INR'),
	    ('unit', 'gram'),
	    ('df', '2'),
	    ('tf', '2'),
	    ('symbol', str(symbol)),
	)

	def generate_button(self,context=None):
		if self.Gold_Currency=='INR':

			response = requests.get('https://proxy.kitco.com/getPM', headers=self.headers, params=self.params)
			res = response.text

			gold_inr = re.search(r'AU,INR.*?\d+:\d+,(\d+.*?),\d+',res).group(1)
			sliver_inr = re.search(r'AG,INR.*?\d+:\d+,(\d+.*?),\d+',res).group(1)
			Platinum_inr = re.search(r'PT,INR.*?\d+:\d+,(\d+.*?),\d+',res).group(1)

			inr24 = gold_inr;self.Price_gold24 = inr24
			inr22 = float(gold_inr) * 22/24;self.Price_gold22 = inr22
			inr18 = float(gold_inr) * 18/24;self.Price_gold18 = inr18
			inr14 = float(gold_inr) * 14/24;self.Price_gold14 = inr14
			inr10 = float(gold_inr) * 10/24;self.Price_gold10 = inr10
			self.Price_Silver = sliver_inr
			self.Price_Platinum = Platinum_inr
		
		
		if self.Gold_Currency=='USD':
			response = requests.get('https://proxy.kitco.com/getPM', headers=self.headers, params=self.params)
			res = response.text

			gold_usd = re.search(r'AU,USD.*?\d+:\d+,(\d+.*?),\d+',res).group(1)
			sliver_usd = re.search(r'AG,USD.*?\d+:\d+,(\d+.*?),\d+',res).group(1)
			Platinum_usd = re.search(r'PT,USD.*?\d+:\d+,(\d+.*?),\d+',res).group(1)

			ca24 = gold_usd;self.Price_gold24 = ca24
			ca22 = float(gold_usd) * 22/24;self.Price_gold22 = ca22
			ca18 = float(gold_usd) * 18/24;self.Price_gold18 = ca18
			ca14 = float(gold_usd) * 14/24;self.Price_gold14 = ca14
			ca10 = float(gold_usd) * 10/24;self.Price_gold10 = ca10
			self.Price_Silver = sliver_usd
			self.Price_Platinum = Platinum_usd


		