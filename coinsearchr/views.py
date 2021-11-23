from flask import Flask, render_template, jsonify, request, make_response, url_for, send_from_directory

from . import app
from . import searcher
from . import db

from math import log10, floor, isnan
import datetime, time
import re
import os
import humanize
import pandas as pd

@app.template_filter()
def format_currency_num(num: float) -> str:
	""" Formats numbers nicely of all orders of magnitude. """
	# TODO replace this with the humanize library
	def round_sig(x, sig=2):
		if x<=0 or not x or isnan(x):
			return x
		return round(x, sig-int(floor(log10(abs(x))))-1)

	def remove_dot0(num: float) -> str:
		num_str = '{0:.12f}'.format(num) # avoid sci notation up to 20 places
		if num_str.lower() == 'nan':
			return '0'
		num_str = num_str.rstrip('0')
		if num_str.endswith('.'):
			num_str = num_str[:-1]
			if len(num_str) <= 2:
				num_str += '.0'
		return num_str

	num = round_sig(num, 3)
	if num > 1e12:
		return f'{remove_dot0(num/1e12)} T'
	if num > 1e9:
		return f'{remove_dot0(num/1e9)} B'
	if num > 1e6:
		return f'{remove_dot0(num/1e6)} M'
	if num > 1e3:
		return f'{remove_dot0(num/1e3)} k'
	return remove_dot0(num)

@app.template_filter()
def time_ago(date_time) -> str:
	# https://stackoverflow.com/a/11157649
	now = datetime.datetime.now()
	if type(date_time) is str:
		date_time = datetime.datetime.fromisoformat(date_time)
	dif = humanize.naturaldelta(now - date_time)
	if date_time <= now:
		return dif + ' ago'
	return 'in ' + dif # rare


bar = '▁▂▃▄▅▆▇█'
barcount = len(bar)
def sparkline(numbers: list) -> str:
	""" Make a sparkline from a list of numbers. https://rosettacode.org/wiki/Sparkline_in_unicode""" 
	mn, mx = min(numbers), max(numbers)
	extent = mx - mn
	sparkline = ''.join(bar[min([barcount - 1,
								 int((n - mn) / extent * barcount)])]
						for n in numbers)
	#return mn, mx, sparkline
	return sparkline

@app.context_processor
def inject_global_vars():
	""" These variables will be available in all templates. """
	return {
		'now': datetime.datetime.utcnow() # access with {{ now.year }}
	}

@app.route('/')
def index():
	return render_template("index.jinja2")



def search_ctrl(request_args, output_type):
	arg_search_term_orig = request.args.get('q') # required for 'sanity check' by browser in suggestion mode
	arg_search_term = arg_search_term_orig.strip() # clean
	arg_currency = request_args.get('currency', 'usd').lower().strip()

	# remove garbage from search request from the suggestions
	s = re.search(r'(.+)\s+[(].+[)] [|]', arg_search_term)
	try:
		arg_search_term = s.group(1)
	except:
		pass

	df = searcher.search_in_database_ranked(arg_search_term, arg_currency)
	# TODO check if currency is valid, default if it's not valid

	data = {
		'show_plus_on_result_count': '+' if len(df.index) >= db.max_query_results else '',
		'search_term': arg_search_term,
		'currency': arg_currency,
		'units_prefix': '',
		'units_suffix': '',
	}

	if arg_currency == 'usd':
		data['units_prefix'] = '$'
	else:
		data['units_suffix'] = arg_currency.upper()

	if output_type == 'json':
		return jsonify(df.to_dict('records'))

	elif output_type == 'html':
		return render_template("search_results.jinja2", df=df, data=data)

	elif output_type == 'suggest_json':
		df = df.head(5)

		if not df.empty:
			results = df.apply(lambda d: f"{d['name']} ({d['symbol'].upper()}) | {data['units_prefix']}{format_currency_num(d['current_price'])}{data['units_suffix']} | Mkt Cap: {data['units_prefix']}{format_currency_num(d['market_cap'])}{data['units_suffix']}", axis=1)
			results = results.to_list()
		else:
			results = []

		out = [
			arg_search_term_orig,
			results,
		]

		resp = make_response(jsonify(out))
		resp.headers['Content-Type'] = 'application/x-suggestions+json'
		return resp


@app.route('/search', methods=['GET']) # args: q=search_term, json=true, currency=usd+, 
def search():
	output_type = 'json' if request.args.get('json', 'false').lower() == 'true' else 'html'
	return search_ctrl(request.args, output_type)
	

@app.route('/suggest', methods=['GET']) # args: q=search_term
def suggest():
	"""
	Provide JSON search suggestions.

	Resources on Spec:
	- http://wiki.mozilla.org/Search_Service/Suggestions
	- Descriptor: https://github.com/dewitt/opensearch/blob/master/opensearch-1-1-draft-6.md#opensearch-11-parameters
	- https://developer.mozilla.org/en-US/docs/Web/OpenSearch
	"""
	return search_ctrl(request.args, 'suggest_json')

# @app.route('/coinsearchr-opensearch.xml')
# def opensearch_descriptor():
# 	# TODO optimize this with static file serving, but use the correct Content-Type
# 	resp = make_response(render_template('coinsearchr-opensearch.xml'))
# 	resp.headers['Content-Type'] = 'application/opensearchdescription+xml'
# 	return resp

@app.route('/convert')
def convert():
	# FIXME implement this Quick Convert page
	return render_template("index.jinja2")



@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static', 'img'), 'favicon.ico', mimetype='image/vnd.microsoft.icon')
