import os
import shutil
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

import cloudpickle as pickle

from golem_remote import open_file
from golem_remote.consts import HASH

class TestOpenFile_1(unittest.TestCase):

    def test_open_file(self):
        original_dir = TemporaryDirectory()
        tempdir = TemporaryDirectory()

        os.makedirs(os.path.join(tempdir.name, "files"))
        p = os.path.join(original_dir.name, "a")

        with open(os.path.join(tempdir.name, "files", HASH(str(p))), "w") as f:
            f.write("abcd")

        def read_file(x):
            with open(x, "r") as f:
                return f.read()

        with open(os.path.join(tempdir.name, "read_file"), "wb") as f:
            pickle.dump(read_file, f)

        with open(os.path.join(tempdir.name, "read_file"), "rb") as f:
            func = pickle.load(f)

        import builtins  # pylint: disable=wrong-import-position
        open_file.orig_open = open
        builtins.open = open_file.open_file(
            Path(original_dir.name),
            task_files_dir=os.path.join(tempdir.name, "files")
        )

        self.assertEqual(func("a"), "abcd")
        with self.assertRaises(OSError):
            func("b")
