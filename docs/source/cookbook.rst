========
Cookbook
========

Initialization
===============
API documentation: :mod:`tabel.Tabel`.

From a list of lists and a separate list of column names:

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

From a dictionary:

  >>> data = {'Name' : ["John", "Joe", "Jane"],
  ...               'Height' : [1.82,1.65,2.15],
  ...               'Married': [False,False,True]}
  >>> tbl = Tabel(data)
  >>> tbl
   Name   |   Height |   Married
  --------+----------+-----------
   John   |     1.82 |         0
   Joe    |     1.65 |         0
   Jane   |     2.15 |         1
  3 rows ['<U4', '<f8', '|b1']

From numpy arrays:

  >>> Tabel([np.array(["John", "Joe", "Jane"]),
  ...                        np.array([1.82,1.65,2.15]),
  ...                        np.array([False,False,True])])
   0    |    1 |   2
  ------+------+-----
   John | 1.82 |   0
   Joe  | 1.65 |   0
   Jane | 2.15 |   1
  3 rows ['<U4', '<f8', '|b1']

Or initialize an empty Tabel:

  >>> tbl = Tabel()
  >>> tbl
  <BLANKLINE>
  0 rows []
  >>> len(tbl), tbl.shape
  (0, (0, 0))


Slicing
=======
API documentation: :py:mod:`tabel.Tabel.__getitem__`.

See the API reference for a detailed description: `Tabel.__getitem__`.

Some common examples:

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

Slicing works on both rows and columns:

  >>> tbl[:,1:3]
     Height |   Married
  ----------+-----------
       1.82 |         0
       1.65 |         0
       2.15 |         1
  3 rows ['<f8', '|b1']

Indexing:

  >>> tbl[[1,2],[0,2]]
   Name   |   Married
  --------+-----------
   Joe    |         0
   Jane   |         1
  2 rows ['<U4', '|b1']

Using named columns:

  >>> tbl[:,['Name','Married']]
   Name   |   Married
  --------+-----------
   John   |         0
   Joe    |         0
   Jane   |         1
  3 rows ['<U4', '|b1']

the ":" can be left out, if you're addressing columns by their names:

  >>> tbl[:, ['Name','Married']]
   Name   |   Married
  --------+-----------
   John   |         0
   Joe    |         0
   Jane   |         1
  3 rows ['<U4', '|b1']

Indexing using boolean array's:

  >>> index = ~tbl[:,'Married']
  >>> tbl[index, :]
   Name   |   Height |   Married
  --------+----------+-----------
   John   |     1.82 |         0
   Joe    |     1.65 |         0
  2 rows ['<U4', '<f8', '|b1']

(The ":" can be omitted for columns as well)

If a single index is given for the row or colum position, the returned datatype
is a row (tuple) or column (array) instead of Tabel:

  >>> tbl['Married']
  array([False, False,  True])
  >>> tbl[1:2, 'Married']
  array([False])

In all other cases the returned datatype is Tabel, including lists of length one:

  >>> tbl[:, ['Married']]
     Married
  -----------
           0
           0
           1
  3 rows ['|b1']

Equally so for rows:

  >>> tbl[2]
  ('Jane', 2.15, True)
  >>> tbl[2,1:3]
  (2.15, True)

Finally, single elements are obtained by individually addressing them:

  >>> tbl[0,"Name"]
  'John'


Setting
=======
API documentation: :py:mod:`tabel.Tabel.__setitem__`.

There is an detailed description in the API documentation:
:py:mod:`tabel.Tabel.__setitem__`. Generally, one just provides the datatype and
shape that would have come from the equivalent get call:

Set a single element:

  >>> tbl[0,"Name"] = "Jos"
  >>> tbl
   Name   |   Height |   Married
  --------+----------+-----------
   Jos    |     1.82 |         0
   Joe    |     1.65 |         0
   Jane   |     2.15 |         1
  3 rows ['<U4', '<f8', '|b1']

Set (part of) a column:

  >>> tbl[0:2,1] = np.array([2,3])
  >>> tbl
   Name   |   Height |   Married
  --------+----------+-----------
   Jos    |     2    |         0
   Joe    |     3    |         0
   Jane   |     2.15 |         1
  3 rows ['<U4', '<f8', '|b1']

Set (part of) a single row:

  >>> tbl[0] = ["John", 1.333, 0]
  >>> tbl
   Name   |   Height |   Married
  --------+----------+-----------
   John   |    1.333 |         0
   Joe    |    3     |         0
   Jane   |    2.15  |         1
  3 rows ['<U4', '<f8', '|b1']


Referencing
===========

Slices are references, Slices return new table objects, but their data always
refers back to the original one as long as that remains in existence. Exceptions
are:

   * New initialization of Tabel objects copy the data
   * Boolean or integer indexing of *rows* returns a Tabel object with copied data

