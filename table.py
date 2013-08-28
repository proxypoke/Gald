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

    @classmethod
    @abstractmethod
    def new(cls):
        pass

    def _check_column(self, column):
        if column not in database.get_column_names(self.__class__.__name__):
            raise ValueError("Invalid column name: {}".format(column))

    def _get_query(self, column):
        '''Construct a getter query with sanitized inputs.'''
        self._check_column(column)
        c = database.cursor()
        return c.execute("SELECT {} FROM {} WHERE id = ?".format(
                         column, self.__class__.__name__),
                         (self.id,)).fetchone()[0]

    def _set_query(self, column, value):
        '''Construct a setter query with sanitized inputs.'''
        self._check_column(column)
        c = database.cursor()
        return c.execute("UPDATE {} SET {} = ? WHERE id = ?".format(
                         self.__class__.__name__, column), (value, self.id))
