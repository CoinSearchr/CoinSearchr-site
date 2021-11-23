# Does other repetitive tasks in the background

import logging

from . import db

logger = logging.getLogger(__name__)

sql_engine = db.create_engine()

def do_delete_old_coin_rows():
	""" Delete old rows from coins list tables. """
	logger.info('Starting do_delete_old_coin_rows.')
	
	for table in ['coin_list', 'coin_list_detail']:
		sql_engine.execute(f"DELETE FROM {table} WHERE date <= date('now', '-7 day') ORDER BY date ASC LIMIT 100")
	
	logger.info('Done do_delete_old_coin_rows.')

