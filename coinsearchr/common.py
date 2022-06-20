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
	
@on_exception(expo, (RateLimitException, Exception), max_time=5, max_tries=10)
def call_url_max5sec(url: str) -> requests.Response:
	response = requests.get(url)
	if response.status_code != 200:
		raise Exception(f'API response ({response.status_code}) to {url}: {response.text}')
	return response

bar = '▁▂▃▄▅▆▇█'
barcount = len(bar)
def make_unicode_sparkline(numbers: list) -> str:
	""" Make a sparkline from a list of numbers. https://rosettacode.org/wiki/Sparkline_in_unicode""" 
	mn, mx = min(numbers), max(numbers)
	extent = mx - mn
	if extent == 0:
		# if all the numbers are the same (i.e., min=max)
		if mn <= 0:
			char = bar[0]
		else:
			char = bar[int(barcount/2)]
		sparkline = (char) * len(numbers)
	else:
		sparkline = ''.join(
			bar[
				min(
					[barcount - 1,
					int((n - mn) / extent * barcount)]
				)
			] for n in numbers
		)
	#return mn, mx, sparkline
	return sparkline

def round_down_to_nearest_multiple(num, divisor):
    return num - (num%divisor)
