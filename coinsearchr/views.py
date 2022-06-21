# -*- coding: utf-8 -*-

from flask import Flask, render_template, jsonify, request, make_response, url_for, send_from_directory, redirect

from . import app, cache
from . import searcher
from . import db
from . import common

from math import log10, floor, isnan
import datetime, time
import re
import os
import humanize
import pandas as pd
import logging
import random
import cachetools

logger = logging.getLogger(__name__)

site_config = db.config['site']

recent_suggestions = cachetools.TTLCache(maxsize=5000, ttl=600) # Behaves like dict. key: the long-form suggestion string. value: the coin ID

@app.template_filter()
def format_currency_num(num: float) -> str:
	""" Formats numbers nicely of all orders of magnitude. """
	sigdigs = 5

	if num == 0 or pd.isna(num):
	 	return "0.00"

	if num < 1e-5:
		# sci notation (esp. for DOGE)
		return humanize.scientific(num, precision=sigdigs-1)
		# TODO improve the appearance of this sci notation with a better library

	if num > 1e6:
		return humanize.intword(num, "%0.3f")

	prec = (sigdigs-1) - floor(log10(num)) # prec = number of digits to include after decimal point
	prec = max(0, prec) # if prec < 0, set to 0 (i.e., if it's a very big number)

	if prec == 0:
		num = round(num) # required because of humanize.intcomma bug that doesn't do this rounding automatically

	# $120.1 looks too weird, so change to $120.12
	if prec == 1:
		prec = 2

	val = humanize.intcomma(num, prec) # prec >= 1; if prec=0, then no rounding is done

	if val.endswith('.0'):
		val = val[:-2]

	# print(f"{type(num)} {num} -> prec:{prec} -> {val}") # debugging
	return val

@app.template_filter()
def format_currency_num_old(num: float) -> str:
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
	if date_time is None:
		return '?'
	dif = humanize.naturaldelta(now - date_time)
	if date_time <= now:
		return dif + ' ago'
	return 'in ' + dif # rare

@app.template_filter()
def make_rank_text(rank) -> str:
	""" Makes text like `(#1)` or `(#inf)` from a rank, where rank is a float, int, or NaN. """
	if pd.isna(rank) or rank < 0.5:
		return "(#\u221e)"
	else:
		return f"(#{rank:,.0f})"

@app.template_filter('pluralize')
def pluralize(number, singular = '', plural = 's'):
	if number == 1:
		return singular
	else:
		return plural


@app.context_processor
def inject_global_vars():
	""" These variables will be available in all templates. """
	return {
		'now': datetime.datetime.utcnow() # access with {{ now.year }}
	}

@app.route('/')
@cache.cached(timeout=3600*24)
def index():
	return render_template("index.jinja2", site_config=site_config)



