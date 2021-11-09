# Search tools for the search engine


import pandas as pd


from . import db

sql_engine = db.create_engine()

def search_in_database(search_term: str, currency: str = 'usd') -> pd.DataFrame:
	""" Searches for a search term in the database. Returns all matching coins. """

	df = pd.read_sql_query(
		'SELECT * FROM coin_list_detail WHERE ((name LIKE ? OR symbol LIKE ?) AND base_currency = ?) ORDER BY market_cap DESC LIMIT ?',
		params = (
			'%' + search_term + '%',
			'%' + search_term + '%',
			currency,
			db.max_query_results
		),
		con=sql_engine
	) # TODO union with exact matches so we can later place them first

	return df

def search_in_database_ranked(search_term: str, currency: str = 'usd') -> pd.DataFrame:
	""" Searches for a search term in the database, and adds a rank to each result. The rank is based on the closeness of the search and the value of the coin. """ 

	df = search_in_database(search_term, currency)

	# FIXME implement ranking beyond just ordering by market cap
	#df = df.sort_values('market_cap', ascending=False).reset_index(drop=True)
	df['rank'] = df.index

	return df
	