To show, take a slice from `tbl`, modify its first columns, check out the
original `tbl`:

   >>> tbl = Tabel({'Name' : ["John", "Joe", "Jane"], 'Height' : [1.82,1.65,2.15], 'Married': [False,False,True]})
   >>> tbl_b = tbl[:,[1,2]]
   >>> tbl_b[:,0] = [1.3,1.4,1.5]
   >>> tbl
    Name   |   Height |   Married
   --------+----------+-----------
    John   |      1.3 |         0
    Joe    |      1.4 |         0
    Jane   |      1.5 |         1
   3 rows ['<U4', '<f8', '|b1']

Column arrays are references too, with the same exceptions as slices. Therefore
the standard numpy arithmetic can be used:

   >>> tbl = Tabel({'Name' : ["John", "Joe", "Jane"], 'Height' : [1.82,1.65,2.15], 'Married': [False,False,True]})
   >>> tbl["Height"] *= 2
   >>> tbl
    Name   |   Height |   Married
   --------+----------+-----------
    John   |     3.64 |         0
    Joe    |     3.3  |         0
    Jane   |     4.3  |         1
   3 rows ['<U4', '<f8', '|b1']


Appending
==========

Appending Tabel
----------------
API documentation: :py:mod:`tabel.Tabel.append`.

Tabels can be appended with their append method:

  >>> tbl = Tabel([ ["John", "Joe", "Jane"],
  ...                [1.82,1.65,2.15],
  ...                [False,False,True]], columns = ["Name", "Height", "Married"])
  >>> tblb = Tabel([["Bas"],[2.01],[True]], columns=["Name", "Height", "Married"])
  >>> tbl.append(tblb)
  >>> tbl
   Name   |   Height |   Married
  --------+----------+-----------
   John   |     1.82 |         0
   Joe    |     1.65 |         0
   Jane   |     2.15 |         1
   Bas    |     2.01 |         1
  4 rows ['<U4', '<f8', '|b1']

or using the "+=" syntax:

  >>> tblb = Tabel([["Bas"],[2.01],[True]], columns=["Name", "Height", "Married"])
  >>> tbl = Tabel([ ["John", "Joe", "Jane"],
  ...                [1.82,1.65,2.15],
  ...                [False,False,True]], columns = ["Name", "Height", "Married"])
  >>> tbl += tblb
  >>> tbl
   Name   |   Height |   Married
  --------+----------+-----------
   John   |     1.82 |         0
   Joe    |     1.65 |         0
   Jane   |     2.15 |         1
   Bas    |     2.01 |         1
  4 rows ['<U4', '<f8', '|b1']


Appending row
--------------
API documentation: :py:mod:`tabel.Tabel.row_append`.

You can also append a row (dict, list or tuple) at the end of the Tabel, for example:

  >>> tbl.row_append({'Name':"Jack", 'Height':1.82, 'Married':1})
  >>> tbl
   Name   |   Height |   Married
  --------+----------+-----------
   John   |     1.82 |         0
   Joe    |     1.65 |         0
   Jane   |     2.15 |         1
   Bas    |     2.01 |         1
   Jack   |     1.82 |         1
  5 rows ['<U4', '<f8', '<i8']

Appending column
-----------------
API documentation: :py:mod:`tabel.Tabel.__setitem__`.

To add a new column to the Tabel, just provide a new column name:

  >>> tbl = Tabel({'Name' : ["John", "Joe", "Jane"], 'Height' : [1.82,1.65,2.15], 'Married': [False,False,True]})
  >>> tbl["New"] = "Foo"
  >>> tbl["Newer"] = list(range(3))
  >>> tbl
   Name   |   Height |   Married | New   |   Newer
  --------+----------+-----------+-------+---------
   John   |     1.82 |         0 | Foo   |       0
   Joe    |     1.65 |         0 | Foo   |       1
   Jane   |     2.15 |         1 | Foo   |       2
  3 rows ['<U4', '<f8', '|b1', '<U3', '<i8']


  Notes:
      When changing a column two syntaxes give approximately the same
      result, with, however, a noteable difference. Using a slice object
      ":" will change all elements of the column with the new element(s)
      provided. If just the colum name is provided, with no indication for row,
      than the whole column is replaced with the column provided.

          >>> tbl = Tabel( [ ["John", "Joe", "Jane"],
          ...              [1.82,1.65,2.15],
          ...              [False,False,True] ],
          ...    columns = ["Name", "Height", "Married"])
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
      while seccond case the type of the Name column changes to `<i8`.





Changing column names
=====================
API documentation: :mod:`tabel.Tabel.columns`.

