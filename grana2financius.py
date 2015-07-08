#!/usr/bin/env python3
import json, argparse, os, time, io
from uuid import uuid4

basicColors = [-7617718,-16537100,-16121,-6543440,-43230,-12627531,-8825528,-14312668,-1762269]
inJSON = []

def outputname():
	if args.output:
		return args.output;
	fout = os.path.basename(args.input.name)
	if fout.startswith('Grana '):
		fout = fout.replace('Grana ', '')
	fout = 'Financius ' + fout.replace('grana', 'json')
	return io.open(fout,mode='w',encoding='UTF-8')
def GranaCategoryById(Id):
	for category in inJSON['categories']:
		if category['id'] == Id: 
			return category

if __name__ == "__main__":
	parser = argparse.ArgumentParser(description = 'Convert Grana backup to Financius backup')
	parser.add_argument('input', help = 'Path to Grana backup file', type=argparse.FileType('r'))
	parser.add_argument('-o', '--output', help = 'Path to Financius backup file', required=False, type=argparse.FileType('w'))
	args = parser.parse_args()
	inJSON = json.load(args.input)
	categories = {}
	account_id = str(uuid4())
	outJSON = {
		'version': 9,
		'timestamp': int(time.time()),
		'currencies': [{
			'id': str(uuid4()),
			"model_state": 1,
			"sync_state": 1,
			"code": "EUR",
			"symbol": "€",
			"symbol_position": 2,
			"decimal_separator": ",",
			"group_separator": " ",
			"decimal_count": 2
		}],
		'categories': [],
		'tags': [],
		'accounts': [{
	      "id": account_id,
	      "model_state": 1,
	      "sync_state": 1,
	      "currency_code": "EUR",
	      "title": "Main",
	      "note": "",
	      "balance": 0,
	      "include_in_totals": True
	    }],
	    'transactions': [],
	}
	i = 0
	for transaction in inJSON['transactions']:
		if not transaction['category_id'] in categories.keys():
			granaCategory = GranaCategoryById(transaction['category_id'])			
			category = {'name': granaCategory['name'].replace('category_', '').capitalize(), 'uuid': str(uuid4()), 'type': 1 if granaCategory['type'] == 0 else  2}
			categories[transaction['category_id']] = category
			outJSON['categories'].append({
				'id': category['uuid'],
				'model_state': 1,
				"sync_state": 1,
				"title": category['name'],
				"color": basicColors[i],
				"transaction_type": 1,
				"sort_order": 0
			})
			i=i+1
		category = categories[transaction['category_id']]
		outJSON['transactions'].append({
			"id": str(uuid4()),
			"model_state": 1,
			"sync_state": 1,
			"account_from_id": account_id if category['type'] == 1 else None,
			"account_to_id": account_id if category['type'] == 2 else None,
			"category_id": category['uuid'],
			"tag_ids": [],
			"date": transaction['date'],
			"amount": transaction['value'],
			"exchange_rate": 1.0,
			"note": transaction['note'],
			"transaction_state": 1,
			"transaction_type": category['type'],
			"include_in_reports": True
		})
		if category['type'] != 2:
			print(category['type'])
	# print(json.dumps(outJSON, indent=4))
	fOUT = outputname()
	fOUT.write(json.dumps(outJSON, indent=2))