# Run this file as a daemon. It will do everything necessary in the background and keep things going.

import pandas as pd
import requests
import schedule
import time

import logging

import update_coins_coingecko

logging.basicConfig(format='%(asctime)s :: %(name)s :: %(levelname)-8s :: %(message)s', level=logging.INFO)

logger = logging.getLogger(__name__)

if __name__ == '__main__':
	logger.info('Starting all updates at the start.')
	update_coins_coingecko.runAllCoinGeckoUpdates()
	
	schedule.every(10).minutes.do(update_coins_coingecko.runAllCoinGeckoUpdates)
	# TODO consider upgrading to a threaded scheduler if we ever want concurrent execution

	while 1:
		schedule.run_pending()

		time.sleep(1)
