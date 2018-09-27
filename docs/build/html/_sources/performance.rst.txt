Performance
============

Tabel is designed for those cases where you have data of multiple types, like
records in a database, where the volume is small enough to fit it all in memory
and high freedom of data manipulation is needed. Use Tabel when the following
conditions are met:

    * Multiple columns with different datatyes each
    * Fields in a row have a shared relation (e.g. records in a database)
    * All data fits in memory
    * Only few and relatively simple SQL queries are needed
    * A large proportion of the data is numeric and would need column-wise
      arithmetic
    * Data manipulation requires complex (computed) slicing across both dimensions
      (rows and columns)

If the above conditions are not met, consider these alternatives:

    * numpy - if your data is purely numerical or when fields in a row have no relation.
    * HDF5  - if your data does not fit in memory
    * SQLite or MySQL - if you need complex DB queries (e.g. transactional)

That said, good general performance is paramount. Here below are some tests to
give an rough overview of where Tabel stands relative to pandas.

To do the tests, a few tools are needed:

    >>> import numpy as np
    >>> import pandas as pd
    >>> from tabel import Tabel
    >>> from timeit import default_timer


slicing tables
---------------

As Tabel is based on numpy, this is where it is good at. I think slicing syntax
is both clean and fast (about 15x faster than pandas in the below tests).

    First slicing test is to get a whole row from a large table. The return
    value should be a tuple from Tabel, pandas produces an object array which I
    believe is not very efficient as columns usually have different datatypes.
    Tabel is abut 43x faster in this particular case:

    >>> n = 1000000
    >>> data_dict = {'a':[1,2,3,4] * n, 'b':['a1','a2']*2*n, 'c':np.arange(4*n)}
    >>> df = pd.DataFrame(data_dict)
    >>> tbl = Tabel(data_dict)
    >>> def test_pandas_slice(n):
    ...     t0 = default_timer()
    ...     for i in range(n):
    ...         _ = df.iloc[100].values
    ...     return (default_timer() - t0)/n*1e6, "micro-sec"
    >>> test_pandas_slice(100000)                     # doctest: +SKIP
    (130.62096348032355, 'micro-sec')
    >>> def test_tabel_slice(n):
    ...     t0 = default_timer()
    ...     for i in range(n):
    ...         _ = tbl[100]
    ...     return (default_timer() - t0)/n*1e6, "micro-sec"
    >>> test_tabel_slice(100000)                      # doctest: +SKIP
    (3.045091559179127, 'micro-sec')


    Second slicing test is to get a number of rows from one particular column, the
    return value should be an array. Tabel is abut 15x faster in this case:

    >>> def test_pandas_slice(n):
    ...     t0 = default_timer()
    ...     for i in range(n):
    ...         _ = df['a'][1:10].values
    ...     return (default_timer() - t0)/n*1e6, "micro-sec"
    >>> test_pandas_slice(100000)                     # doctest: +SKIP
    (63.41531826881692, 'micro-sec')
    >>> def test_tabel_slice(n):
    ...     t0 = default_timer()
    ...     for i in range(n):
    ...         _ = tbl[1:10, 'a']
    ...     return (default_timer() - t0)/n*1e6, "micro-sec"
    >>> test_tabel_slice(100000)                      # doctest: +SKIP
    (4.007692479062825, 'micro-sec')


appending rows
--------------

I find myself often doing something similar to the following procedure:

    >>> for i in large_number:                        # doctest: +SKIP
    ...  row = calculate_something()
    ...  tbl.append(row)

where "do something" could be reading some tricky formatted ascii file or
calculating the position of the stars, it doesn't matter. The point is,
appending data is never a very efficient thing to do, memory needs to be
reserved, all values need to be re-evaluated for type setting and then all data
gets copied over to the new location. Still I prefer this over more efficient
methods as it keeps my code clean and simple.

