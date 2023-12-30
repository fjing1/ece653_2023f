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


import os
from hypothesis import strategies as st
from hypothesis.stateful import RuleBasedStateMachine, rule, invariant
import unittest
import pickledb


class PickleDBStateMachine(RuleBasedStateMachine):
    def __init__(self):
        super().__init__()
        self.db_file = 'test_stateful.db'
        self.db = pickledb.load(self.db_file, False)
        self.model = dict()  # Internal model to represent the expected state of the database

    @rule(key=st.text(), value=st.text())
    def set_value(self, key, value):
        self.db.set(key, value)
        self.model[key] = value

    @rule(key=st.text())
    def get_value(self, key):
        if key in self.model:
            assert self.db.get(key) == self.model[key]
        else:
            assert self.db.get(key) == False

    @rule(key=st.text())
    def delete_key(self, key):
        self.db.rem(key)
        self.model.pop(key, None)
        assert self.db.get(key) == False

    @rule(key=st.text(), value=st.text())
    def update_value(self, key, value):
        if key in self.model:
            self.db.set(key, value)
            self.model[key] = value

    @rule()
    def list_keys(self):
        assert set(self.db.getall()) == set(self.model.keys())

    @rule()
    def dump_database(self):
        self.db.dump()
        reloaded_db = pickledb.load(self.db_file, False)
        for key in self.model:
            assert reloaded_db.get(key) == self.model[key]

    @invariant()
    def db_matches_model(self):
        for key in self.model:
            assert self.db.get(key) == self.model[key]
        for key in self.db.getall():
            assert key in self.model

    def teardown(self):
        if os.path.exists(self.db_file):
            os.remove(self.db_file)


TestPickleDBStateMachine = PickleDBStateMachine.TestCase


if __name__ == '__main__':
    unittest.main()
