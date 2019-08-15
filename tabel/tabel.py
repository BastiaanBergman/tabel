#!/usr/bin/env python
"""
.. module:: tabel.tabel
.. moduleauthor:: Bastiaan Bergman <Bastiaan.Bergman@gmail.com>

"""
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
import numpy as np
from .numpy_types import *                              # pylint: disable=wildcard-import
from .hashjoin import HashJoinMixin
from .util import ImpError, isstring

try:
    from tabulate import tabulate
except ImpError:
    def tabulate(tbl, columns=None, tablefmt=None):     # pylint: disable=unused-argument
        """Alt tabulate
        """
        outp = ""
        outp += " ".join(columns) + "\n"
        for r in tbl:
            outp += str(r) + "\n"
        return outp

try:
    import os
except ImpError as e:
    import warnings                             # pylint: disable=ungrouped-imports
    warnings.warn("Dependencies could not be loaded: {}".format(e))

try:
    import csv
except ImpError as e:
    import warnings                             # pylint: disable=ungrouped-imports
    warnings.warn("Dependencies could not be loaded: {}".format(e))

try:
    import gzip
except ImpError as e:
    import warnings
    warnings.warn("Dependencies could not be loaded: {}".format(e))

try:
    import pandas as pd     # to take pandas data and transform it to native
    PD_PRESENT = True
except ImpError:
    PD_PRESENT = False


def transpose(datastruct):
    """Transpose rows and columns.

    Convenience function. Usually DB connectors return data as a list of
    records, Tabel takes and internally stores data as a list of columns (column
    store). This function will transpose the list of records into a list of
    columns without a priori assuming anything about the datatype of each
    individual element.

    Arguments:
        datastruct (list):
            list or tuple containing lists or tuples with the data for each row.

    Returns:

        transposed datastruct, list containing lists with the data for each
        column.
    """
    shape = (len(datastruct), len(datastruct[0]))
    datastruct_out = [[] for i in range(shape[1])]      # pylint: disable=unused-variable
    for row in datastruct:
        assert len(row) == shape[1]
        for col, c in zip(datastruct_out, row):
            col.append(c)
    return datastruct_out


T = transpose
"""Convenience alias for :mod:`tabel.transpose`."""

