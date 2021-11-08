# Updates the Coin Gecko list of coins periodically

import pandas as pd
import requests
import logging
import pangres

import datetime

import db

logger = logging.getLogger(__name__)

sql_engine = db.create_engine()

# API docs: https://www.coingecko.com/api/documentations/v3

def doCoinGeckoCoinListUpdate():
    logger.info('Starting CoinGecko coin list update.')
    coinsList: list = requests.get('https://api.coingecko.com/api/v3/coins/list') # list of dicts of 10k coins; keys: id, symbol, name

    df = pd.DataFrame(coinsList)

    df['source'] = 'coingecko'
    df['date'] = datetime.datetime.now()

    df = df.set_index(['date', 'source', 'id'])

    pangres.upsert(engine=sql_engine, df=df, table_name='coin_list', create_schema=False, add_new_columns=False, adapt_dtype_of_empty_db_columns=False)


    logger.info('Done CoinGecko coin list update.')

