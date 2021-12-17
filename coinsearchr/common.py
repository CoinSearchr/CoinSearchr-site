import re
import requests

from ratelimit import limits, RateLimitException
from backoff import on_exception, expo


def extract_re(regex, txt, group_number):
	s = re.search(regex, txt)
	try:
		return s.group(group_number)
	except:
		return None
	
@on_exception(expo, (RateLimitException, Exception), max_time=20, max_tries=10)
def call_url_max20sec(url: str) -> requests.Response:
	response = requests.get(url)
	if response.status_code != 200:
		raise Exception(f'API response ({response.status_code}) to {url}: {response.text}')
	return response