class Tabel(HashJoinMixin):
    """Tabel datastructure

    Data table with rows and columns, rows are numbered columns are named. Each
    column has its own datatype. Data is stored by columns (column store), fixed
    datatype per column, varyiable datatypes from column to column.

    Parameters:
        datastruct (object) :
            list, tuple, ndarray or dict of lists, tuples, ndarrays or elements;
            or a `pandas.DataFrame`. List of columns of data. See :mod:`tabel.T` for
            a convenience function to transpose a list of records.
        columns (list of strings) :
            Column names, ignored when keys are part of the datastruct (dict and
            `pandas.DataFrame`). Automatic names are generated, if omitted, as
            strings of column number.
        copy (boolean) :
            Wether to make a copy of the data or to reference to the current
            memory location (when possible), default: True

    Notes:

        1. It is possible to create an empty Tabel instance and later add data
           using the :mod:`tabel.Tabel.append` and/or
           :mod:`tabel.Tabel.__setitem__` methods.

        2. It is possibe to add or manipulate data directly through the instance
           attributes :mod:`tabel.Tabel.columns` and :mod:`tabel.Tabel.data`. One
           could use the :mod:`tabel.Tabel.valid` method to check wether the
           manipulated structure is still valid.

        4. If one or more (but not all) of the columns contain a single element
           this element is repeated to match the length of the other columns.

    Examples:

        To initialize a Tabel, call the constructor with the data in column
        lists:

            >>> from tabel import Tabel
            >>> Tabel( [ ["John", "Joe", "Jane"],
            ...          [1.82, 1.65, 2.15],
            ...          [False, False, True] ],
            ...       columns = ["Name", "Height", "Married"])
             Name   |   Height |   Married
            --------+----------+-----------
             John   |     1.82 |         0
             Joe    |     1.65 |         0
             Jane   |     2.15 |         1
            3 rows ['<U4', '<f8', '|b1']

    """
    max_repr_rows = 20
    """int: Maximum number of rows to show when :func:`~tabel.Tabel.__repr__` is invoked."""
    repr_layout = 'presto'
    """string: The layout used with `tabulate` in the :func:`~tabel.Tabel.__repr__` method."""

    join_fill_value = {"float": np.nan, "integer": 999999, "string": ""}
    """dict: Fill vallues to be used when doing outer joins"""


    def __init__(self, datastruct=None, columns=None, copy=True):
        self.data = list()
        """list :
            numpy.ndarrays of the column data. Each array containing one column
            of data. Can be maniulated directly, if desired, as long as the
            structure remains valid within this framwork. Validity can be
            checked with the property :func:`~tabel.Tabel.valid`.
            """
        self.columns = list()
        """list :
            string names of columns. Can be maniulated directly, if desired, as
            long as the structure remains valid within this framwork. Validity
            can be checked with the method :func:`~tabel.Tabel.valid`.
            """
        if datastruct is not None:
            if hasattr(datastruct, "items"):
                datastruct_iter = datastruct.items()
            elif columns is not None:
                datastruct_iter = zip(columns, datastruct)
            elif len(datastruct):
                columns = [str(i) for i in range(len(datastruct))]
                datastruct_iter = zip(columns, datastruct)
            else:
                raise NotImplementedError("datastruct structure could not be resolved")

            stack = []
            for k, v in datastruct_iter:
                column = self._columnize(v, copy)
                self.columns.append(k)
                if len(column) == 1:
                    stack += [(k, v)]
                    self.data.append([])
                else:
                    self.data.append(column)

            for k, v in stack:
                column = self._columnize(v, copy)
                c = self.columns.index(k)
                self.data[c] = column

        if not self.valid:
            raise ValueError("Invalid Table created.")

    def _columnize(self, value, copy=True):
        if isstring(value) or (not hasattr(value, "__iter__")):
            value = [value] * max(1, len(self))
        return np.array(value, copy=copy)

    def row_append(self, row):
        """Append a row reccord at the end of the Tabel.

        Appending a single row at the end of the Tabel.

        Arguments:
            row (dict, list, tuple) :
                The row to be appended to the Tabel. If a dict is provided the
                keys should match the column names of the Tabel. If a list or
                tuple is provided the length and order should match the columns
                of the Tabel. columns do not need to match if the current Tabel
                has zero length.
        Returns:
            Nothing. Change in-place.
        """
        if len(self) == 0:
            self.__init__(row)
        elif hasattr(row, "items"):
            assert set(self.columns) == set(row), \
                "Not the same columns in Tabel: {} {}".format(self.columns, row.keys())
            for col, dta in row.items():
                ci = self.columns.index(col)
                self.data[ci] = np.concatenate([self.data[ci], np.array([dta])])
        elif len(row) == len(self.columns):
            for ci, dta in enumerate(row):
                self.data[ci] = np.concatenate([self.data[ci], np.array([dta])])
        else:
            raise ValueError("Number of elements in {row} not equal ".format(row=row),
                             "to number of columns in Tabel.")

        if not self.valid:
            raise ValueError("Invalid datastructure.")

    def append(self, tbl):
        """Append new Tabel to the current Tabel.

        Append a Tabel or pandas.DataFrame to the end of this Tabel. Each column
        is appended to each column of the instance invoking the method.

        Arguments:
            tbl (Tabel) :
                Tabel with the same columns as the current Tabel, order of
                columns does not need to match. Columns do not need to match if
                the current Tabel has zero length. Besides Tabel onjects
                pandas.DataFrame objects are also allowed.

        Returns:
            Nothing, change in-place.
        """
        if len(self) == 0 and isinstance(tbl, Tabel):
            self.__init__(tbl.data, columns=tbl.columns)

        elif len(self) == 0:
            self.__init__(tbl)

        elif isinstance(tbl, Tabel):
            assert set(self.columns) == set(tbl.columns), \
                "Not the same columns in Tabel: {} {}".format(self.columns, tbl.columns)
            for col, dta in zip(tbl.columns, tbl.data):
                ci = self.columns.index(col)
                self.data[ci] = np.concatenate([self.data[ci], dta])

        elif isinstance(tbl, pd.DataFrame):
            assert set(self.columns) == set(tbl), \
                "Not the same columns in Tabel: {} {}".format(self.columns, tbl.keys())
            for col, dta in tbl.items():
                ci = self.columns.index(col)
                self.data[ci] = np.concatenate([self.data[ci], dta])
        else:
            raise ValueError("Tabel type not recognized.")

        if not self.valid:
            raise ValueError("Invalid datastructure.")

    def __iadd__(self, other):
        self.append(other)
        return self

    def _column_index(self, c):
        if not isinstance(c, np.ndarray):
            try:
                return self.columns.index(c)
            except (TypeError, ValueError) as e:    # pylint: disable=unused-variable
                pass
            try:
                c = int(c)
                assert c < len(self.columns)
                return c
            except (TypeError, ValueError, AssertionError) as e:  # pylint: disable=unused-variable
                pass
        raise ValueError("Not a single, existing column: {}".format(c))

    def _column_indices(self, c):
        # Slice or ndarray of indices or booleans?
        if isinstance(c, (slice, np.ndarray)):
            try:
                c = np.arange(len(self.columns))[c]
                assert np.all(c < len(self.columns))
                return c
            except (ValueError, TypeError,              # pylint: disable=unused-variable
                    IndexError, AssertionError) as e:
                pass

        # Iterable with column names?
        try:
            return [self._column_index(ci) for ci in c]
        except (ValueError, TypeError) as e:        # pylint: disable=unused-variable
            raise ValueError("Not iterable or existing columns: {}".format(c))

    def __getitem__(self, key):
        """Indexing and slicing parts of a Tabel.

        Slicing and indexing mostly follows Numpy array and Python list
        conventions.

        Arguments:

            key (r, c):
                r can be a single integer, a boolean array, an integer itereable
                or a slice object. c can be a single integer or string, a
                boolean array, an integer or string itereable or a slice object.

            key (int or string) :
                When only a single int is supplied, it is considered to
                point to a whole single row.

                When only a single string is supplied, it is considered to
                point to a whole single column.

        Returns:

            Depending on key, four different types can be returned.

            element ():
                If both the row place and the column place are a single integer
                (or string for the column place), adressing a single element in
                the Tabel, wich could be of any datatype supported by
                Numpy.ndarray.
            column (ndarray):
                If the column place is a single string or integer, adressing a
                single column and the row place is either abscent or not an
                integer.
            row (tuple) :
                If the row place is a single integer, adressing a single row and
                the coumn place is either abscent or not a single integer/string.
            Tabel (Tabel) :
                If a tuple key (r, c) is provided with anything other than an
                integer for the row place and anything other than a single
                integer/string type for the column place.

    Notes:

        Returned Tabel objects from slicing are referenced to the original Tabel
        object unless row indexing was with a boolean list/array or the returned
        type was not a Tabel or np.ndarray object. Changes made to the slice
        will be reflected in the original Tabel. Appending or joining Tabels or
        adding/renaming columns will never be reflected in the original Tabel
        object. Use the `py:copy` function to make a full copy of the object.

    Raises:

        KeyError :
            When a key is referencing an invallid or not existing part of the data.

    Examples:

        >>> tbl[:, 1:3]
           Height |   Married
        ----------+-----------
             1.82 |         0
             1.65 |         0
             2.15 |         1
        3 rows ['<f8', '|b1']

        >>> tbl[0, 0]
        'John'
        >>> tbl["Name"]
        array(['John', 'Joe', 'Jane'], dtype='<U4')
        >>> tbl[0]
        ('John', 1.82, False)
        """
        # A whole single column?
        try:
            c = self.columns.index(key)
            return self.data[c]
        except (ValueError) as e:       # pylint: disable=unused-variable
            pass

        # A pair provided?
        try:
            (r, c) = key
            return self._getitem(r, c)
        except (ValueError, TypeError) as e:        # pylint: disable=unused-variable
            pass

        # A whole single row?
        try:
            r = int(key)
            return tuple(dt[r] for dt in self.data)
        except (ValueError, TypeError) as e:        # pylint: disable=unused-variable
            raise KeyError("Invalid key: {}".format(key))

    def _getitem(self, r, c):
        """Get item from row r and column c

        Arguments:
            r (int, iterable, slice) :
                The row number or numbers to be getting
            c (int, string, iterable, slice)
                The column to be getting
        Returns :

        """
        if not isinstance(r, np.ndarray):
            # Single element?
            try:
                r = int(r)
                c = self._column_index(c)
                return self.data[c][r]
            except (ValueError, TypeError) as e:        # pylint: disable=unused-variable
                pass

        # Single column?
        try:
            c = self._column_index(c)
            return self.data[c][r]
        except (ValueError, TypeError) as e:        # pylint: disable=unused-variable
            pass

        if not isinstance(r, np.ndarray):
            # Single row?
            try:
                r = int(r)
                c = self._column_indices(c)
                return tuple(self.data[ci][r] for ci in c)
            except (ValueError, TypeError) as e:        # pylint: disable=unused-variable
                pass

        # Requesting a sub-Tabel
        try:
            c = self._column_indices(c)
            columns = [self.columns[ci] for ci in c]
            data = [self.data[ci][r] for ci in c]
            return Tabel(data, columns, copy=False)
        except (ValueError, TypeError, KeyError) as e:      # pylint: disable=unused-variable
            raise KeyError("Invalid key provided: ({}, {})".format(r, c))

    def __setitem__(self, key, value):
        """Setting a slice of a Tabel

        Setting, like getting, slices mostly follows numpy conventions.
        Specifically the rules for the key are the same as for
        :mod:`tabel.Tabel.__getitem__` with the same relation between key and
        expected type for the value. In adition this method can also be used to
        add new columns.

        Arguments:

            key (r, c):
                r can be a single integer, a boolean array, an integer
                itereable or a slice object.

                c can be a single integer or string, a boolean array, an integer
                or string itereable or a slice object.

                To adress a single element in the Tabel object the key should be
                a tuple of (r, c) with r a single integer adressing the row and
                c a single integer or string addressing the column of the
                element to be changed.

            key (int or string):
                When only a single int is supplied, it is considered to
                point to a whole single row.

                When only a single string is supplied, it is considered to
                point to a whole single column.


            value (object):
                The type the value needs to have depends on the key provided.

                element:
                    A single element of the same type, or a type convertable to
                    the same, as the column targeted as a destination. See
                    :mod:`tabel.Tabel.dtype` to get the type of the columns.

                column :
                    An array or list of elements, each element of of the same
                    type, or a type convertable to the same, as the column
                    targeted as a destination. If a new column is targeted a
                    single element could be provided, in which case it will be
                    replicated along all rows.

                row :
                    A tuple of elements, each of the same type or a type
                    convertable to the same, as the column targeted as a
                    destination. Length of the tuple should match the number of
                    columns addressed.

                Tabel :
                    Not currently implemented.

        Returns:

            nothing, change in-place.

        Notes:

            When changing a column two syntaxes give approximately the same
            result, with, however, a noteable difference. Using a slice object
            ":" will change all elements of the column with the new element(s)
            provided. If just the colum name is provided, with no indication for row,
            than the whole column is replaced with the column provided.

                >>> tbl = Tabel( [ ["John", "Joe", "Jane"], [1.82, 1.65, 2.15],
                ...              [False, False, True] ], columns = ["Name", "Height", "Married"])
                >>> tbl[:, "Name"] = [1, 2, 3]
                >>> tbl
                   Name |   Height |   Married
                --------+----------+-----------
                      1 |     1.82 |         0
                      2 |     1.65 |         0
                      3 |     2.15 |         1
                3 rows ['<U4', '<f8', '|b1']
                >>> tbl["Name"] = [1, 2, 3]
                >>> tbl
                   Name |   Height |   Married
                --------+----------+-----------
                      1 |     1.82 |         0
                      2 |     1.65 |         0
                      3 |     2.15 |         1
                3 rows ['<i8', '<f8', '|b1']

            Note how in the first case the type of the name column stays "<U8"
            while seccond case the type of the Name column changes to "<i8".
        """
        # Replace whole single column?
        try:
            c = self.columns.index(key)
            self.data[c] = self._columnize(value)
            return
        except (ValueError) as e:                   # pylint: disable=unused-variable
            pass

        # Add new column?
        if isstring(key):
            self.columns.append(key)
            self.data.append(self._columnize(value))
            return

        # A pair provided?
        try:
            (r, c) = key
            self._setitem(r, c, value)
            return
        except (ValueError, TypeError) as e:        # pylint: disable=unused-variable
            pass

        # Change whole single row?
        try:
            r = int(key)
            assert len(value) == len(self.columns), \
                "Value iterable does not match number of columns."
            for i, v in enumerate(value):
                self.data[i][r] = v
            return
        except (ValueError, TypeError) as e:        # pylint: disable=unused-variable
            raise KeyError("Invalid key: {}".format(key))

    def _setitem(self, r, c, value):
        """Set item on row r and column c.

        Arguments:
            r (int, iterable, slice) :
                The row number or numbers to be getting
            c (int, string, iterable, slice)
                The column to be getting
        Returns :
            Nothing
        """
        # Single element?
        try:
            r = int(r)
            c = self._column_index(c)
            self.data[c][r] = value
            return
        except (ValueError, TypeError) as e:        # pylint: disable=unused-variable
            pass

        # Single column?
        try:
            c = self._column_index(c)
            self.data[c][r] = value
            return
        except (ValueError, TypeError) as e:        # pylint: disable=unused-variable
            pass

        # Single row?
        try:
            r = int(r)
            c = self._column_indices(c)
            assert len(c) == len(value), \
                "Data does not match the addressed row: {}, {}".format(c, value)
            for ci, v in zip(c, value):
                self.data[ci][r] = v
            return
        except (ValueError, TypeError) as e:        # pylint: disable=unused-variable
            pass

        # A Tabel?
        try:
            self[r, c]                            # pylint: disable=pointless-statement
            NotImplementedError(("Setting Tabel slices with Tabel ",
                                 "slice is not yet implemented."))
        except (ValueError, TypeError, KeyError) as e:      # pylint: disable=unused-variable
            pass

        raise KeyError("Invalid key provided: ({}, {})".format(r, c))

    def __delitem__(self, key):
        """Deleting rows or columns from a Tabel.

        Deleting rows or columns can be done using the del keyword.

        Arguments:
            key (int, list of ints, slice or string):

                If the key is a single integer, a list of integers or a slice
                object, then the specified rows will be removed from the Tabel.

                If the key is a single string, then the specified column will be
                removed from the Tabel.

        Returns:

            nothing, change in-place.

        Raises:

            IndexError:
                When key is an integer or list of integers that references an
                invalid row.

                Note that no exception is thrown if key is a slice object that
                refers to one or more invalid rows.

            ValueError:
                When key is a string that references an invalid column.

        Notes:

            Because Tabel stores data by columns, this operation requires
            creating new numpy arrays for all columns in the Tabel.

            Examples:
        >>> tbl = Tabel( [ ["John", "Joe", "Jane"], [1.82, 1.65, 2.15],
        ...              [False, False, True] ], columns = ["Name", "Height", "Married"])
        >>> del tbl["Name"]
        >>> del tbl[0]
        >>> tbl
           Height |   Married
        ----------+-----------
             1.65 |         0
             2.15 |         1
        2 rows ['<f8', '|b1']
        >>> del tbl[0:2]
        >>> tbl
         Height   | Married
        ----------+-----------
        0 rows ['<f8', '|b1']
        >>> del tbl['Married']
        >>> tbl
         Height
        ----------
        0 rows ['<f8']
        """

        # If we are passed a string, we try to delete a column with that name
        if isstring(key):
            c = self.columns.index(key)
            self.columns.pop(c)
            self.data.pop(c)
        else: # otherwise try to delete rows using numpy.delete()
            for i in range(len(self.data)):
                self.data[i] = np.delete(self.data[i], key)

    def __len__(self):
        if self.data:
            return max([len(dt) for dt in self.data])
        return 0

    @property
    def shape(self):
        """Tabel shape.

        Returns:

            tuple (r, c) with r the number of rows and c the number of columns.
        """
        if self.data:
            return len(self.data[0]), len(self.data)
        return (0, 0)

    def __repr__(self):
        """Pretty print using tabulate.

        Examples:
            >>> tbl = Tabel( [ ["John", "Joe", "Jane"], [1.82, 1.65, 2.15],
            ...          [False, False, True] ], columns = ["Name", "Height", "Married"])
            >>> tbl
             Name   |   Height |   Married
            --------+----------+-----------
             John   |     1.82 |         0
             Joe    |     1.65 |         0
             Jane   |     2.15 |         1
            3 rows ['<U4', '<f8', '|b1']

        """
        tabl = tabulate([[c[r] for c in self.data]
                         for r in range(min(len(self), self.max_repr_rows))],
                        self.columns, tablefmt=self.repr_layout)
        len_str = "\n{} rows".format(len(self))
        typ_str = " {}".format([dt.dtype.descr[0][1] for dt in self.data])
        return tabl + len_str + typ_str

    @property
    def dtype(self):
        """List of dtypes of the data columns.
        """
        return np.dtype([(c, dt.dtype) for c, dt in zip(self.columns, self.data)])

    def astype(self, dtypes):
        """Returns a type-converted tabel.

        Converts the tabel according to the provided list of dtypes and returns
        a new Tabel instance.

        Arguments:

            dtypes (list) :
                list of valid numpy dtypes in the order of the columns. List
                should have same length as number of columns present (see
                `Tabel.shape`) See Tabel.dtype for the current types of the
                Tabel.

        Returns:

            Tabel object with the columns converted to the new dtype.

        Examples:

        """
        return Tabel({k: v.astype(dty) for k, v, dty in zip(self.columns, self.data, dtypes)})

    @property
    def dict(self):
        """Dump all data as a dict of columns.

        Keywords are the column names and values are the column Numpy.ndarrays.
        Usefull when transferring to a pandas DataFrame.
        """
        return {k: v for k, v in zip(self.columns, self.data)}

    @property
    def valid(self):
        """Check wether the current datastructure is legit.

        Returns:
            (bool) True if the Tabel internal structure is valid.

        Notes:
            This is currently checking for the length of the columns to be the
            same and the number of the columns to be the same as the number of
            column names.
        """
        wid_chk = (len(self.columns) == len(self.data))
        len_chk = (np.all([len(d) == len(self.data[0]) for d in self.data]))
        return wid_chk and len_chk

    def sort(self, columns):
        """Sort the Tabel.

        Sorting in-place the Tabel according to columns provided. Rows always stay together,
        just the order of rows is affectd.

        Arguments:
            columns (string or list) :
                column name or column names to be sorted, listed in-order.

        returns:
            Nothing. Sorting in-place.

        Examples:
            >>> tbl = Tabel({'a':['b', 'g', 'd'], 'b':list(range(3))})
            >>> tbl.sort('a')
            >>> tbl
             a   |   b
            -----+-----
             b   |   0
             d   |   2
             g   |   1
            3 rows ['<U1', '<i8']
        """
        columns = columns if hasattr(columns, '__iter__') and not isstring(columns) else [columns]
        ind = np.lexsort([self.data[self.columns.index(c)] for c in columns])
        for i in range(len(self.columns)):
            self.data[i] = self.data[i][ind]

    def save(self, filename, fmt='auto', header=True):
        """Save to file

        Saves the Tabel data including a header with the column names to a file
        of the specified name in the current directory or the directory
        specified.

        Arguments:
            filename (str) :
                filename, should include path

            fmt (str) :
                formatting, valid values are: 'auto', 'csv', 'npz', 'gz'

                ``auto`` :
                    Determine the filetype from the fiel extension.
                ``csv`` :
                    Write to csv file using pythons `csv` module.
                ``gz`` :
                    Write to csv using pythons `csv` module and zip using
                    standard `gzip` module.
                ``npz`` :
                    Write to compressed `numpy` native binary format.

            header (bool) :
                whether to write a header line with the column names, only used for
                csv and gz

        Returns:
            Nothing.
        """
        if fmt == 'auto':
            fmt = os.path.splitext(filename)[1].replace('.', '')

        if fmt == 'csv':
            with open(filename, 'w') as f:
                self._write_csv(f, header)

        elif fmt == "gz":
            with gzip.open(filename, 'wt') as f:
                self._write_csv(f, header)

        elif fmt == 'npz':
            np.savez_compressed(filename, **{k: v for k, v in zip(self.columns, self.data)})

        else:
            raise ValueError("Only formats supported: csv, npz, gz")

    def _write_csv(self, f, header=True):
        """Writing csv filesself.

        Arguments:
            f (object) :
                file handle
            header (bool) :
                whether to write the columns header
        """
        writer = csv.writer(f)
        if header:
            writer.writerow(self.columns)
        writer.writerows(zip(*self.data))


