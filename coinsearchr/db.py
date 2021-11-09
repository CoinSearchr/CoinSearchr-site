import sqlalchemy
import os
from os.path import dirname, abspath, join
import yaml

# Database and Configuration

parentPath = dirname(dirname(abspath(__file__)))
configPath = join(parentPath, 'config.yaml')
with open(configPath) as stream:
    config = yaml.safe_load(stream)

max_query_results = config['search']['max_query_results']


def create_engine():
    assert config['database']['db_type'] == 'sqlite3' # no support for others, currently
    return sqlalchemy.create_engine('sqlite:///' + config['database']['db_path'])

