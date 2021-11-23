# Run this file as a daemon. It will do everything necessary in the background and keep things going.
# Use manage.py to call this file.

import pandas as pd
import requests
import schedule
import time

import logging

from . import update_coins_coingecko
from . import update_other_tasks

logger = logging.getLogger(__name__)

def run_tasks():

	logger.info('Starting all updates at the start.')
	update_other_tasks.do_delete_old_coin_rows()
	update_coins_coingecko.runAllCoinGeckoUpdates()
	
	schedule.every(5).minutes.do(update_coins_coingecko.runAllCoinGeckoUpdates) # this long after the end of the previous 7-minute run

	schedule.every(6).hours.do(update_other_tasks.do_delete_old_coin_rows)

	# TODO consider upgrading to a threaded scheduler if we ever want concurrent execution (Issue #5, partly)

	while 1:
		schedule.run_pending()

		time.sleep(10)