Just manipulate the columns property directly:

  >>> data = [ ["John", "Joe", "Jane"],
  ...                [1.82,1.65,2.15],
  ...                [False,False,True]]
  >>> tbl = Tabel(data, columns=['Name','Height','Married'])
  >>> tbl
   Name   |   Height |   Married
  --------+----------+-----------
   John   |     1.82 |         0
   Joe    |     1.65 |         0
   Jane   |     2.15 |         1
  3 rows ['<U4', '<f8', '|b1']
  >>> tbl.columns = ["First Name", "BMI", "Overweght"]
  >>> tbl
   First Name   |   BMI |   Overweght
  --------------+-------+-------------
   John         |  1.82 |           0
   Joe          |  1.65 |           0
   Jane         |  2.15 |           1
  3 rows ['<U4', '<f8', '|b1']

Transposing
===========
API documentation: :py:mod:`tabel.T`.

Data from database connectors often comes in list of records, a convenience
function is available to make the transpose:

  >>> from tabel import T
  >>> data = [['John', 1.82, False], ['Joe', 1.65, False], ['Jane', 2.15, True]]
  >>> tbl = Tabel(T(data))
  >>> tbl
   0    |    1 |   2
  ------+------+-----
   John | 1.82 |   0
   Joe  | 1.65 |   0
   Jane | 2.15 |   1
  3 rows ['<U4', '<f8', '|b1']


Group By
========
API documentation: :py:mod:`tabel.Tabel.group_by`.

To group by unique elements in a column or unique combinations of elements in
columns provide the column(s) as a list as the first argument. The second
argument is a list of tuples for the aggregate functions and their columns:

  >>> from tabel import first
  >>> tbl = Tabel({'a':[10,20,30, 40]*3, 'b':["100","200"]*6, 'c':[100,200]*6})
  >>> tbl
     a |   b |   c
  -----+-----+-----
    10 | 100 | 100
    20 | 200 | 200
    30 | 100 | 100
    40 | 200 | 200
    10 | 100 | 100
    20 | 200 | 200
    30 | 100 | 100
    40 | 200 | 200
    10 | 100 | 100
    20 | 200 | 200
    30 | 100 | 100
    40 | 200 | 200
  12 rows ['<i8', '<U3', '<i8']
  >>> tbl.group_by(['b','a'], [(np.sum, 'a'), (first, 'c')])
     b |   a |   a_sum |   c_first
  -----+-----+---------+-----------
   100 |  10 |      30 |       100
   100 |  20 |       0 |
   100 |  30 |      90 |       100
   100 |  40 |       0 |
   200 |  10 |       0 |
   200 |  20 |      60 |       200
   200 |  30 |       0 |
   200 |  40 |     120 |       200
  8 rows ['<U3', '<i8', '<i8', '|O']

`first` is a convenience function, for when aggregation should just take the
first element.


Sorting
=======
 API documentation: :py:mod:`tabel.Tabel.sort`.

   >>> tbl = Tabel({'Name' : ["John", "Joe", "Jane"], 'Height' : [1.82,1.65,2.15], 'Married': [False,False,True]})
   >>> tbl.sort("Name")
   >>> tbl
    Name   |   Height |   Married
   --------+----------+-----------
    Jane   |     2.15 |         1
    Joe    |     1.65 |         0
    John   |     1.82 |         0
   3 rows ['<U4', '<f8', '|b1']

Note that one can use indexing to reorder in any order:

  >>> tbl[[2,1,0],[2,1,0]]
     Married |   Height | Name
  -----------+----------+--------
           0 |     1.82 | John
           0 |     1.65 | Joe
           1 |     2.15 | Jane
  3 rows ['|b1', '<f8', '<U4']

Joining
=======
API documentation: :py:mod:`tabel.Tabel.join`.

To join another Tabel, provide the Tabe and the column or columns to use as a
key for joining:

  >>> tbl = Tabel({"a":list(range(4)), "b": ['a','b'] *2})
  >>> tbl_b = Tabel({"a":list(range(4)), "c": ['d','e'] *2})
  >>> tbl.join(tbl_b, "a")
  >>> tbl
     a | b   | c
  -----+-----+-----
     0 | a   | d
     1 | b   | e
     2 | a   | d
     3 | b   | e
  4 rows ['<i8', '<U1', '<U1']



Saving
======
API documentation: :py:mod:`tabel.Tabel.save`.

Data can be saved to disk in various formats:

  >>> tbl = Tabel({'Name' : ["John", "Joe", "Jane"], 'Height' : [1.82,1.65,2.15], 'Married': [False,False,True]})
  >>> tbl.save("test.csv", fmt="csv")

I recommend the numpy native 'npz' format:

  >>> tbl.save("test.npz", fmt="npz")

Reading
========
API documentation: :py:mod:`tabel.read_tabel`.

Read from disk:

  >>> from tabel import read_tabel
  >>> t = read_tabel("test.csv", fmt="csv")
  >>> t
   Name   |   Height | Married
  --------+----------+-----------
   John   |     1.82 | False
   Joe    |     1.65 | False
   Jane   |     2.15 | True
  3 rows ['<U4', '<f8', '<U5']
