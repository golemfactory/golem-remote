from hashlib import md5
from pathlib import Path
from typing import Callable, Any

TASK_DEFINITION_TEMPLATE = Path("task_definition", "runf.json")
LOGGER_NAME = "golem_remote"

GOLEM_RESOURCES_DIR = "/golem/resources"
GOLEM_TASK_FILES_DIR = "files"

HASH: Callable[[Any], str] = lambda x: md5(str(x).encode("utf-8")).hexdigest()
