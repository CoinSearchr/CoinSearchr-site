# Run this file as a daemon. It will do everything necessary in the background and keep things going.
# Use manage.py to call this file.

import pandas as pd
import requests
import schedule
import time

import logging

from . import update_coins_coingecko

logger = logging.getLogger(__name__)

def run_tasks():

	logger.info('Starting all updates at the start.')
	update_coins_coingecko.runAllCoinGeckoUpdates()
	
	schedule.every(5).minutes.do(update_coins_coingecko.runAllCoinGeckoUpdates) # this long after the end of the previous 7-minute run
	# TODO consider upgrading to a threaded scheduler if we ever want concurrent execution

	while 1:
		schedule.run_pending()

		time.sleep(10)

