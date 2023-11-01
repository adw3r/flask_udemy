import sqlite3

from flask import g

import settings


def connect_db():
    conn = sqlite3.connect(settings.SQLITE_DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def get_db():
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = connect_db()
    return g.sqlite_db
