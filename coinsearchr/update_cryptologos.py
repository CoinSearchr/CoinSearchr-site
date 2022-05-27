# Updates the list of CryptoLogos from cryptologos.cc (to get vector logos)

# Options of other sources in the future:
# - Poorly-Categorized Git repo: https://github.com/spothq/cryptocurrency-icons
# - Lookup by contract address (largely not SVG): https://github.com/dorianbayart/CryptoLogos
# - Maybe more options by searching "cryptocurrency logos github"

import pandas as pd
import requests
import logging
import pangres
import datetime
from ratelimit import limits, RateLimitException
from backoff import on_exception, expo
import re
from bs4 import BeautifulSoup

from . import db, common

logger = logging.getLogger(__name__)

sql_engine = db.create_engine()

class Error404(Exception):
	def __init__(self, message=""):
		super().__init__(message)

@on_exception(expo, (RateLimitException, Exception), max_time=240, max_tries=10)
@limits(calls=120, period=60) # arbitrary
def call_api(url: str) -> str:
	response = requests.get(url)
	if response.status_code == 404:
		raise Error404(f'API response ({response.status_code}) to {url}')
	elif response.status_code != 200:
		raise Exception(f'API response ({response.status_code}) to {url}: {response.text}')
	return response.content

def update_cryptologoscc_logos():
	logger.info('Starting cryptologos.cc logos update.')
	
	base_link = 'https://cryptologos.cc/'
	logo_list_html = call_api('https://gist.githubusercontent.com/CoinSearchr/6f5446c026d6f6c060bcbce830651d93/raw/cryptologoscc_scrape.html')
	# This gist must be manually updated with the latest rendered version of the website, copied out of Inspect Element.

	soup = BeautifulSoup(logo_list_html, 'html.parser')

	logos_list = []

	for a_tag in soup.find_all('a'):
		title_text = a_tag.find('div', {'class': 'div-middle-text'})

		# skip the links at the very top of the page that aren't for coins
		if title_text is None:
			continue

		next_page_url = base_link + a_tag['href']
		coin_page_html = call_api(next_page_url)
		coin_soup = BeautifulSoup(coin_page_html, 'html.parser')

		link = coin_soup.find('meta', {'name':'image', 'property':'image'})
		if link is None:
			continue
		else:
			link = link['content']
			if 'logo.png' not in link:
				continue
		link = link.replace('logo.png', 'logo.svg')

		logo_data = {
			'title_text': title_text.text,
			'link': link,
		}
		logos_list.append(logo_data)

		# DEBUG exit early
		#if len(logos_list) >= 10:
		#	break

	df = pd.DataFrame(logos_list)

	# extract name and symbol from text
	regex = re.compile(r'(.+) \((.+)\) logo')
	df['name'] = df['title_text'].apply(lambda x: common.extract_re(regex, x, 1))
	df['symbol'] = df['title_text'].apply(lambda x: common.extract_re(regex, x, 2))

	df['source'] = 'cryptologos.cc'
	df['priority'] = 1
	df['file_type'] = 'svg'
	df['date'] = datetime.datetime.now()

	def load_logo_contents(url: str) -> str:
		try:
			return call_api(url).decode('utf-8')
		except Error404:
			return None

	df['logo_contents'] = df['link'].apply(lambda url: load_logo_contents(url)) # TODO make this happen in parallel, maybe
	
	# filter out failed URL loads
	df = df[pd.notna(df['logo_contents'])]

	df = df.set_index(['name', 'symbol', 'source'])

	pangres.upsert(sql_engine, df=df, table_name='logo_list', if_row_exists='update', create_schema=False, add_new_columns=False, adapt_dtype_of_empty_db_columns=False)

	logger.info(f'Done cryptologos.cc logos update ({len(df.index)} logos).')


def run_logo_update():
	logger.info('Starting full logo update.')

	try:
		update_cryptologoscc_logos()
	except Exception as err:
		logger.error(f'Error running cryptologos.cc logo update: {err}.')
	
	logger.info('Done full logo update.')
	