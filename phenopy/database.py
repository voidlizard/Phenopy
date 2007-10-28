from __future__ import with_statement
import psycopg2
import sys, os
from config import configuration
from contextlib import contextmanager

_connection = None

def connect():
    conf = configuration(os.environ['TRACKER_PROFILE'])
    return psycopg2.connect(conf.database)

def connection(new=False):
    global _connection
    if _connection is None:
        _connection = connect()
        _connection.set_isolation_level(0)

    if new:
        return connect()

    return _connection

@contextmanager
def transaction(conn):
    conn.set_isolation_level(2)
    try:
        yield None
    except:
        conn.rollback()
        raise
    else:
        conn.commit()
    finally:
        conn.close()

