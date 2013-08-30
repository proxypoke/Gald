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


class Accounts(Table):
    '''Represents a single location of money.

    This can be a bank account, cash or savings.'''

    name = str
    balance = 0.0

    @classmethod
    def new(cls, name, balance=0):
        '''Create a new account in the database.'''
        return super().new(("name", "balance"), (name, balance))

# purely for convenience
new = Accounts.new
from_id = Accounts.from_id
