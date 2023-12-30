# Hypothesis Testing for PickleDB
# Copyright (C) 2023 Cuiyang (William) Wang
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.


import unittest
import os
import tempfile
from hypothesis import given, assume, strategies as st
import pickledb


class TestPickleDB(unittest.TestCase):
    def setUp(self):
        self.db_file = 'test.db'
        self.db = pickledb.load(self.db_file, False)

    def tearDown(self):
        if os.path.exists(self.db_file):
            os.remove(self.db_file)

    @given(st.text(), st.text())
    def test_set_get(self, key, value):
        self.db.set(key, value)
        self.assertEqual(self.db.get(key), value)

    @given(st.text(), st.text())
    def test_exists(self, key, value):
        self.db.set(key, value)
        self.assertTrue(self.db.exists(key))

    @given(st.text(), st.text())
    def test_remove(self, key, value):
        self.db.set(key, value)
        self.db.rem(key)
        self.assertFalse(self.db.exists(key))

    @given(st.text(), st.lists(st.text()))
    def test_list_operations(self, key, values):
        # Test list creation, addition, and retrieval
        self.db.lcreate(key)
        for value in values:
            self.db.ladd(key, value)
        self.assertEqual(self.db.lgetall(key), values)

    @given(st.text(), st.dictionaries(st.text(), st.text()))
    def test_dict_operations(self, key, dictionary):
        # Test dictionary creation, addition, and retrieval
        self.db.dcreate(key)
        for k, v in dictionary.items():
            self.db.dadd(key, (k, v))
        self.assertEqual(self.db.dgetall(key), dictionary)

    @given(st.text(), st.text(), st.integers(min_value=1, max_value=100))
    def test_append(self, key, value, num):
        # Test appending a value multiple times
        self.db.set(key, value)
        for _ in range(num):
            self.db.append(key, value)
        expected_value = value + value * num
        self.assertEqual(self.db.get(key), expected_value)

    # Test for totalkeys, which returns the number of keys in the database
    @given(st.lists(st.tuples(st.text(), st.text())))
    def test_totalkeys(self, key_value_pairs):
        for key, value in key_value_pairs:
            self.db.set(key, value)
        self.assertEqual(self.db.totalkeys(), len(set(key for key, _ in key_value_pairs)))
        self.db.deldb()

    @given(st.text(), st.lists(st.text(), min_size=1))
    def test_list_pop(self, key, values):
        # Test popping an element from the list
        self.db.lcreate(key)
        for value in values:
            self.db.ladd(key, value)
        popped_value = self.db.lpop(key, -1)
        self.assertEqual(popped_value, values[-1])
        self.assertEqual(self.db.lgetall(key), values[:-1])

    @given(st.text(), st.dictionaries(st.text(), st.text(), min_size=1))
    def test_dict_pop(self, key, dictionary):
        # Test popping a key-value pair from the dictionary
        self.db.dcreate(key)
        for k, v in dictionary.items():
            self.db.dadd(key, (k, v))
        popped_key = next(iter(dictionary))
        popped_value = self.db.dpop(key, popped_key)
        self.assertEqual(popped_value, dictionary[popped_key])
        del dictionary[popped_key]
        self.assertEqual(self.db.dgetall(key), dictionary)

    @given(st.text(), st.integers(min_value=0, max_value=100), st.text())
    def test_lrange(self, key, num_elements, value):
        # Test lrange functionality
        self.db.lcreate(key)
        for _ in range(num_elements):
            self.db.ladd(key, value)
        start, end = 0, min(num_elements, 10)  # Example range
        expected_range = [value] * (end - start)
        self.assertEqual(self.db.lrange(key, start, end), expected_range)

    @given(st.text(), st.lists(st.text()))
    def test_lremlist(self, key, values):
        # Test removing a list
        self.db.lcreate(key)
        for value in values:
            self.db.ladd(key, value)
        self.db.lremlist(key)
        self.assertFalse(self.db.exists(key))

    @given(st.text(), st.text(), st.dictionaries(st.text(), st.text()), st.dictionaries(st.text(), st.text()))
    def test_dmerge(self, key1, key2, dict1, dict2):
        # Test merging two dictionaries
        assume(key1 != key2)
        self.db.dcreate(key1)
        for k, v in dict1.items():
            self.db.dadd(key1, (k, v))
        self.db.dcreate(key2)
        for k, v in dict2.items():
            self.db.dadd(key2, (k, v))
        self.db.dmerge(key1, key2)
        dict1.update(dict2)
        self.assertEqual(self.db.dgetall(key1), dict1)

    @given(st.text(), st.dictionaries(st.text(), st.text()))
    def test_dkeys_dvals(self, key, dictionary):
        # Test retrieval of dictionary keys and values
        self.db.dcreate(key)
        for k, v in dictionary.items():
            self.db.dadd(key, (k, v))
        self.assertEqual(set(self.db.dkeys(key)), set(dictionary.keys()))
        self.assertEqual(set(self.db.dvals(key)), set(dictionary.values()))

    @given(st.text())
    def test_deldb(self, key):
        # Test deletion of the database
        self.db.set(key, 'value')
        self.db.deldb()
        self.assertFalse(self.db.exists(key))

    @given(st.text(), st.text())
    def test_getitem_setitem(self, key, value):
        # Test __getitem__ and __setitem__ methods
        self.db[key] = value
        self.assertEqual(self.db[key], value)

    @given(st.text())
    def test_delitem(self, key):
        # Test __delitem__ method
        self.db[key] = 'value'
        del self.db[key]
        self.assertFalse(self.db.exists(key))

    @given(st.lists(st.text()))
    def test_getall(self, keys):
        # Test getall method
        for key in keys:
            self.db[key] = 'value'
        self.assertEqual(set(self.db.getall()), set(keys))
        self.db.deldb()

    @given(st.text(), st.lists(st.text()))
    def test_lextend(self, key, values):
        # Test lextend method
        self.db.lcreate(key)
        self.db.lextend(key, values)
        self.assertEqual(self.db.lgetall(key), values)

    @given(st.text(), st.lists(st.text(), min_size=1))
    def test_lremvalue(self, key, values):
        # Test lremvalue method
        self.db.lcreate(key)
        for value in values:
            self.db.ladd(key, value)
        remove_value = values[0]
        self.db.lremvalue(key, remove_value)
        values.remove(remove_value)
        self.assertEqual(self.db.lgetall(key), values)

    @given(st.text(), st.dictionaries(st.text(), st.text()))
    def test_drem(self, key, dictionary):
        # Test drem method (removing a key-value pair from a dictionary)
        self.db.dcreate(key)
        for k, v in dictionary.items():
            self.db.dadd(key, (k, v))
        self.db.drem(key)
        self.assertFalse(self.db.exists(key))
        self.db.deldb()

    @given(st.text(), st.dictionaries(st.text(), st.text()), st.text())
    def test_dexists(self, key, dictionary, search_key):
        # Test dexists method (check if a key exists in a dictionary)
        self.db.dcreate(key)
        for k, v in dictionary.items():
            self.db.dadd(key, (k, v))
        exists = self.db.dexists(key, search_key)
        self.assertEqual(exists, search_key in dictionary)

    @given(st.dictionaries(keys=st.text(), values=st.text()))
    def test_dump_and_load(self, data):
        # Test dump and load methods for data persistence
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            database_file = tmp.name

        try:
            # Initialize PickleDB and dump data
            db = pickledb.load(database_file, False)
            for key, value in data.items():
                db.set(key, value)
            db.dump()

            # Load the data into a new instance and check
            new_db = pickledb.load(database_file, False)
            for key, value in data.items():
                self.assertEqual(new_db.get(key), value)

        finally:
            # Clean up the temporary file
            if os.path.exists(database_file):
                os.remove(database_file)


if __name__ == '__main__':
    unittest.main()
