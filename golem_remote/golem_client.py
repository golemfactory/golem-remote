import enum
import json
import logging
import os
import shutil
import subprocess
import tempfile
import time
from abc import ABCMeta, abstractmethod
from pathlib import Path
from typing import Optional, Any, Dict, Set
from uuid import uuid4 as make_uuid

from golem_remote import config, consts
from golem_remote.open_file import list_dir_recursive
from .config import PYTHON_PATH
from .encoding import encode_obj_to_str, decode_str_to_obj
from .queue_helpers import Queue, get_result_key
from .runf_helpers import SubtaskID, SubtaskData, Host, Port, TaskID

logger = logging  # temporary solution - should be logging.getLogger(LOGGER_NAME)


class SubtaskState(enum.Enum):
    running = enum.auto()
    finished = enum.auto()


class GolemClientInterface(metaclass=ABCMeta):
    @abstractmethod
    def __init__(self, *_, **__):
        self.subtasks: Dict[SubtaskID, SubtaskState] = {}
        self.task_id: Optional[TaskID] = None

    def run_function(self, data: SubtaskData) -> SubtaskID:
        if not self.task_id:
            raise Exception("Task is not running")

        subtask_id = self._run(data)
        return subtask_id

    ####################################################################
    @abstractmethod
    def initialize_task(self) -> None:
        pass

    @abstractmethod
    def _run(self, data: SubtaskData) -> SubtaskID:
        pass

    @abstractmethod
    def get(self,
            subtask_id: SubtaskID,
            blocking: Optional[bool] = True,
            timeout: Optional[float] = None) -> Any:
        pass


def fill_task_definition(template_path: Path,
                         queue_host: Host,
                         queue_port: Port,
                         output_path: Path,
                         number_of_subtasks: int = 1,
                         task_files_dir: Path = None):
    with open(str(template_path), "r") as f:
        task_definition = json.load(f)

    task_definition["options"]["queue_host"] = queue_host
    task_definition["options"]["queue_port"] = queue_port
    task_definition["subtasks"] = number_of_subtasks
    task_definition["resources"] = []
    if task_files_dir:
        task_definition["resources"] += [str(file)
                                        for file in list_dir_recursive(task_files_dir)]
        # task_definition["resources"] += [str(task_files_dir.absolute())]

    with open(str(output_path), "w") as f:
        json.dump(task_definition, f)

    logger.info(f"Task definition built: {json.dumps(task_definition, indent=4, sort_keys=True)}")


def initialize_task_files(tmp: Path, task_files: Set[Path]) -> None:
    tmp = Path("~", "temporary").expanduser()
    """Takes a list of task files and a temporary directory and creates symlinks to the
    specified files there."""
    os.mkdir(os.path.join(tmp, consts.GOLEM_TASK_FILES_DIR))

    for f in task_files:
        dest_path = Path(consts.GOLEM_TASK_FILES_DIR, consts.HASH(f))
        # os.symlink(str(f.absolute()), str(Path(tmp, dest_path)))
        shutil.copy(str(f.absolute()), str(Path(tmp, dest_path)))

    # we create a guard file because otherwise Golem does not work properly
    with open(os.path.join(tmp, "guard"), "w") as f:
        f.write("GUARD")


def _run_cmd(cmd):
    logger.info(f"Running command {' '.join(cmd)}")
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE)

    stdout, stderr = process.communicate()
    if stderr:
        raise Exception(f"Something went wrong: {stderr}")
    return stdout


class GolemClient(GolemClientInterface):
    def __init__(self,
                 golem_host: Host = config.GOLEM_HOST,
                 golem_port: Port = config.GOLEM_PORT,
                 golem_dir: Path = config.GOLEM_DIR,
                 golemcli: Path = config.GOLEMCLI,
                 queue_host: Host = config.QUEUE_HOST,
                 queue_port: Port = config.QUEUE_PORT,
                 blocking: bool = False,
                 timeout: float = 30,
                 number_of_subtasks: int = 1,
                 clear_db: bool = False,
                 task_id: TaskID = None,
                 task_files: Set[Path] = None) -> None:
        super().__init__()

        self.golem_host = golem_host
        self.golem_port = golem_port
        self.golem_dir = golem_dir
        self.golemcli = golemcli
        self.queue_host = queue_host
        self.queue_port = queue_port
        self.timeout = timeout
        self.blocking = blocking
        self.clear_db = clear_db
        self.task_id = task_id
        self.number_of_subtasks = number_of_subtasks
        self.task_files = task_files if task_files else []

        self.task_definition_template_path = Path(
            os.path.dirname(__file__), consts.TASK_DEFINITION_TEMPLATE)

        self.queue: Optional[Queue] = None

    def _build_start_task_cmd(self, task_definition_path: Path):
        return [
            str(PYTHON_PATH),
            str(self.golemcli),
            "tasks",
            "create",
            str(task_definition_path),
            "-a",
            self.golem_host,
            "-p",
            str(self.golem_port),
            # "-d", str(self.golem_dir)]  # TODO uncomment it when rpc_auth will be merged
        ]

    def _run(self, data: SubtaskData) -> SubtaskID:
        if self.queue is None:
            raise Exception("Queue is None. Maybe you forgot to initialize_task()?")

        subtask_id = str(make_uuid())
        data = encode_obj_to_str(data)

        self.queue.set(subtask_id, data)
        self.queue.push(subtask_id)

        self.subtasks[subtask_id] = SubtaskState.running
        return subtask_id

    def _create_golem_task(self) -> None:
        if self.task_id:
            logger.warning(f"Task already initialized with {self.task_id}")
            return

        with tempfile.TemporaryDirectory() as task_definition_tmp, \
             tempfile.TemporaryDirectory() as task_files_tmp:
            task_definition_path = Path(task_definition_tmp, "definition.json")

            initialize_task_files(task_files_tmp, self.task_files)
            fill_task_definition(self.task_definition_template_path, self.queue_host,
                                 self.queue_port, task_definition_path, self.number_of_subtasks,
                                 task_files_dir=Path("~", "temporary").expanduser())# Path(task_files_tmp))

            logger.info(f"Task definition saved in {task_definition_path}")
            stdout = _run_cmd(self._build_start_task_cmd(task_definition_path))

        self.task_id = stdout.decode("ascii")[:-1]  # last char is \n
        logger.info(f"Task {self.task_id} started")

    def _create_queue(self) -> None:
        self.queue = Queue(self.task_id, self.queue_host, self.queue_port)

    def initialize_task(self) -> None:
        self._create_golem_task()
        self._create_queue()

        if self.clear_db:
            logger.info("Clearing database")
            self.queue.clear_db()
            self.clear_db = False  # do it only once

    def __getstate__(self):
        state = self.__dict__.copy()
        del state["queue"]

    def __setstate__(self, state):
        self.__dict__.update(state)
        self._create_queue()

    # TODO this is a naive implementation
    # later, there should be something like async_redis here
    def get(self, subtask_id, blocking = True, timeout= None):
        if self.queue is None:
            raise Exception("Queue is None. Maybe you forgot to initialize_task()?")

        blocking = blocking if blocking is not None else self.blocking
        timeout = timeout if timeout is not None else self.timeout

        result = self.queue.get(get_result_key(subtask_id))
        runtime: float = 0
        while not result and blocking and runtime < timeout:
            result = self.queue.get(get_result_key(subtask_id))
            time.sleep(0.5)
            runtime += 0.5

        if result is not None:
            result = decode_str_to_obj(result)
        return result
