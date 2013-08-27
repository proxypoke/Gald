#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sqlite3
import tempfile
import atexit
import os


_conn = None

SCHEMA_DIR = "schema"
SCHEMA_SUFFIX = ".sql"


class DatabaseError(Exception):
    pass


def init(file=None):
    '''Create a new database connection.'''
    global _conn
    if _conn is not None:
        raise DatabaseError(
            "Refusing to reinitialize database. Close it first.")
    file = tempfile.mktemp(prefix="gald_") if file is None else file
    try:
        _conn = sqlite3.connect(file)
        _conn.row_factory = sqlite3.Row
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


def load_schema(name):
    '''Load a schema for a table.'''
    try:
        filename = os.path.join(SCHEMA_DIR, name) + SCHEMA_SUFFIX
        with open(filename) as sfile:
            return sfile.read()
    except:
        raise DatabaseError("No such schema: {}.".format(name))
