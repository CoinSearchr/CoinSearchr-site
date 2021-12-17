import re

def extract_re(regex, txt, group_number):
	s = re.search(regex, txt)
	try:
		return s.group(group_number)
	except:
		return None
	
