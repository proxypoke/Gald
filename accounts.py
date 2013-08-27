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

    @property
    def name(self):
        c = database.cursor()
        # NOTE: it's ugly to duplicate this query in every property method, but
        # sqlite can't parameterize column names, and string formatting is
        # evil™. Thus, it's not possible to write a generic method to do this.
        return c.execute("SELECT Name FROM Accounts WHERE id = (?)",
                         (self.id,)).fetchone()["Name"]

    @name.setter
    def name(self, value):
        c = database.cursor()
        c.execute("UPDATE Accounts SET Name = ? WHERE Id = ?",
                  (value, self.id))

    @property
    def balance(self):
        c = database.cursor()
        return c.execute("SELECT Balance FROM Accounts WHERE id = (?)",
                         (self.id,)).fetchone()["Balance"]

    @balance.setter
    def balance(self, value):
        c = database.cursor()
        c.execute("UPDATE Accounts SET Balance = ? WHERE Id = ?",
                  (value, self.id))

# purely for convenience
new = Account.new
from_id = Account.from_id
