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

import database
from abc import ABCMeta, abstractmethod


# type conversion map Python → SQLite
_typemap = {
    type(None): "NULL",
    int:        "INTEGER",
    float:      "REAL",
    str:        "TEXT",
    bytes:      "BLOB"}


class Table(metaclass=ABCMeta):
    '''banana banana banana'''

    # has the table been initialized in the database yet?
    __initialized = False

    def __init__(self, rowid):
        self._rowid = rowid

    @property
    def rowid(self):
        return self._rowid

    @classmethod
    def _init(cls):
        '''Create a table in the database from the class' attributes.'''
        if cls.__initialized:
            return

        # get the column names from the class' attributes
        cols = [var.lower() for var in dir(cls)
                # exclude private attributes
                if not var.startswith("_")
                # exclude methods
                and not hasattr(getattr(cls, var), "__call__")]
        typemap = {col: type(getattr(cls, col)) for col in cols}

        # begin constructing query & create all needed properties
        lines = []  # the lines inside the CREATE TABLE block
        for col, type_ in typemap.items():
            # do not process cls.rowid unless it was overwritten
            if col == "rowid" and type_ is property:
                continue
            # only process types which can be translated into SQLite types
            if not type_ in _typemap:
                raise TypeError(
                    "Invalid type for SQLite: {} (in attribute {})".format(
                        type_, col))
            lines.append("{} {}".format(col, _typemap[type_]))
            prop = property(
                lambda self: self._get_query(col),
                lambda self, val: self._set_query(col, val))
            setattr(cls, col, prop)
        query = "CREATE TABLE IF NOT EXISTS {} (\n".format(cls.__name__)
        query += ",\n".join(lines)
        query += " )"

        database.cursor().execute(query)
        cls.__initialized = True

    @classmethod
    @abstractmethod
    def new(cls, cols, vals):
        '''Create a new row in the appropriate table and return a new instance
        of the class.'''
        cls._init()
        for col in cols:
            cls._check_column(col)
        cols = "(" + ", ".join(cols) + ")"
        # construct the placeholders string
        plhs = "(" + ", ".join(["?" for _ in range(len(vals))]) + ")"
        query = 'INSERT INTO {} {} VALUES {}'.format(cls.__name__, cols, plhs)
        c = database.cursor()
        c.execute(query, vals)
        return cls(c.lastrowid)

    @classmethod
    def _check_column(cls, column):
        if column not in database.get_column_names(cls.__name__):
            raise ValueError("Invalid column name: {}".format(column))

    def _get_query(self, column):
        '''Construct a getter query with sanitized inputs.'''
        column = column.lower()
        self._check_column(column)
        c = database.cursor()
        return c.execute("SELECT {} FROM {} WHERE _rowid_ = ?".format(
                         column, self.__class__.__name__),
                         (self.id,)).fetchone()[0]

    def _set_query(self, column, value):
        '''Construct a setter query with sanitized inputs.'''
        column = column.lower()
        self._check_column(column)
        c = database.cursor()
        return c.execute("UPDATE {} SET {} = ? WHERE _rowid_ = ?".format(
                         self.__class__.__name__, column), (value, self.id))
