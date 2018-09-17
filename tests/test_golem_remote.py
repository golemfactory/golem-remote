from golem_remote import decode_str_to_obj, encode_obj_to_str, GolemClient
from golem_remote.queue_helpers import Queue

from golem_remote.golem_client import GolemClientInterface, SubtaskState, \
    get_result_key
from uuid import uuid4 as make_uuid
import cloudpickle as pickle

from golem_remote.runf_helpers import SubtaskData


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

    def get(self, subtask_id, blocking = None, timeout = None):
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


class MockQueue(Queue):
    def __init__(self, *args, **kwargs):
        self.subtasks = []
        self.d = {}

    def pop(self, block, timeout):
        return self.subtasks.pop()

    def pop_nowait(self):
        return self.subtasks.pop()

    def push(self, key):
        self.subtasks.append(key)

    def set(self, key, value):
        self.d[key] = value
        p: SubtaskData = decode_str_to_obj(value)
        res = p.function(*p.args, **p.kwargs)
        out_key = get_result_key(key)
        self.d[out_key] = encode_obj_to_str(res)

    def get(self, key):
        return self.d[key]


# this one actually inserts stuff to redis
# but computes funcs by itself, not using golem
class MockQueue2(Queue):
    def set(self, key, value):
        super().set(key, value)
        p: SubtaskData = decode_str_to_obj(value)
        res = p.function(*p.args, **p.kwargs)
        super().set(get_result_key(key), encode_obj_to_str(res))


class GolemClientQueueMock(GolemClient):
    def initialize_task(self):
        if self.task_id:
            raise Exception("Task already initialized")

        self.task_id = "123"
        self.queue = MockQueue2(self.task_id)
