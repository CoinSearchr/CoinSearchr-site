import sqlite3
import db
import os.path

assert db.config['database']['db_type'] == 'sqlite3'
connection = sqlite3.connect(db.config['database']['db_path'])

schema_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'schema.sql')
with open(schema_file) as f: # TODO make it find this file no matter where the script is run from
    connection.executescript(f.read())

cur = connection.cursor()

connection.commit()
connection.close()
