import sys
import os
local_path = os.path.abspath(os.path.join(os.getcwd(), "../"))
sys.path.insert(0,local_path)

from tabel import Tabel, read_tabel, T, first
import os
import pytest
import numpy as np
from itertools import product
from copy import copy, deepcopy
import pandas as pd

def naneq(a, b):
    """ Test wether a and b are equal, counting both nan as being equal.
    """
    try:
        return np.all(np.isnan(a) == np.isnan(b)) or np.all(a == b)
    except TypeError as e:
        return np.all(a == b)

@pytest.fixture
def tbls():
    tbls = [Tabel({'Name' : ["John", "Joe", "Jane"], 'Height' : [1.82,1.65,2.15], 'Married': [False,False,True]}),
            Tabel([ np.array(["John", "Joe", "Jane"]),np.array([1.82,1.65,2.15]),np.array([False,False,True])], columns = ["Name", "Height", "Married"]),
            Tabel([ ["John", "Joe", "Jane"],[1.82,1.65,2.15],[False,False,True]], columns = ["Name", "Height", "Married"]),
            Tabel(),
            Tabel([1,2,3]),
            Tabel({'a':range(10),'b':range(10)}),
            Tabel({'a':range(10),'b':list(map(str, range(10)))}),
            Tabel([range(10),range(10),range(10)]),
            Tabel(np.array([np.arange(10),np.arange(10,20)])),
            Tabel({'a':12,'b':13}),
            Tabel(pd.DataFrame({'a':[12]*6, 'b':np.arange(6), 'c':range(6)})),
            Tabel({'a':[3,4,5], 'b':1}),
            Tabel({'a':1, 'b':[3,4,5]}),
            Tabel({'aa':[1,1,1], 'b':[3,4,5]}),
            ]
    return tbls


class TestTabelInit(object):
    def test_tabel_init(self, tbls):
        for tbl in tbls:
            assert tbl.valid


class TestAppend(object):
    def test_append_tabel(self, tbls):
        for tbl in tbls:
            length = len(tbl)
            tbl += tbl
            assert tbl.valid
            assert len(tbl) == 2 * length

    def test_append_column(self, tbls):
        for tbl in tbls:
            width = tbl.shape[1]
            ln = len(tbl)
            tbl["n1"] = 12
            tbl["n2"] = "Foo"
            tbl["n3"] = np.arange(len(tbl))
            tbl["n4"] = [12]*len(tbl)
            tbl["n5"] = ["Bar"]*len(tbl)
            assert tbl.valid
            assert tbl.shape[1] == width + 5
            if ln > 0:
                assert len(tbl) == ln

    def test_append_combinations(self):
        first_tbl = [Tabel(), Tabel({'a':2,'b':3}), Tabel({'a':"ff",'b':"ffr"})]
        seccond_tbl = [Tabel({'a':22,'b':13}), pd.DataFrame({'a':[22],'b':[13]}),
                       Tabel({'a':"ff",'b':"ffr"}),
                       pd.DataFrame({'a':["jdw"],'b':["okdw"]}),
                       ]
        for ftbl, stbl in product(first_tbl, seccond_tbl):
                ftbl = deepcopy(ftbl)
                fl = len(ftbl)
                ftbl.append(stbl)
                assert ftbl.valid
                assert len(ftbl) == fl + 1

    def test_row_append_combinations(self):
        first_tbl = [Tabel(), Tabel({'a':2,'b':3}), Tabel({'a':"ff",'b':"ffr"})]
        seccond_tbl = [{'a':22,'b':13}, [22,33], (44,55), np.array([33,33]),
                       {'a':"ded",'b':"fr"}, ["frd","werf"],
                       ("efds","dew"), np.array(["frde","frtg"])]
        for ftbl, stbl in product(first_tbl, seccond_tbl):
                ftbl = deepcopy(ftbl)
                fl = len(ftbl)
                ftbl.row_append(stbl)
                assert ftbl.valid
                assert len(ftbl) == fl + 1


