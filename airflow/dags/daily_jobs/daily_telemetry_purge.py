import json
import os
import psycopg2
# import sys

# sys.path.append(os.path.dirname(__file__))

with open(os.path.dirname(os.path.abspath(__file__)) + '/' + 'config.json', 'r') as config_file:
    config = json.load(config_file)


def open_db_conn():
    conn = psycopg2.connect(
        host=config['database']['host'],
        port=config['database']['port'],
        user=config['database']['user'],
        password=config['database']['password'],
        database=config['database']['db']
    )

    return conn


def close_db_conn(conn):
    conn.close()


def perform_telemetry_purge():
    print('Performing telemetry purge...')
    print('Opening database connection...')
    conn = open_db_conn()
    conn.autocommit = False

    sql = config['sql']['daily_telemetry_purge']

    print('Creating database cursor...')
    cursor = conn.cursor()
    print('Executing SQL...')
    cursor.execute(sql)

    count = cursor.rowcount
    print('Purged {0} records...'.format(count))

    print('Committing changes...')
    # conn.rollback()
    conn.commit()
    print('Closing database connection...')
    close_db_conn(conn)
