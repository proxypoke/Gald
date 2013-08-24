#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sqlite3
import tempfile
import atexit


_conn = None


class DatabaseError(Exception):
    pass


def init(file=None):
    '''Create a new database connection.'''
    global _conn
    if _conn is not None:
        raise DatabaseError(
            "Refusing to reinitialize database. Close it first.")
    file = tempfile.mktemp() if file is None else file
    try:
        _conn = sqlite3.connect(file)
    except sqlite3.OperationalError:
        return False


@atexit.register
def close():
    '''Commit all pending changes and close the database.'''
    global _conn
    if _conn is None:
        return
    _conn.commit()
    _conn.close()
    _conn = None


def _conn_or_raise():
    if _conn is None:
        raise DatabaseError("No active connection. Have you called init?")


def cursor():
    '''Acquire a cursor for the current database connection.'''
    _conn_or_raise()
    return _conn.cursor()


def commit():
    '''Commit all changes to the current connectly connected database.'''
    _conn_or_raise()
    _conn.commit()