class TestSlice(object):
    def test_slice_type(self, tbls):
        for tbl in tbls:
            if len(tbl) > 0:
                assert type(tbl[0]) == tuple
                assert type(tbl[:,0]) == np.ndarray
                assert type(tbl[:,:]) == Tabel
                assert type(tbl[0,0]) == type(tbl.data[0][0])
                assert type(tbl[[0],[0]]) == Tabel
                (r,c) = tbl.shape
                assert type(tbl[np.array([True]*r),np.array([True]*c)]) == Tabel
                assert type(tbl[list(range(r)),list(range(c))]) == Tabel
                assert type(tbl[:,:]) == Tabel

    def test_slice_columns(self, tbls):
        for tbl in tbls:
            if tbl:
                assert np.all(tbl[:,0] == tbl.data[0])
                assert np.all(tbl[:,tbl.columns[0]] == tbl.data[0])

    def test_slice_rows(self, tbls):
        for tbl in tbls:
            if tbl:
                assert np.all(tbl[0][0] == tbl.data[0][0])

    def test_slice_boolean(self, tbls):
        for tbl in tbls:
            if tbl.shape[0] > 0 & tbl.shape[1] > 0:
                ind = tbl[:,0] == 0
                ind = ind if isinstance(ind, np.ndarray) else np.array([ind])
                assert type(tbl[ind,:]) == Tabel

    def test_slice_permiseable(self, tbls):
        row_it = [slice(0,2,None), [0,1], np.array([True,False,True]), 0, np.array([0,1]),
                  np.array([False, True, False]), slice(0,3,2)]
        col_it = row_it + [["Name", "Height"], "Name", ["Height", "Name"]]
        keys = list(product(row_it, col_it))
        for tbl in tbls[0:3]:
            for key in keys:
                _ = tbl[key]


class TestSetter(object):
    def test_set_individual_elm(self, tbls):
        for tbl in tbls[0:3]:
            tbl[0,0] = "Bas"
            tbl[1,1] = 12
            tbl[2,1] = True

    def test_set_column(self, tbls):
        for tbl in tbls[:3]:
            i = tbl.columns.index("Name")
            tbl[0:2,i] = np.array(["Bas", "Jack"])
            tbl[0:2,"Name"] = ["Bas", "Jack"]
            tbl[[0], "Name"] = ["Bas"]
            length = len(tbl)
            tbl["Name"] = "Blanc"
            assert np.all(tbl["Name"] == np.array(length*["Blanc"]).astype(tbl["Name"].dtype))
            tbl[[False, True, False], 1] = [13]
            tbl["Name"] = ["Noone"] * length
            tbl[:, "Name"] = ["Noone"] * length

    def test_set_row(self):
        tbl = Tabel({"a":list(range(2,6)), "b": ['1','2'] *2, "c":[1.1,2.2]*2})
        tbl[0,:] = (12, "12", 12.12)
        tbl[1,['a','b']] = [12, "12"]
        tbl[2] = (13, "13", 13.13)
        tbl[3, np.array([True, False, True])] = (14, 14.14)

    def test_add_column(self):
        tbl = Tabel({"a":list(range(2,6)), "b": ['1','2'] *2, "c":[1.1,2.2]*2})
        tbl["d"] = np.array([True]*len(tbl))
        tbl["e"] = 100
        tbl["f"] = "Blanc"
        assert len(tbl.columns) == 6
        assert np.all([len(c)==len(tbl) for c in tbl.data])

    def test_replace_column(self):
        tbl = Tabel({"a":list(range(2,6)), "b": ['1','2'] *2, "c":[1.1,2.2]*2})
        tbl[:,"a"] = np.array([1.4,2.4]*2)
        assert tbl[0,'a'] == 1
        tbl["a"] = np.array([1.1,2.2]*2)
        assert tbl['a'].dtype == np.float
        tbl[:,"b"] = np.arange(4)
        assert tbl[0, "b"] == "0"
        tbl["b"] = np.arange(4)
        assert tbl[0, "b"] == 0
        tbl[:,"c"] = np.arange(4)
        assert tbl["c"].dtype == np.float
        tbl["c"] = np.arange(4)
        assert tbl["c"].dtype == np.int


