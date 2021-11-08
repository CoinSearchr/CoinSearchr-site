# Run this file as a daemon. It will do everything necessary in the background and keep things going.

import pandas as pd
import requests

import logging

from . import update_coins_coingecko

logging.basicConfig(format='%(asctime)s :: %(name)s :: %(levelname)-8s :: %(message)s', level=logging.INFO)

logger = logging.getLogger(__name__)

update_coins_coingecko.doCoinGeckoCoinListUpdate()

