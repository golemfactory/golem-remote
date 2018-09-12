import enum
import json
import logging
import os
import subprocess
import tempfile
import time
from abc import ABCMeta, abstractmethod
from pathlib import Path
from typing import Optional, Any, Dict
from uuid import uuid4 as make_uuid

from golem_remote import config, consts
from .config import PYTHON_PATH
from .encoding import encode_obj_to_str, decode_str_to_obj
from .queue_helpers import Queue, get_result_key
from .runf_helpers import SubtaskID, SubtaskData, Host, Port, TaskID

logger = logging.getLogger("golem_remote")


class SubtaskState(enum.Enum):
    running = enum.auto()
    finished = enum.auto()


class GolemClientInterface(metaclass=ABCMeta):
    @abstractmethod
    def __init__(self, *_, **__):
        self.subtasks: Dict[SubtaskID, SubtaskState] = {}
        self.task_id: Optional[TaskID] = None

    # how to type it??
    def run_function(self, function, args, kwargs) -> SubtaskID:
        if not self.task_id:
            raise Exception("Task is not running")

        subtask_id = self._run(function, args, kwargs)
        return subtask_id

    ####################################################################
    @abstractmethod
    def initialize_task(self) -> None:
        pass

    @abstractmethod
    def _run(self, function, args, kwargs) -> SubtaskID:
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
                         number_of_subtasks: int = 1):
    with open(str(template_path), "r") as f:
        task_definition = json.load(f)

    task_definition["options"]["queue_host"] = queue_host
    task_definition["options"]["queue_port"] = queue_port
    task_definition["subtasks"] = number_of_subtasks
    with open(str(output_path), "w") as f:
        json.dump(task_definition, f)


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
                 tempdir: Path = None,
                 blocking: bool = False,
                 timeout: float = 30,
                 number_of_subtasks: int = 1) -> None:
        super().__init__()

        self.golem_host = golem_host
        self.golem_port = golem_port
        self.golem_dir = golem_dir
        self.golemcli = golemcli
        self.queue_host = queue_host
        self.queue_port = queue_port
        self.timeout = timeout
        self.blocking = blocking

        self.task_definition_template_path = Path(
            os.path.dirname(__file__), consts.TASK_DEFINITION_TEMPLATE)

        if tempdir:
            self._tempdir: Path = tempdir
        else:
            # ugly, but we have to prevent the TemporaryDirectory object from being
            # garbage-collected - and in the same time keep tempdir interface as Path
            self.__tempdir = tempfile.TemporaryDirectory()
            self._tempdir = Path(self.__tempdir.name)

        self.task_definition_path = Path(self._tempdir, "definition.json")

        fill_task_definition(self.task_definition_template_path, queue_host, queue_port,
                             self.task_definition_path, number_of_subtasks)

        self.queue: Optional[Queue] = None

    def _build_start_task_cmd(self):
        return [
            str(PYTHON_PATH),
            str(self.golemcli),
            "tasks",
            "create",
            str(self.task_definition_path),
            "-a",
            self.golem_host,
            "-p",
            str(self.golem_port),
            # "-d", str(self.golem_dir)]  # TODO uncomment it when rpc_auth will be merged
        ]

    def _run(self, function, args, kwargs):
        if self.queue is None:
            raise Exception("Queue is None. Maybe you forgot to initialize_task()?")

        subtask_id = str(make_uuid())
        parameters = SubtaskData(function=function, args=args, kwargs=kwargs)
        parameters = encode_obj_to_str(parameters)

        self.queue.set(subtask_id, parameters)
        self.queue.push(subtask_id)

        self.subtasks[subtask_id] = SubtaskState.running
        return subtask_id

    def initialize_task(self):
        if self.task_id:
            raise Exception("Task already initialized")

        stdout = _run_cmd(self._build_start_task_cmd())
        self.task_id = stdout.decode("ascii")[:-1]  # last char is \n
        logger.info(f"Task {self.task_id} started")
        self.queue = Queue(self.task_id, self.queue_host, self.queue_port)

    # TODO this is a naive implementation
    # later, there should be something like async_redis here
    def get(self,
            subtask_id: SubtaskID,
            blocking: Optional[bool] = True,
            timeout: Optional[float] = None):
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
