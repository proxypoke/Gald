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


class Table(metaclass=ABCMeta):
    '''banana banana banana'''

    __initialized = False

    @classmethod
    def _init(cls):
        '''Initialize the table in the database.'''
        if cls.__initialized:
            return
        c = database.cursor()
        c.execute(database.load_schema(cls.__name__.lower()))
        c.close()
        database.commit()
        __initialized = True

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
        return c.execute("SELECT {} FROM {} WHERE id = ?".format(
                         column, self.__class__.__name__),
                         (self.id,)).fetchone()[0]

    def _set_query(self, column, value):
        '''Construct a setter query with sanitized inputs.'''
        column = column.lower()
        self._check_column(column)
        c = database.cursor()
        return c.execute("UPDATE {} SET {} = ? WHERE id = ?".format(
                         self.__class__.__name__, column), (value, self.id))
