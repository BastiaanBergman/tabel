About Tabel
============

Lightweight, intuitive and fast data-tables.

*Tabel* data-tables are tables with columns and column names, rows and row
numbers. Indexing and slicing your data is analogous to numpy array's. The
only real difference is that each column can have its own data type.


Design objectives
-----------------

  I got frustrated with pandas: it's complicated slicing syntax (.loc, .x,
  .iloc, .. etc), it's enforced index column and the Series objects I get when I
  want a numpy array. With Tabel I created the simplified pandas I need for many
  of my data-jobs. Just focussing on simple slicing of multi-datatype tables and
  basic table tools.

  * Intuitive simple slicing.

  * Using numpy machinery, for best performance, integration with other tools
    and future support.

  * Store data by column numpy arrays (column store).

  * No particular index column, all columns can be used as the index, the choice
    is up to the user.

  * Fundamental necessities for sorting, grouping, joining and appending tables.


Install
========



Quickstart
===========

init
----

To setup a Tabel:

  >>> from tabel import Tabel
  >>> tbl = Tabel([ ["John", "Joe", "Jane"],
  ...                [1.82,1.65,2.15],
  ...                [False,False,True]], columns = ["Name", "Height", "Married"])
  >>> tbl
   Name   |   Height |   Married
  --------+----------+-----------
   John   |     1.82 |         0
   Joe    |     1.65 |         0
   Jane   |     2.15 |         1
  3 rows ['<U4', '<f8', '|b1']

Alternatively, Tabels can be setup from dictionaries, numpy arrays, pandas
DataFrames and even single values, or no data at all. See the
:ref:`Initialization` for more examples. Database connectors usually return data
as a list of records, the module provides a convenience function to transpose
this into a list of columns :py:mod:`tabel.T`. Finally, data can be red from file:
:ref:`Reading`.

slice
-----

Slicing can be done the numpy way, always returning Tabel objects:

  >>> tbl[1:3,[0,2]]
   Name   |   Married
  --------+-----------
   Joe    |         0
   Jane   |         1
  2 rows ['<U4', '|b1']

Unless when,..

  1. explicitly one column is requested, a numpy array is returned:

    >>> tbl[1:3,'Name']       # doctest: +SKIP
    array(['Joe', 'Jane'],
          dtype='<U4')


  2. explicitly one row is requested, a tuple is returned:

    >>> tbl[0,:]
    ('John', 1.82, False)

  3. explicitly one element is requested:

    >>> tbl[0,'Name']
    'John'

In general, slicing is intuitive and does not deviate from what would expect
from numpy. With the one addition that columns can be referred to by names as
well as numbers. There is more examples in :ref:`Slicing`.

set
----

Setting elements works the same as slicing:

  >>> tbl = Tabel({'Name' : ["John", "Joe", "Jane"], 'Height' : [1.82,1.65,2.15], 'Married': [False,False,True]})
  >>> tbl[0,"Name"] = "Jos"
  >>> tbl
   Name   |   Height |   Married
  --------+----------+-----------
   Jos    |     1.82 |         0
   Joe    |     1.65 |         0
   Jane   |     2.15 |         1
  3 rows ['<U4', '<f8', '|b1']

The datatype that the value is expected to have, is the same as the datatype a
slice would result into. See more examples in :ref:`Setting`

Adding columns, works the same as setting elements, just give it a new name:

  >>> tbl = Tabel({'Name' : ["John", "Joe", "Jane"], 'Height' : [1.82,1.65,2.15], 'Married': [False,False,True]})
  >>> tbl['new'] = [1,2,3]
  >>> tbl
   Name   |   Height |   Married |   new
  --------+----------+-----------+-------
   John   |     1.82 |         0 |     1
   Joe    |     1.65 |         0 |     2
   Jane   |     2.15 |         1 |     3
  3 rows ['<U4', '<f8', '|b1', '<i8']

Or set the whole column to the same value:

  >>> tbl = Tabel({'Name' : ["John", "Joe", "Jane"], 'Height' : [1.82,1.65,2.15], 'Married': [False,False,True]})
  >>> tbl['new'] = 13
  >>> tbl
   Name   |   Height |   Married |   new
  --------+----------+-----------+-------
   John   |     1.82 |         0 |    13
   Joe    |     1.65 |         0 |    13
   Jane   |     2.15 |         1 |    13
  3 rows ['<U4', '<f8', '|b1', '<i8']

Just like numpy, slices are not actual copies of the data, rather they are
references. See :ref:`Referencing` for details.

append Tabel and row
---------------------