class TestSaveNRead(object):
    def test_save_n_read(self, tbls, tmpdir):
        for header in [True, False]:
            for fmt in ['csv', 'gz', 'npz']:
                for tbl in tbls:
                    if len(tbl) > 0:
                        fn = os.path.join(str(tmpdir), "test."+fmt)
                        tbl.save(fn, header=header)
                        tbl_r = read_tabel(fn, header=header)
                        assert (set(tbl_r.columns) == set(tbl.columns)) or (not header), (tbl, tbl_r)
                        assert len(tbl_r) == len(tbl), (tbl, tbl_r)
                        assert tbl_r.valid, (tbl, tbl_r)

                        if not tbl_r.columns[0].isdigit() and len(tbl)>2:
                            # header sniffer should work
                            tbl_r = read_tabel(fn, header=None)
                            assert set(tbl_r.columns) == set(tbl.columns), (tbl, tbl_r)
                            assert len(tbl_r) == len(tbl), (tbl, tbl_r)

class TestGroupBy(object):
    def test_group_by(self):
        tbl = Tabel({'a':[10,20,30, 40]*3, 'b':["100","200"]*6, 'c':[100,200]*6})
        tbl_g = tbl.group_by(['b','a'], [(np.sum, 'a'), (first, 'c')])
        idx = np.argsort(tbl_g['a_sum'])
        assert np.all(tbl_g[idx, 'a_sum'] == np.array([30, 60, 90, 120]))
        assert np.all(tbl['a'] == [10,20,30, 40]*3)
        assert np.all(tbl_g[idx, 'c_first'] == np.array([100, 200, 100, 200]))
        tbl_g = tbl.group_by(['b','a'], [])
        idx = np.argsort(tbl_g['a'])
        assert np.all(tbl_g[idx, 'a'] == [10,20,30,40])


class TestShapeNLen(object):
    def test_shape_n_len(self, tbls):
        for tbl in tbls:
            assert len(tbl) == tbl.shape[0]

    def test_shape(self, tbls):
        for tbl in tbls:
            assert len(tbl.columns) == tbl.shape[1]
            assert len(tbl.data) == tbl.shape[1]

    def test_len(self, tbls):
        for tbl in tbls:
            for c in tbl.columns:
                assert len(tbl[c]) == tbl.shape[0]


class TestTranspose(object):
    def test_transpose(self, tbls):
        for tbl in tbls:
            if len(tbl) == 0:
                continue
            lrec = [tbl[i] for i in range(len(tbl))]
            tbl_n = Tabel(T(lrec))
            for i,column in enumerate(tbl.columns):
                assert np.all(tbl[column] == tbl_n[str(i)])
            lrec = [list(tbl[i]) for i in range(len(tbl))]
            tbl_n = Tabel(T(lrec))
            for i,column in enumerate(tbl.columns):
                assert np.all(tbl[column] == tbl_n[str(i)])


