import enum
import json
import os
import subprocess
import tempfile
import time
from abc import ABCMeta, abstractmethod
from pathlib import Path
from typing import Optional, Any, Dict
from uuid import uuid4 as make_uuid

import cloudpickle as pickle

from golem_remote import config, consts
from .config import PYTHON_PATH
from .encoding import encode_obj_to_str, decode_str_to_obj
from .queue_helpers import Queue
from .runf_helpers import SubtaskID, SubtaskData, Host, Port, TaskID


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
    def initialize_task(self):
        pass

    @abstractmethod
    def _run(self, function, args, kwargs) -> SubtaskID:
        pass

    @abstractmethod
    def get(self, subtask_id: SubtaskID) -> Any:
        pass


class GolemClientAllMock(GolemClientInterface):
    def __init__(self, *args, **kwargs):
        super().__init__()
        self._subtasks_results = {}

    def initialize_task(self):
        self.task_id = "Task"

    def _run(self, function, args, kwargs):
        subtask_id = str(make_uuid())
        self._subtasks_results[subtask_id] = function(*args, **kwargs)
        self.subtasks[subtask_id] = SubtaskState.finished
        return subtask_id

    def get(self, subtask_id):
        return self._subtasks_results[subtask_id]


class GolemClientMockPickle(GolemClientAllMock):
    def __init__(self, *args, **kwargs):
        super().__init__()
        self._subtasks_results = {}

    def initialize_task(self):
        self.task_id = "Task"

    def __run_pickled(self, function, args, kwargs):
        function = pickle.loads(function)
        args = [pickle.loads(x) for x in args]
        kwargs = {k: pickle.loads(v) for k, v in kwargs.items()}
        return function(*args, **kwargs)

    def _run(self, function, args, kwargs):
        subtask_id = str(make_uuid())
        function = pickle.dumps(function)
        args = [pickle.dumps(x) for x in args]
        kwargs = {k: pickle.dumps(v) for k, v in kwargs.items()}
        self._subtasks_results[subtask_id] = function(*args, **kwargs)
        self.subtasks[subtask_id] = SubtaskState.finished
        return subtask_id

    def get(self, subtask_id):
        return self._subtasks_results[subtask_id]


# class GolemClientProcess(GolemClient):
#     pass

def fill_task_definition(template_path: Path,
                         queue_host: Host,
                         queue_port: Port,
                         output_path: Path,
                         number_of_subtasks: int=1):
    with open(str(template_path), "r") as f:
        task_definition = json.load(f)

    task_definition["options"]["queue_host"] = queue_host
    task_definition["options"]["queue_port"] = queue_port
    task_definition["subtasks"] = number_of_subtasks
    with open(str(output_path), "w") as f:
        json.dump(task_definition, f)


class GolemClient(GolemClientInterface):

    def __init__(self,
                 golem_host: Host=config.GOLEM_HOST,
                 golem_port: Port=config.GOLEM_PORT,
                 golem_dir: Path=config.GOLEM_DIR,
                 golemcli: Path=config.GOLEMCLI,
                 queue_host: Host=config.QUEUE_HOST,
                 queue_port: Port=config.QUEUE_PORT, # 6379,
                 tempdir: Path=None,
                 blocking: bool=False,
                 timeout: int=30,
                 number_of_subtasks: int=1):
        super().__init__()

        # print(os.path.dirname(__file__))
        self.golem_host = golem_host
        self.golem_port = golem_port
        self.golem_dir = golem_dir
        self.golemcli = golemcli
        self.queue_host = queue_host
        self.queue_port = queue_port
        self.timeout = timeout
        self.blocking = blocking

        self.task_definition_template_path = Path(
            os.path.dirname(__file__),
            consts.TASK_DEFINITION_TEMPLATE
        )

        self._tempdir: Path = tempdir \
            if tempdir \
            else tempfile.TemporaryDirectory()

        self.task_definition_path = Path(self._tempdir.name, "definition.json")
        fill_task_definition(
            self.task_definition_template_path,
            queue_host,
            queue_port,
            self.task_definition_path,
            number_of_subtasks
        )

        self.queue: Queue = None

    def _run_cmd(self, cmd):

        # print(f"INFO: running command {' '.join(cmd)}")
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE)

        stdout, stderr = process.communicate()
        if stderr:
            raise Exception(f"Something went wrong: {stderr}")
        return stdout

    def _build_start_task_cmd(self):
        return [str(PYTHON_PATH), str(self.golemcli), "tasks", "create",
                str(self.task_definition_path),
                "-a", self.golem_host, "-p", str(self.golem_port),
                ]
        # "-d", str(self.golem_dir)]

    def _run(self, function, args, kwargs):
        subtask_id = make_uuid()
        parameters = SubtaskData(
            function=function,
            args=args,
            kwargs=kwargs
        )
        parameters = encode_obj_to_str(parameters)

        self.queue.set(subtask_id, parameters)
        self.queue.push(subtask_id)

        self.subtasks[subtask_id] = SubtaskState.running
        return subtask_id

    def initialize_task(self):
        if self.task_id:
            raise Exception("Task already initialized")

        stdout = self._run_cmd(self._build_start_task_cmd())
        self.task_id = stdout.decode("ascii")[:-1]
        # print(f"Task {self.task_id} started")
        self.queue = Queue(self.task_id, self.queue_host, self.queue_port)

    # TODO this is a naive implementation
    # later, there should be something like async_redis here
    def get(self, subtask_id: SubtaskID, blocking=None, timeout=None):
        blocking = blocking if blocking is not None else self.blocking
        timeout = timeout if timeout is not None else self.timeout

        result = self.queue.get(f"{subtask_id}-OUT")
        runtime = 0
        while not result and blocking and runtime < timeout:
            result = self.queue.get(f"{subtask_id}-OUT")
            time.sleep(0.5)
            runtime += 0.5

        result = decode_str_to_obj(result)
        return result


class MockQueue(Queue):
    def __init__(self, *args, **kwargs):
        self.subtasks = []
        self.d = {}

    def push(self, key):
        # print(f"Pushing {key} to queue")
        self.subtasks.append(key)

    def set(self, key, value):
        p: SubtaskData = decode_str_to_obj(value)
        res = p.function(*p.args, **p.kwargs)
        # print(f"Setting {key} to {res}")
        self.d[key] = encode_obj_to_str(res)

    def get(self, key):
        # print(f"Getting {key}")
        return self.d[key]


# this one actually inserts stuff to redis
# but computes funcs by itself, not using golem
class MockQueue2(Queue):
    def set(self, key, value):
        p: SubtaskData = decode_str_to_obj(value)
        res = p.function(*p.args, **p.kwargs)
        super().set(key, encode_obj_to_str(res))


class GolemClientQueueMock(GolemClient):
    def initialize_task(self):
        if self.task_id:
            raise Exception("Task already initialized")

        self.task_id = "123"
        # print(f"Task {self.task_id} started")
        self.queue = MockQueue2(self.task_id)
