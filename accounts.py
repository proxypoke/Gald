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
from table import Table


def init():
    '''Initialize the accounts table.'''
    c = database.cursor()
    c.execute(database.load_schema("accounts"))
    c.close()
    database.commit()


class Accounts(Table):
    '''Represents a single location of money.

    This can be a bank account, cash or savings.'''

    @classmethod
    def new(cls, name, balance=0):
        '''Create a new account in the database.'''
        return super().new(("name", "balance"), (name, balance))

    @classmethod
    def from_id(cls, id):
        '''Create an account object from an existing id in the database.'''
        c = database.cursor()
        # NOTE: for queries with a single ?-value, execute wants a string or a
        # sequence.
        row = c.execute("SELECT * FROM Accounts WHERE Id = ?", (id,)).fetchone()
        if row is None:
            raise IndexError("No such entry in the database.")
        return Accounts(id)

    def __init__(self, id):
        super().__init__()
        self._id = id

    @property
    def id(self):
        return self._id

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
new = Accounts.new
from_id = Accounts.from_id