def read_tabel(filename, fmt='auto', header=True):
    """Read data from disk

    Read data from disk and return a Tabel object.

    Arguments:
        filename (str) :
            filename sring, including path and extension.
        fmt (str) :
            format specifier, supports: 'csv', 'npz', 'gz'.
        header (bool) :
            whether to expect a header (True) or not (False) or try to sniff
            (None), only used for csv and gz

    Returns:
        Tabel object containing the data.
    """
    if fmt == 'auto':
        fmt = os.path.splitext(filename)[1].replace('.', '')
    if fmt == "csv":
        with open(filename, 'r') as f:      # , newline=""
            data = _read_csv(f, header)
    elif fmt == "gz":
        with gzip.open(filename, 'rt') as f:
            data = _read_csv(f, header)
    elif fmt == "npz":
        reader = np.load(filename)
        columns = reader.keys()
        datastruct = [reader[k] for k in columns]
        data = dict(datastruct=datastruct, columns=columns)
    else:
        raise ValueError("Only formats supported: csv, npz, gz")
    return Tabel(**data)


def _read_csv(f, header=True):
    """Reading csv.
    Arguments:
        f (object) :
            filehandle to ope file
        header (bool, None) :
            whether to expect a header (True) or not (False) or try to sniff
            (None), only used for csv and gz

    returns (dict) :
        dictionary containing the data
    """
    dialect, sniff_header = _csv_sniff(f)
    reader = csv.reader(f, dialect)
    columns = next(reader)
    if header is None:
        header = sniff_header
    if not header:
        columns = [str(i) for i in range(len(columns))]
        f.seek(0)
    datastruct = [[] for i in range(len(columns))]
    for row in reader:
        for data_col, c in zip(datastruct, row):
            data_col.append(c)
    np_types = NP_INT_TYPES + NP_FLOAT_TYPES
    datastruct = list(map(np.array, datastruct))
    for i, data_col in enumerate(datastruct):
        for np_type in np_types:
            try:
                datastruct[i] = data_col.astype(np_type)
            except ValueError:
                continue
            break
    data = dict(datastruct=datastruct, columns=columns)
    return data


def _csv_sniff(f):
    """
    Sniff using csv module whether or not a csv file (csv or gz) has a header.

    Arguments:
        f (filehandle) :
            filehandle of the file to be read
    """
    sniff_size = 2**20 - 1
    dialect = csv.Sniffer().sniff(f.read(sniff_size))
    f.seek(0)
    has_header = csv.Sniffer().has_header(f.read(sniff_size))
    f.seek(0)
    return dialect, has_header