def search_ctrl(request_args, output_type):
	arg_search_term_orig = request.args.get('q', '') # required for 'sanity check' by browser in suggestion mode
	arg_search_term = arg_search_term_orig.strip() # clean
	arg_currency = request_args.get('currency', 'usd').lower().strip()
	arg_search_id = request.args.get('id', '')

	# check if currency is valid, default if it's not valid
	if arg_currency not in db.config['currencies'].keys():
		# invalid currency, assume 'usd'
		arg_currency = 'usd'

	# check to see if we're looking up a specific search result
	if arg_search_term in recent_suggestions.keys():
		arg_search_id = recent_suggestions[arg_search_term]
		arg_search_term = None # cancel the search by search term basically

	# early exit search results
	if arg_search_term and output_type == 'html':
		if 'Data out of date' in arg_search_term or arg_search_term.lower() == 'contact':
			return redirect(url_for('contact'), 302)
		if 'No results found' in arg_search_term or arg_search_term.lower() == 'home':
			return redirect(url_for('index'), 302)
		if arg_search_term.lower() == 'top':
			return redirect('https://coingecko.com/')


	coingecko_direct = 'https://coingecko.com/'
	if arg_search_term:

		# remove garbage from search request from the suggestions
		arg_search_term = arg_search_term.split(' (')[0]
		
		coingecko_direct = f'https://www.coingecko.com/en/search?query={arg_search_term}&utm_source=coinsearchr&utm_medium=search'
		if db.config['search']['disable_search_page'] and output_type == 'html':
			return redirect(coingecko_direct, 302)

		df = searcher.search_in_database_ranked(search_term=arg_search_term, currency=arg_currency)
		result_type = 'search'
	elif arg_search_id:
		coingecko_direct = f'https://www.coingecko.com/en/coins/{arg_search_id}?utm_source=coinsearchr&utm_medium=suggest'
		if db.config['search']['disable_search_page'] and output_type == 'html':
			return redirect(coingecko_direct, 302)

		df = searcher.search_in_database_ranked(search_id=arg_search_id, currency=arg_currency)
		result_type = 'id lookup'
	else:
		# no valid search term was given, error
		df = searcher.search_in_database_ranked(search_id=None, search_term=None, currency=None) # force getting an empty dataframe with the right cols to return no search results
		result_type = 'error'

	data = {
		'show_plus_on_result_count': '+' if len(df.index) >= db.max_query_results else '',
		'search_term': arg_search_term,
		'currency': arg_currency,
		'units_prefix': '',
		'units_suffix': '',
		'coingecko_direct': coingecko_direct,
		'result_type': result_type, # either 'search', 'id lookup', 'error'
	}

	data['units_prefix'] = db.config['currencies'][arg_currency]['prefix']
	data['units_suffix'] = db.config['currencies'][arg_currency]['suffix']

	if output_type == 'json':
		return jsonify(df.to_dict('records'))

	elif output_type == 'html':
		data['row_count'] = len(df.index)
		if len(df.index) > 0:
			top_row = df.iloc[0]
			df = df.iloc[1:] # remove first row
		else:
			top_row = None

		if (result_type == 'id lookup') and (data['row_count'] > 0):
			data['search_term'] = top_row['name'] + ' (' + top_row['symbol'].upper() + ')'
			
		return render_template("search_results.jinja2", df=df, data=data, trow=top_row, site_config=site_config)

	elif output_type == 'suggest_json':
		df = df.head(5)

		if not df.empty:
			suggestions = df.apply(lambda d: (re.sub(r'\s+', ' ',
			
			f"""
			{d['name']} ({d['symbol'].upper()}) | 
			{data['units_prefix']}{format_currency_num(d['current_price'])}{data['units_suffix']} | 
			Market Cap: {data['units_prefix']}{format_currency_num(d['market_cap'])}{data['units_suffix']}
			{make_rank_text(d['market_cap_rank'])} |
			7d: {data['units_prefix']}{format_currency_num(d['low_7d'])}{data['units_suffix']} to {data['units_prefix']}{format_currency_num(d['high_7d'])}{data['units_suffix']} {d['sparkline_unicode_7d']} |
			24h: {data['units_prefix']}{format_currency_num(d['low_24h'])}{data['units_suffix']} to {data['units_prefix']}{format_currency_num(d['high_24h'])}{data['units_suffix']} {d['sparkline_unicode_24h']}
			
			""").strip(), d['id']), axis=1) # 2-tuple of: (suggestion, id)

			# store the suggestions in the suggestion cache
			suggest_dict = {i[0]: i[1] for i in suggestions}
			recent_suggestions.update(suggest_dict)

			results = list(suggest_dict.keys())

			### Add on warning about it not being up-to-date if it's not
			latest_update = df['date'].max()
			tdelta = datetime.datetime.now() - latest_update
			if tdelta > datetime.timedelta(minutes=20):
				results = results[:4] # many browsers only show 5 "suggestions"
				results.append(f"⚠️ Warning: Data out of date. Data last updated {humanize.naturaltime(latest_update)}. Contact support (click here).")
				app.logger.info(f"Telling user that the data is out of date. Data last updated {humanize.naturaltime(latest_update)}.")
		else:
			results = ["No results found."]

		out = [
			arg_search_term_orig,
			results,
		]

		resp = make_response(jsonify(out))
		resp.headers['Content-Type'] = 'application/x-suggestions+json'
		return resp


