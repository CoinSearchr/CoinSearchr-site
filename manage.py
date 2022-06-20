#!/usr/bin/env python3

import logging

logging.basicConfig(format='%(asctime)s :: %(levelname)-8s :: %(name)s :: %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

from coinsearchr import tasks_daemon, init_db

import argparse

if __name__ == '__main__':
    logger.info('Starting manage.py.')

    parser = argparse.ArgumentParser()
    parser.add_argument('--action', '-a', help='Do this action', choices=['init_db', 'run_tasks'])
    args = parser.parse_args()

    if args.action == 'init_db':
        init_db.init_db()
        logger.info('Done init_db.')

    elif args.action == 'run_tasks':
        tasks_daemon.run_tasks()

    logger.info('Done manage.py.')