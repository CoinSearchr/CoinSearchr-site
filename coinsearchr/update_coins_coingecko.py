# Updates the Coin Gecko list of coins periodically

import pandas as pd
import numpy as np

import requests
import logging
import pangres
import datetime
import json

from ratelimit import limits, RateLimitException
from backoff import on_exception, expo
import re

from . import db, common

logger = logging.getLogger(__name__)

sql_engine = db.create_engine()

# API docs:
# https://www.coingecko.com/api/documentations/v3

@on_exception(expo, (RateLimitException, Exception), max_time=60, max_tries=10)
@limits(calls=50, period=60)
def call_api(url):
	response = requests.get(url)
	if response.status_code != 200:
		raise Exception(f'API response ({response.status_code}): {response.text}')
	return response.json()

def doCoinGeckoCoinListUpdate():
	logger.info('Starting CoinGecko coin list update.')
	coinsList: list = call_api('https://api.coingecko.com/api/v3/coins/list') # list of dicts of 10k coins; keys: id, symbol, name

	df = pd.DataFrame(coinsList)

	df['source'] = 'coingecko'
	df['date'] = datetime.datetime.now()

	df = df.set_index(['source', 'id'])

	pangres.upsert(sql_engine, df=df, table_name='coin_list', if_row_exists='update', create_schema=False, add_new_columns=False, adapt_dtype_of_empty_db_columns=False)


	logger.info('Done CoinGecko coin list update.')


def doCoinGeckoCoinListDetailedUpdate():
	logger.info('Starting CoinGecko coin list detailed update.')

	for currency in db.config['currencies'].keys(): # ['usd', ...]
		pageNum = 1
		while len(coinsList := call_api(f'https://api.coingecko.com/api/v3/coins/markets?vs_currency={currency}&order=market_cap_desc&per_page=240&page={pageNum}&sparkline=true&price_change_percentage=1h%2C24h%2C7d')) > 0:

			df = pd.DataFrame(coinsList)

			df['source'] = 'coingecko'
			df['date'] = datetime.datetime.now()
			df['base_currency'] = currency
			df['page_num'] = pageNum

			# parse date format
			date_cols = ['atl_date', 'ath_date', 'last_updated']
			df[date_cols] = df[date_cols].apply(pd.to_datetime)

			# change some int cols to floats for SQLite storage (avoids integer overflow error)
			float_cols = ['current_price', 'market_cap', 'fully_diluted_valuation', 'total_volume', 'high_24h', 'low_24h', 'price_change_24h', 'price_change_percentage_24h', 'market_cap_change_24h', 'market_cap_change_percentage_24h', 'circulating_supply', 'total_supply', 'max_supply', 'ath', 'ath_change_percentage', 'atl', 'atl_change_percentage', 'price_change_percentage_1h_in_currency', 'price_change_percentage_24h_in_currency', 'price_change_percentage_7d_in_currency']
			for col in float_cols:
				df[col] = pd.to_numeric(df[col], downcast='float')

			df = df.set_index(['source', 'base_currency', 'id'])

			df = df.drop(columns=['roi']) # try dropping that JSON column in case that's what's causing the overflow error, and to save space
			# TODO expand out 'roi' column from dict

			def apply_make_unicode_sparkline(sparkline: str, points_to_combine: int = 24, fine_points_to_keep: int = 168) -> str:
				"""
				# averaging guide: https://www.geeksforgeeks.org/averaging-over-every-n-elements-of-a-numpy-array/
				
				:param points_to_combine: how many points to combine into a single point (24 means every day turns into one bar)
				:param fine_points_to_keep: minimum number of un-averaged points to keep in generation
				"""
				data: list = sparkline['price'] # json.loads(sparkline_7d) [use json loads if from database]
				#data = [(x if pd.notna(x) else 0) for x in data]
				data = [0]*(fine_points_to_keep*2) + data # add a bunch before in case the sparkline isn't long enough
				#data = data[-common.round_down_to_nearest_multiple(len(data), points_to_combine):]
				data = data[-fine_points_to_keep:]
				if points_to_combine != 1:
					data_small = list(np.average(np.array(data).reshape(-1, points_to_combine), axis=1))
				else:
					data_small = data
				#print(f"data: {data}")
				#print(f"smal: {data_small}")
				return common.make_unicode_sparkline(data_small)
			df['sparkline_unicode_7d'] = df['sparkline_in_7d'].apply(lambda sparkline: apply_make_unicode_sparkline(sparkline, points_to_combine=12, fine_points_to_keep=168))
			df['sparkline_unicode_24h'] = df['sparkline_in_7d'].apply(lambda sparkline: apply_make_unicode_sparkline(sparkline, points_to_combine=1, fine_points_to_keep=24))

			df['high_7d'] = df['sparkline_in_7d'].apply(lambda x: 0 if len(x['price']) == 0 else max(x['price']))
			df['low_7d'] = df['sparkline_in_7d'].apply(lambda x: 0 if len(x['price']) == 0 else min(x['price']))

			df['num_id'] = df['image'].apply(lambda txt: common.extract_re(r'/coins/images/(\d+)/[a-zA-Z]', txt, 1))
			
			try:
				pangres.upsert(sql_engine, df=df, table_name='coin_list_detail', if_row_exists='update', create_schema=False, add_new_columns=False, adapt_dtype_of_empty_db_columns=False)
			except Exception as err:
				logger.error(f'Upsert failed. Error: {repr(err)}. Continuing to next set.')

			pageNum += 1

		logger.info(f'Done getting {pageNum-1} pages for {currency.upper()} exchange rates.')

	logger.info('Done CoinGecko coin list detailed update.')

def runAllCoinGeckoUpdates():
	logger.info('Starting full Coin Gecko update.')
	doCoinGeckoCoinListUpdate()
	doCoinGeckoCoinListDetailedUpdate()
	logger.info('Done full Coin Gecko update.')
	