Tabels can be appended with other Tabels:

  >>> tbl = Tabel({'Name' : ["John", "Joe", "Jane"], 'Height' : [1.82,1.65,2.15], 'Married': [False,False,True]})
  >>> tbl += tbl
  >>> tbl
   Name   |   Height |   Married
  --------+----------+-----------
   John   |     1.82 |         0
   Joe    |     1.65 |         0
   Jane   |     2.15 |         1
   John   |     1.82 |         0
   Joe    |     1.65 |         0
   Jane   |     2.15 |         1
  6 rows ['<U4', '<f8', '|b1']

Or append rows as dictionary:

  >>> tbl = Tabel({'Name' : ["John", "Joe", "Jane"], 'Height' : [1.82,1.65,2.15], 'Married': [False,False,True]})
  >>> tbl.row_append({'Height':1.81, 'Name':"Jack", 'Married':True})
  >>> tbl
   Name   |   Height |   Married
  --------+----------+-----------
   John   |     1.82 |         0
   Joe    |     1.65 |         0
   Jane   |     2.15 |         1
   Jack   |     1.81 |         1
  4 rows ['<U4', '<f8', '|b1']

See :ref:`Appending` for more examples.

instance properties
--------------------

Your data is simply stored as a list of numpy arrays and can be accessed or
manipulated like that (just don't make a mess):

  >>> tbl = Tabel({'Name' : ["John", "Joe", "Jane"], 'Height' : [1.82,1.65,2.15], 'Married': [False,False,True]})
  >>> tbl.columns
  ['Name', 'Height', 'Married']
  >>> tbl.data        # doctest: +SKIP
  [array(['John', 'Joe', 'Jane'],
        dtype='<U4'), array([ 1.82,  1.65,  2.15]), array([False, False,  True], dtype=bool)]

Further the basic means to asses the size of your data:

  >>> tbl.shape
  (3, 3)
  >>> len(tbl)
  3

See :mod:`tabel.Tabel` for more details on the available properties.

pandas
-------

For for interfacing with the popular datatable framework, going back and forth
is easy:

  >>> import pandas as pd
  >>> df = pd.DataFrame({'a':range(3),'b':range(10,13)})
  >>> df
     a   b
  0  0  10
  1  1  11
  2  2  12

To make a Tabel from a DataFrame, just supply it to the initialize:

  >>> tbl = Tabel(df)
  >>> tbl
     a |   b
  -----+-----
     0 |  10
     1 |  11
     2 |  12
  3 rows ['<i8', '<i8']

The dict property of Tabel provides a way to make a DataFrame from a Tabel:

   >>> df = pd.DataFrame(tbl.dict)
   >>> df
      a   b
   0  0  10
   1  1  11
   2  2  12


Resources & getting help
==========================

 * See for the full API and more examples the documentation on `RTD <>`_.
 * The repository on bitbucket
 * Installables on pip
 * Questions and answers on `StackOverflow <https://stackoverflow.com/>`_, I
   will try to monitor for it.

Stable releases
================
None yet


Dependencies
============

* sys
* itertools
* numpy
* tabulate (optional, recommended)
* os (optional, for writing files)
* csv (optional, for writing csv files)
* gzip (optional, for zipping csv files)
* pandas (optional, for converting back and forth to DataFrames)

Tested on:
    * Python 2.7.14; numpy 1.14.0
    * Python 3.6.4;  numpy 1.14.3



Contributing to Tabel
=====================
Tabel is perfect already, no more contributions needed. Just kidding!

See the repository for filing issues and proposing enhancements.

I'm using pylint, pytest and sphynx.

Contributors
============
Just me, Bastiaan Bergman [Bastiaan.Bergman@gmail.com].


Release ToDo
============

* Make it pip/conda installable

* cleanup tabel.ipynb


What's in the name?
===================

*Tabel* /taːˈbɛl/ is Dutch for table (two-dimensional enlisting), `wiktionary
<https://nl.wiktionary.org/wiki/tabel>`_. The english word table, as in "dinner
table", translates in Dutch to *tafel*. The Dutch word *tafel* is an old
fashioned word for data-table, mostly used for calculation tables which itself
is old fashioned as well.


ToDo
=====

* polish error messages and validity checking and add testing for it.
* cashe buffers for faster appending: store temp in list and concatenate to
  array only once we use another method
* allow for (sparse) numpy arrays as an element
* adjust & limit __repr__ width in jupyter cell
* add plugins on readme page (https://github.com/AtomLinter/linter-pylint/blob/master/README.md)
* items() and row_items() and keys() and values() method
* pop_column method
* tox - environment testing
* set subsets of tabels with (subsets) of other tabels, seems logic as __setitem__ is
  allowed to provide the datatype that should have come from a __getitem__
* datetime column support
* read Tabel, column order for npz files not preserved (certainly on py2, possibly on py3)
* type conversion for columns containing numbers and empty strings when reading csv
* add disk datalogger
