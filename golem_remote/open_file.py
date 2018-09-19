# This should not be used anywhere except docker_runf.py in Golem RunF task.
# It's a python black magic - a collection of hacks to get paths relatively working.
# Should definitely be replaced with a solution basing on some virtual filesystem, either on
# the system (docker) level (this would probably be better, although IDK how would
# Windows paths behave then) or on the Python level, hot-patching FS modules :
#  - builtins.open
#  - os
#  - shelve
#  - ...

import os
import io
from pathlib import Path
from typing import Callable

from .consts import GOLEM_RESOURCES_DIR, GOLEM_TASK_FILES_DIR, HASH

orig_open: Callable[..., io.IOBase] = None


def open_file(original_dir: Path,
              task_files_dir: str = os.path.join(GOLEM_RESOURCES_DIR, GOLEM_TASK_FILES_DIR)):
    def _open(file, *args, **kwargs) -> io.IOBase:
        file = Path(file)
        if not file.is_absolute():
            file = f"{str(original_dir)}/{file[1:]}"
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
