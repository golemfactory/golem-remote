import os
import shutil
import unittest
from tempfile import TemporaryDirectory

import cloudpickle as pickle
import mock

from golem_remote import open_file
from golem_remote.consts import HASH

class TestOpenFile_1(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.tempdir = TemporaryDirectory()

    def test_open_file_1(self):
        os.makedirs(os.path.join(self.tempdir.name, "files"))

        with open(os.path.join(self.tempdir.name, "files", HASH("a")), "w") as f:
            f.write("abcd")

        def read_file(x):
            with open(x, "r") as f:
                return f.read()

        with open(os.path.join(self.tempdir.name, "read_file"), "wb") as f:
            pickle.dump(read_file, f)

    def test_open_file_2(self):

        with open(os.path.join(self.tempdir.name, "read_file"), "rb") as f:
            func = pickle.load(f)

        import builtins  # pylint: disable=wrong-import-position
        open_file.orig_open = open
        builtins.open = open_file.open_file(os.path.join(self.tempdir.name, "files"))

        self.assertEqual(func("a"), "abcd")
        with self.assertRaises(OSError):
            func("b")
