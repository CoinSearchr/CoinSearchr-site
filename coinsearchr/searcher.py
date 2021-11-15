# Search tools for the search engine


import pandas as pd


from . import db
from . import app

import time
import logging
logger = logging.getLogger(__name__)

sql_engine = db.create_engine()

def search_in_database(search_term: str, currency: str = 'usd') -> pd.DataFrame:
	""" Searches for a search term in the database. Returns all matching coins. """
	stime = time.time()

	df = pd.read_sql_query(
		"""
		SELECT source, base_currency, id, symbol, name, image, current_price, market_cap, market_cap_rank, fully_diluted_valuation, 
			total_volume, high_24h, low_24h, price_change_24h, price_change_percentage_24h, market_cap_change_24h, market_cap_change_percentage_24h,
			circulating_supply, total_supply, max_supply, ath, ath_change_percentage, ath_date, atl, atl_change_percentage, atl_date, last_updated, 
			price_change_percentage_1h_in_currency, price_change_percentage_24h_in_currency, price_change_percentage_7d_in_currency, date, page_num
		FROM coin_list_detail WHERE ((name LIKE ? OR symbol LIKE ?) AND base_currency = ?)
		ORDER BY market_cap DESC LIMIT ? """,
		params = (
			'%' + search_term + '%',
			'%' + search_term + '%',
			currency,
			db.max_query_results
		),
		con=sql_engine
	) # TODO union with exact matches so we can later place them first

	app.logger.info(f'Database query took {(time.time() - stime)*1000:.0f}ms.')

	return df

def search_in_database_ranked(search_term: str, currency: str = 'usd') -> pd.DataFrame:
	""" Searches for a search term in the database, and adds a rank to each result. The rank is based on the closeness of the search and the value of the coin. """ 

	df = search_in_database(search_term, currency)

	# FIXME implement ranking beyond just ordering by market cap
	#df = df.sort_values('market_cap', ascending=False).reset_index(drop=True)
	df['rank'] = df.index

	return df
	