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
import types
from abc import ABCMeta, abstractmethod


# type conversion map Python → SQLite
_typemap = {
    type(None): "NULL",
    int:        "INTEGER",
    float:      "REAL",
    str:        "TEXT",
    bytes:      "BLOB"}

class Constraint(metaclass=ABCMeta):
    '''Meta class for column constraints.'''

    @abstractmethod
    def __init__(self, type_or_val, keyword):
        self._default = None
        # see if we have a default value
        if type(type_or_val) in _typemap.keys():
            self._default = type_or_val
            type_or_val = type(type_or_val)
        # if the argument is a basic type, try to convert it to SQLite type and
        # construct a query with that type
        if type(type_or_val) is type:
            sqltype = Table._convert_or_raise(type_or_val)
            self._query = " ".join((
                "'{}'",
                sqltype,
                keyword))
        # otherwise, if it's a restriction, add its query to the current query
        elif isinstance(type_or_val, Constraint):
            self._query = "{} {}".format(type_or_val._query, keyword)
        # otherwise, tell the caller that it's doing bullshit
        else:
            raise TypeError(
                "Invalid type or value supplied: {}".format(type_or_val))
        # lastly, if there was a default value, add it to the query
        if self._default is not None:
            self._query = '{} DEFAULT "{}"'.format(self._query, self._default)

    def __call__(self, column):
        return self._query.format(column)


class Unique(Constraint):
    '''Used to create a column with the UNIQUE constraint.'''

    def __init__(self, type_or_val):
        super().__init__(type_or_val, "UNIQUE")


class PrimaryKey(Constraint):
    '''Used to create a column with the PRIMARY KEY constraint.'''

    def __init__(self, type_or_val):
        super().__init__(type_or_val, "PRIMARY KEY")


class NotNull(Constraint):
    '''Used to create a column with the NOT NULL constraint.'''

    def __init__(self, type_or_val):
        super().__init__(type_or_val, "NOT NULL")


class Table(metaclass=ABCMeta):
    '''A simple database abstraction layer.

    Table makes it possible to specify SQL tables and interact with them as
    Python classes and objects.

    To create a new table, subclass this class and specify the columns of the
    the as attributes of the class:

    class Foobar(Table):
        foo = str
        bar = int
        baz = 3.14159265
        spam = b'eggs'
        null = None

    As you can probably see, types of a table are specified either as a Python
    type (such as str) or inferred from their default values.

    Table currently support all types that SQLite supports. This is the
    conversion table:

        - NULL      ←→ None
        - INTEGER   ←→ int
        - REAL      ←→ float
        - TEXT      ←→ str
        - BLOB      ←→ bytes

    If a value is given instead of a type, then the type is inferred from that
    value, and it is used as the column's DEFAULT parameter.

    For example, specifying

        foo = str

    will result in this line in the schema:

        foo TEXT

    whereas

        foo = "bar"

    will generate this line:

        foo TEXT DEFAULT "bar"

    Support for things like PRIMARY KEY, AUTOINCREMENT, or UNIQUE are planned,
    but not yet implemented.
    '''

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
                and not (isinstance(getattr(cls, var), types.FunctionType)
                         or isinstance(getattr(cls, var), types.MethodType))]
        attrmap = {col: getattr(cls, col) for col in cols}

        # begin constructing query & create all needed properties
        lines = []  # the lines inside the CREATE TABLE block
        for col, attr in attrmap.items():
            # do not process cls.rowid unless it was explicitly overwritten
            if col == "rowid" and type(attr) is property:
                continue

            # only a type was given, create a column with no default value
            if type(attr) is type:
                lines.append(cls._make_column_by_type(col, attr))
            # otherwise, try to construct a column with default value
            else:
                lines.append(cls._make_column_by_value(col, attr))
            # finally, add the new column to the class as a property
            cls._add_prop(col)

        query = "CREATE TABLE IF NOT EXISTS {} (\n".format(cls.__name__)
        query += ",\n".join(lines)
        query += " )"
        # save the query for later review
        cls.__schema__ = property(lambda _: query)

        database.cursor().execute(query)
        cls.__initialized = True

    @classmethod
    def _add_prop(cls, col):
        '''Add a property to this class.'''
        prop = property(
            lambda self: self._get_query(col),
            lambda self, val: self._set_query(col, val))
        setattr(cls, col, prop)

    @classmethod
    def _make_column_by_type(cls, col, type_):
        '''Create a line for a CREATE TABLE query with only a type.'''
        t = cls._convert_or_raise(type_)
        return "{} {}".format(col, t)

    @classmethod
    def _make_column_by_value(cls, col, val):
        '''Create a line for a CREATE TABLE query with a default value.'''
        t = cls._convert_or_raise(type(val))
        return "{} {} DEFAULT {}".format(col, t, val)

    @staticmethod
    def _convert_or_raise(type_):
        '''Convert a type into a SQLite type if possible, else raise.'''
        if not type_ in _typemap:
            raise TypeError( "Invalid type for SQLite: {}".format(type_))
        return _typemap[type_]

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
    def from_id(cls, id):
        '''Create an object from an existing id in the database.'''
        c = database.cursor()
        # NOTE: for queries with a single ?-value, execute wants a string or a
        # sequence.
        row = c.execute("SELECT * FROM {} WHERE _rowid_ = ?".format(cls.__name__),
                        (id,)).fetchone()
        if row is None:
            raise IndexError("No such entry in the database.")
        return cls(id)

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
                         (self.rowid,)).fetchone()[0]

    def _set_query(self, column, value):
        '''Construct a setter query with sanitized inputs.'''
        column = column.lower()
        self._check_column(column)
        c = database.cursor()
        return c.execute("UPDATE {} SET {} = ? WHERE _rowid_ = ?".format(
                         self.__class__.__name__, column), (value, self.rowid))
