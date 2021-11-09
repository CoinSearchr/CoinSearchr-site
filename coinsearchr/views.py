from flask import Flask, render_template, jsonify, request

from . import app
from . import searcher
from . import db

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
    }

    if request.args.get('json', 'false').lower() == 'true':
        return jsonify(df.to_dict('records'))

    else:
        return render_template("search_results.jinja2", df=df, data=data)
        
