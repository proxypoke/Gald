#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Gald - a simple accounting tool
#
# Author: slowpoke <mail+git@slowpoke.io>
#
# This program is free software under the non-terms
# of the Anti-License. Do whatever the fuck you want.
#
# Github: https://www.github.com/proxypoke/Gald
# (Shortlink: https://git.io/gald)
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
    '''Create a new database connection.

    Arguments:
        file -- where to create the database. Uses a temporary file if None.
    '''
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


def get_table_names():
    '''Get a list of all table names.'''
    c = cursor()
    # The rows returned from sqlite_master look like this:
    # (type, name, tbl_name, rootpage, sql)
    return [row[0].lower() for row in
            # The second condition excludes all sqlite specific special tables.
            c.execute('''SELECT name FROM sqlite_master
                      WHERE type = "table"
                      AND name NOT LIKE "sqlite_%"''').fetchall()]


def get_column_names(table):
    '''Get the column names of a table.'''
    c = cursor()
    # sanitize the query
    if table.lower() not in get_table_names():
        raise ValueError("Invalid table name: {}".format(table))
    # table_info() returns rows with (cid, name, type, notnull, dflt_value, pk)
    return [row[1] for row in
            c.execute('''PRAGMA table_info({})'''.format(table)).fetchall()]