class TestJoin(object):
    def test_inner_int_join(self):
        tbl = Tabel({"a":list(range(4)), "b": ['a','b'] *2})
        tbl_b = Tabel({"a":list(range(2,6)), "c": ['d','e'] *2})
        tbl_j = tbl.join(tbl_b, "a")
        assert "c_r" in tbl_j.columns
        assert tbl_j[0] == (2,'a','d')
        assert len(tbl_j) == 2
        assert np.all(tbl[0] == (0,'a'))

    def test_inner_str_join(self):
        tbl = Tabel({"a":list(map(str, range(4))), "b": ['a','b'] *2})
        tbl_b = Tabel({"a":list(map(str, range(4))), "c": ['d','e'] *2})
        tbl_j = tbl.join(tbl_b, "a", jointype="inner")
        assert "c_r" in tbl_j.columns
        assert tbl_j[0] == ('0','a','d')
        assert len(tbl_j) == 4
        assert np.all(tbl[0] == ('0','a'))

    def test_outer_join(self):
        tbl = Tabel({"a":list(range(4)), "b": ['a','b'] *2})
        tbl_b = Tabel({"a":list(range(2,6)), "c": [1,2] *2, "d":[1.1,2.2]*2})
        tbl_j = tbl.join(tbl_b, "a", jointype='outer')
        naneq(tbl_j[tbl_j['a_l']==0,'c_r'], Tabel.join_fill_value['integer'])
        naneq(tbl_j[tbl_j['a_l']==0, 'd_r'], Tabel.join_fill_value['float'])
        naneq(tbl_j[tbl_j['a_r']==4, 'b_l'], Tabel.join_fill_value['string'])
        assert "c_r" in tbl_j.columns
        assert len(tbl_j) == 6


class TestSort(object):
    def test_sort(self):
        tbl = Tabel({'aa':['b','g','d'], 'b':list(range(3))})
        tbl.sort('aa')
        assert tbl[0] == ('b',0)
        assert tbl[1] == ('d',2)
        tbl.sort(['aa', 'b'])
        assert tbl[1] == ('g',1)


class TestDTypeProperties(object):
    def test_dtype_properties(self):
        tbl = Tabel({"a":list(range(2,6)), "c": [u'1',u'2'] *2, "d":[1.1,2.2]*2})
        assert tbl.dtype == np.dtype([('a', '<i8'), ('c', '<U1'), ('d', '<f8')])
        tbl_n = tbl.astype([np.float, np.int16, np.dtype('<U10')])
        assert tbl_n.dtype == np.dtype([('a', '<f8'), ('c', '<i2'), ('d', '<U10')])


class TestPandasBackAndForth(object):
    def test_pandas_b_and_f(self):
        data = {'a':[12]*6, 'b':np.arange(6), 'c':list(map(str, range(6)))}
        df = pd.DataFrame(data)
        tbl = Tabel(df)
        for k in data.keys():
            assert np.all(tbl.dict['a'] == data['a'])
        tbl = Tabel(data)
        df = pd.DataFrame(tbl.dict)
        for k in data.keys():
            assert np.all(df['a'] == data['a'])


class TestDelItem(object):
    def test_del_row_int(self):
        tbl1 = Tabel({"a":list(range(2,6)), "b": ['1','2'] *2, "c":[1.1,2.2]*2})
        tbl2 = Tabel({"a":list(range(2,6)), "b": ['1','2'] *2, "c":[1.1,2.2]*2})
        del tbl1[0]
        assert len(tbl1) == 3
        for i in range(len(tbl1)):
            assert tbl1[i] == tbl2[i+1]

        del tbl1[-1]
        assert len(tbl1) == 2
        assert tbl1[0] == tbl2[1]
        assert tbl1[1] == tbl2[2]

    def test_del_row_slice(self):
        tbl1 = Tabel({"a":list(range(2,6)), "b": ['1','2'] *2, "c":[1.1,2.2]*2})
        tbl2 = Tabel({"a":list(range(2,6)), "b": ['1','2'] *2, "c":[1.1,2.2]*2})
        del tbl1[1:3]
        assert len(tbl1) == 2
        assert tbl1[0] == tbl2[0]
        assert tbl1[1] == tbl2[3]


    def test_del_col(self):
        tbl1 = Tabel({"a":list(range(2,6)), "b": ['1','2'] *2, "c":[1.1,2.2]*2})
        tbl2 = Tabel({"a":list(range(2,6)), "b": ['1','2'] *2, "c":[1.1,2.2]*2})
        del tbl1['b']
        assert tbl1.columns == ['a','c']
        assert all( tbl1['a'] == tbl2['a'] )
        assert all( tbl1['c'] == tbl2['c'] )
