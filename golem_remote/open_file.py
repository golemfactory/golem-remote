# This should not be used anywhere except docker_runf.py in Golem RunF task.
# It's a python black magic.

import os
import io

from .consts import GOLEM_RESOURCES_DIR, GOLEM_TASK_FILES_DIR, HASH

orig_open = None


def open_file(task_files_dir: str = os.path.join(GOLEM_RESOURCES_DIR, GOLEM_TASK_FILES_DIR)):
    def _open(file, *args, **kwargs) -> io.IOBase:
        #  extended debug information - can be disabled without
        available_files = list(os.listdir(task_files_dir))
        if HASH(file) in available_files:
            # pylint: disable=not-callable
            return orig_open(os.path.join(task_files_dir, HASH(file)), *args,
                             **kwargs)  # type: ignore
        else:
            # works normally for files other than specified
            # pylint: disable=not-callable
            return orig_open(file, *args, **kwargs)  # type: ignore

    return _open