@app.route('/search', methods=['GET']) # args: q=search_term, json=true, currency=usd+, 
@cache.cached(timeout=5, query_string=True)
def search():
	output_type = 'json' if request.args.get('json', 'false').lower() == 'true' else 'html'
	return search_ctrl(request.args, output_type)

# FIXME enable caching
@app.route('/logo', methods=['GET']) # args: id=coin_id
@cache.cached(timeout=3600*24, query_string=True)
def logo():
	""" Get logo based on ID. """
	arg_search_id = request.args.get('id')

	df = searcher.search_in_database(search_id=arg_search_id)

	def send_question_mark():
		with open(os.path.join(app.root_path, 'static', 'img', 'question-mark.svg'), 'rb') as fp:
			resp = make_response(fp.read())
			resp.headers['Content-Type'] = 'image/svg+xml'
			return resp

	if len(df.index) > 0:
		row = df.iloc[0]
	else:
		#raise Exception(f"Main database entry not found for id '{arg_search_id}'.")
		#return send_from_directory(os.path.join(app.root_path, 'static', 'img'), 'question-mark.svg', mimetype='image/svg+xml')
		return send_question_mark()

	# TODO do remapping here for ID's with different CoinGecko name/symbol than in the SVG database

	# try to get a vector logo from the SVG database
	logo_info: dict = searcher.get_logo_from_database(name = row['name'], symbol = row['symbol'])

	if logo_info:
		# found in database
		mimetype = 'image/svg+xml' if logo_info['file_type'] == 'svg' else 'svg' # TODO add support for other filetypes in the future
		
		resp = make_response(logo_info['logo_contents'])
		resp.headers['Content-Type'] = mimetype

	else:
		# must make call to CoinGecko

		if not row['image'].startswith('http'):
			# no logo available from CoinGecko, return a static question mark
			#return send_from_directory(os.path.join(app.root_path, 'static', 'img'), 'question-mark.svg', mimetype='image/svg+xml')
			return send_question_mark()

		# FIXME read from cache or similar (Issue #44)
		req = common.call_url_max5sec(row['image'])
		logger.info("Had to request a logo directly from CoinGecko at load time. This should be avoided because the database cache.")

		resp = make_response(req.content)
		resp.headers['Content-Type'] = req.headers.get('content-type')
	
	return resp

@app.route('/suggest', methods=['GET']) # args: q=search_term
@cache.cached(timeout=5, query_string=True)
def suggest():
	"""
	Provide JSON search suggestions.

	Resources on Spec:
	- http://wiki.mozilla.org/Search_Service/Suggestions
	- Descriptor: https://github.com/dewitt/opensearch/blob/master/opensearch-1-1-draft-6.md#opensearch-11-parameters
	- https://developer.mozilla.org/en-US/docs/Web/OpenSearch
	"""
	return search_ctrl(request.args, 'suggest_json')

@app.route('/convert')
def convert():
	# FIXME implement this Quick Convert page
	return render_template("index.jinja2", site_config=site_config)


@app.route('/contact')
@cache.cached(timeout=3600*24)
def contact():
	return render_template("contact.jinja2", site_config=site_config)


@app.route('/guide/firefox')
@cache.cached(timeout=3600*24)
def guide_firefox():
	return render_template("guide_firefox.jinja2", site_config=site_config)

@app.route('/guide/vivaldi')
@cache.cached(timeout=3600*24)
def guide_vivaldi():
	return render_template("guide_vivaldi.jinja2", site_config=site_config)


@app.route('/favicon.ico')
#@cache.cached(timeout=3600*24)
def favicon():
	return send_from_directory(os.path.join(app.root_path, 'static', 'img'), 'favicon.ico', mimetype='image/vnd.microsoft.icon')

@app.route('/robots.txt')
#@cache.cached(timeout=3600*24)
def robots_txt():
	return send_from_directory(os.path.join(app.root_path, 'static', 'other'), 'robots.txt', mimetype='text/plain')

@app.route('/privacy')
@app.route('/privacypolicy')
@app.route('/privacy-policy')
@cache.cached(timeout=3600*24)
def privacypolicy():
	return render_template("privacypolicy.jinja2", site_config=site_config)
