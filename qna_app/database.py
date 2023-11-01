import sqlite3

from flask import g

import settings


class DbRow(sqlite3.Row):
    def __repr__(self):
        return f'{type(self).__name__}({dict(self)})'


def connect_db():
    conn = sqlite3.connect(settings.SQLITE_DB_PATH)
    conn.row_factory = DbRow
    return conn


def get_db():
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = connect_db()
    return g.sqlite_db


def init():
    db = get_db()
    with open('schema.sql', encoding='utf-8') as file:
        sql_stmnt = file.read()
    db.executescript(sql_stmnt)
    db.commit()
    db.close()
