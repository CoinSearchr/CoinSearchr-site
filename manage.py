from coinsearchr import tasks_daemon, init_db

import argparse

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--action', '-a', help='Do this action', choices=['init_db', 'run_tasks'])
    args = parser.parse_args()

    if args.action == 'init_db':
        init_db.init_db()

    elif args.action == 'run_tasks':
        tasks_daemon.run_tasks()

        