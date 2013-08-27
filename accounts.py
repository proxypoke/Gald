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


def init():
    '''Initialize the accounts table.'''
    c = database.cursor()
    c.execute(database.load_schema("accounts"))
    c.close()
    database.commit()


class Account:
    '''Represents a single location of money.

    This can be a bank account, cash or savings.'''

    @classmethod
    def new(cls, name, balance=0):
        '''Create a new account in the database.'''
        c = database.cursor()
        c.execute('''INSERT INTO Accounts
                (name, balance) VALUES (?, ?)''', (name, balance))
        id = c.lastrowid
        return Account(id)

    @classmethod
    def from_id(cls, id):
        '''Create an account object from an existing id in the database.'''
        c = database.cursor()
        # NOTE: for queries with a single ?-value, execute wants a string or a
        # sequence.
        row = c.execute("SELECT * FROM Accounts WHERE Id = ?", (id,)).fetchone()
        if row is None:
            raise IndexError("No such entry in the database.")
        return Account(id)

    def __init__(self, id):
        self._id = id

    @property
    def id(self):
        return self._id

    @classmethod
    def _check_column(self, column):
        if column not in database.get_column_names("accounts"):
            raise ValueError("Invalid column name: {}".format(column))

    def _get_query(self, column):
        '''Construct a getter query with sanitized inputs.'''
        self._check_column(column)
        c = database.cursor()
        return c.execute("SELECT {} FROM Accounts WHERE id = ?".format(
                         column), (self.id,)).fetchone()[0]

    def _set_query(self, column, value):
        '''Construct a setter query with sanitized inputs.'''
        self._check_column(column)
        c = database.cursor()
        return c.execute("UPDATE Accounts SET {} = ? WHERE id = ?".format(
                         column), (value, self.id))

    @property
    def name(self):
        return self._get_query("Name")

    @name.setter
    def name(self, value):
        return self._set_query("Name", value)

    @property
    def balance(self):
        return self._get_query("Balance")

    @balance.setter
    def balance(self, value):
        self._set_query("Balance", value)


# purely for convenience
new = Account.new
from_id = Account.from_id
