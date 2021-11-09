import sqlite3
import os.path

from . import db

def init_db():
    assert db.config['database']['db_type'] == 'sqlite3'
    connection = sqlite3.connect(db.config['database']['db_path'])

    schema_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'schema.sql') # find the schema file, no matter the CWD [in the parent to this file]
    with open(schema_file) as f:
        connection.executescript(f.read())

    cur = connection.cursor()

    connection.commit()
    connection.close()

if __name__ == '__main__':
    init_db()
