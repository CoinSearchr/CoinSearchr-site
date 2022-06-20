# Search tools for the search engine


import pandas as pd


from . import db
from . import app

import time
import logging
logger = logging.getLogger(__name__)

sql_engine = db.create_engine()

def search_in_database(currency: str = 'usd', search_term: str = None, search_id: str = None) -> pd.DataFrame:
	""" Searches for a search term in the database. Returns all matching coins. """
	stime = time.time()

	if search_term:
		df = pd.read_sql_query(
			"""
			SELECT source, base_currency, id, symbol, name, image, current_price, market_cap, market_cap_rank, fully_diluted_valuation, 
				total_volume, high_24h, low_24h, high_7d, low_7d, price_change_24h, price_change_percentage_24h, market_cap_change_24h, market_cap_change_percentage_24h,
				circulating_supply, total_supply, max_supply, ath, ath_change_percentage, ath_date, atl, atl_change_percentage, atl_date, last_updated, 
				price_change_percentage_1h_in_currency, price_change_percentage_24h_in_currency, price_change_percentage_7d_in_currency, sparkline_unicode_7d, sparkline_unicode_24h, date, page_num
			FROM coin_list_detail
			WHERE ((name LIKE ? OR symbol LIKE ?) AND base_currency = ?)
			ORDER BY market_cap DESC LIMIT ? """,
			params = (
				'%' + search_term + '%',
				'%' + search_term + '%',
				currency,
				db.max_query_results
			),
			con=sql_engine
		)
	
	elif search_id:
		df = pd.read_sql_query(
			"""
			SELECT source, base_currency, id, symbol, name, image, current_price, market_cap, market_cap_rank, fully_diluted_valuation, 
				total_volume, high_24h, low_24h, high_7d, low_7d, price_change_24h, price_change_percentage_24h, market_cap_change_24h, market_cap_change_percentage_24h,
				circulating_supply, total_supply, max_supply, ath, ath_change_percentage, ath_date, atl, atl_change_percentage, atl_date, last_updated, 
				price_change_percentage_1h_in_currency, price_change_percentage_24h_in_currency, price_change_percentage_7d_in_currency, sparkline_unicode_7d, sparkline_unicode_24h, date, page_num
			FROM coin_list_detail
			WHERE (id = ? AND base_currency = ?)
			ORDER BY market_cap DESC LIMIT ? """,
			params = (
				search_id,
				currency,
				db.max_query_results
			),
			con=sql_engine
		)

	else:
		df = pd.read_sql_query(
			"""
			SELECT source, base_currency, id, symbol, name, image, current_price, market_cap, market_cap_rank, fully_diluted_valuation, 
				total_volume, high_24h, low_24h, high_7d, low_7d, price_change_24h, price_change_percentage_24h, market_cap_change_24h, market_cap_change_percentage_24h,
				circulating_supply, total_supply, max_supply, ath, ath_change_percentage, ath_date, atl, atl_change_percentage, atl_date, last_updated, 
				price_change_percentage_1h_in_currency, price_change_percentage_24h_in_currency, price_change_percentage_7d_in_currency, sparkline_unicode_7d, sparkline_unicode_24h, date, page_num
			FROM coin_list_detail
			LIMIT 0 """,
			con=sql_engine
		)
		
	app.logger.info(f'Database query took {(time.time() - stime)*1000:.0f}ms.')

	return df

def search_in_database_ranked(currency: str = 'usd', search_term: str = None, search_id: str = None) -> pd.DataFrame:
	""" Searches for a search term in the database, and adds a rank to each result. The rank is based on the closeness of the search and the value of the coin. """ 

	df = search_in_database(currency = currency, search_term = search_term, search_id = search_id)

	# FIXME implement ranking beyond just ordering by market cap
	#df = df.sort_values('market_cap', ascending=False).reset_index(drop=True)
	df['rank'] = df.index

	return df
	
def get_logo_from_database(name: str, symbol: str) -> dict:
	df = pd.read_sql_query(
		"""
		SELECT * FROM logo_list
		WHERE (name LIKE ? AND symbol LIKE ?)
		ORDER BY priority ASC
		LIMIT 1
		""",
		params = (
			name,
			symbol
		), # Note: Uses LIKE instead of '=' to avoid case-sensitive search
		con=sql_engine
	)

	if len(df.index) > 0:
		return df.iloc[0].to_dict()
	else:
		return {}
