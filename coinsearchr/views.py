from flask import Flask, render_template, jsonify, request

from . import app
from . import searcher
from . import db

from math import log10, floor, isnan
import datetime, time
import humanize

@app.template_filter()
def format_currency_num(num: float) -> str:
	""" Formats numbers nicely of all orders of magnitude. """
	# TODO replace this with the humanize library
	def round_sig(x, sig=2):
		if x<=0 or not x or isnan(x):
			return x
		return round(x, sig-int(floor(log10(abs(x))))-1)

	def remove_dot0(num: float) -> str:
		num = str(num)
		if num.endswith('.0'):
			return num[:-2]
		return num

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

@app.route('/')
def index():
	return render_template("index.jinja2")

@app.route('/search', methods=['GET']) # args: q=search_term, json=true, currency=usd+, 
def search():
	arg_search_term = request.args.get('q', '')
	arg_currency = request.args.get('currency', 'usd').lower()

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

	if request.args.get('json', 'false').lower() == 'true':
		return jsonify(df.to_dict('records'))

	else:
		return render_template("search_results.jinja2", df=df, data=data)
		