I expect bad performance for both Tabel and pandas, but a simple test shows that
pandas is doing a bit worse. If we repeatedly add a simple row of two integers
to a pandas DataFrame we'll use about 300 micro-second per row:

    >>> import pandas as pd
    >>> from tabel import Tabel
    >>> from timeit import default_timer
    >>> df = pd.DataFrame({'1':[],'2':[]})
    >>> row = pd.DataFrame({'1':[1],'2':[2]})
    >>> def test_pandas(n):
    ...     t0 = default_timer()
    ...     for i in range(n):
    ...         df.append(row, ignore_index=True)
    ...     return (default_timer() - t0)/n*1e6, "micro-sec"
    >>> test_pandas(100000)                             # doctest: +SKIP
    (299.0699630905874, 'micro-sec')

The same exercise with Tabel's :mod:`tabel.Tabel.row_append` method takes only a
quarter of that time:

    >>> tbl = Tabel()
    >>> row = (1, 2)
    >>> def test_tabel(n):
    ...     t0 = default_timer()
    ...     for i in range(n):
    ...         tbl.row_append(row)
    ...     return (default_timer() - t0)/n*1e6, "micro-sec"
    >>> test_tabel(100000)                              # doctest: +SKIP
    (79.83603572938591, 'micro-sec')

Granted, there are very many different scenarios thinkable and there probably
are scenarios where pandas would outperform Tabel. If you come across one of
those please let me know and I happily add it here.


grouping tables
---------------

A big Tabel with a million rows can be grouped by multiple columns. Both pandas
and Tabel take a good amount of time on this, but then this is typically done
once on a an individual Tabel or DataFrame. pandas is about 10x faster than
Tabel on this simple test. The good news is that this is independent of n,
meaning they're both equally scalable.

    >>> n = 100000
    >>> data_dict = {'a':[1,2,3,4] * n, 'b':['a1','a2']*2*n, 'c':np.arange(4*n)}
    >>> df = pd.DataFrame(data_dict)
    >>> def test_pandas_groupby(n):
    ...     t0 = default_timer()
    ...     for i in range(n):
    ...         _ = df.groupby(('a', 'b')).sum()
    ...     return (default_timer() - t0)/n*1e3, "mili-sec"
    >>> test_pandas_groupby(10)                         # doctest: +SKIP
    (34.32465291116387, 'mili-sec')
    >>> tbl = Tabel(data_dict)
    >>> def test_tabel_groupby(n):
    ...     t0 = default_timer()
    ...     for i in range(n):
    ...         _ = tbl.group_by(('b', 'a'),[(np.sum, 'c')])
    ...     return (default_timer() - t0)/n*1e3, "mili-sec"
    >>> test_tabel_groupby(10)                          # doctest: +SKIP
    (322.54316059406847, 'mili-sec')


joining tables
--------------

Two Tabels can be joined together by some common key present in both Tabels. Two
table with a million rows takes about 2.5 second to be joined with pandas and 5
times that with Tabel, this ratio reduces somewhat with n. See the codeblock
below for the specific case tested here.

    >>> n = 1000000
    >>> data_dict = {'a':[1,2,3,4] * n, 'b':['a1','a2']*2*n, 'c':np.arange(4*n)}
    >>> df_1 = pd.DataFrame(data_dict)
    >>> df_2 = pd.DataFrame(data_dict)
    >>> def test_pandas_join():
    ...     t0 = default_timer()
    ...     _ = df_1.join(df_2, on='c', how='inner', lsuffix='l', rsuffix='r')
    ...     return (default_timer() - t0)*1e3, "mili-sec"
    >>> test_pandas_join()                              # doctest: +SKIP
    (2462.8482228145003, 'mili-sec')
    >>> tbl_1 = Tabel(data_dict)
    >>> tbl_2 = Tabel(data_dict)
    >>> def test_tabel_join():
    ...     t0 = default_timer()
    ...     _ = tbl_1.join(tbl_2, key='c', jointype='inner')
    ...     return (default_timer() - t0)*1e3, "mili-sec"
    >>> test_tabel_join()                               # doctest: +SKIP
    (10393.40596087277, 'mili-sec')
