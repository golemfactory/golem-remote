from uuid import uuid4 as make_uuid

import cloudpickle as pickle

import golem_remote
from golem_remote.golem_client import GolemClientInterface
from golem_remote.runf_helpers import SubtaskData
from tests.helpers import _TestWithRedis
from tests.test_golem_client import GolemClientQueueMock, \
    GolemClientQueue2Mock


class GolemClientAllMock(GolemClientInterface):
    """Does not use Queue at all, does not pickle anything"""

    def __init__(self, *args, **kwargs):
        super().__init__()
        self._subtasks_results = {}

    def initialize_task(self):
        self.task_id = "Task"

    def _run(self, data):
        subtask_id = str(make_uuid())
        self._subtasks_results[subtask_id] = data.function(*data.args, **data.kwargs)
        return subtask_id

    def get(self, subtask_id, blocking=None, timeout=None):
        return self._subtasks_results[subtask_id]


class GolemClientMockPickle(GolemClientAllMock):
    """Pickles data, but does not use Queue"""

    def __init__(self, *args, **kwargs):
        super().__init__()
        self._subtasks_results = {}

    def initialize_task(self):
        self.task_id = "Task"

    def __run_pickled(self, data: bytes):
        data: SubtaskData = pickle.loads(data)
        return data.function(*data.args, **data.kwargs)

    def _run(self, data: SubtaskData):
        subtask_id = str(make_uuid())
        data: bytes = pickle.dumps(data)
        self._subtasks_results[subtask_id] = self.__run_pickled(data)
        return subtask_id

    def get(self, subtask_id, blocking=None, timeout=None):
        return self._subtasks_results[subtask_id]


class TestGolemRemote(_TestWithRedis):

    def test_workflow(self):
        def run_test(class_):
            golem_remote.init(class_=class_)
            secret_sauce = "Secret"

            @golem_remote.remote
            def func(arg1, arg2, kwarg1="abc", kwarg2="def"):
                print(f"Running func: {arg1} {arg2} {kwarg1} {kwarg2}")
                return (arg1 + arg2, kwarg1 + kwarg2, secret_sauce)

            res_id1 = func.remote(1, 2, kwarg1="abcd")
            res1 = golem_remote.get(res_id1)
            self.assertEqual(res1, (1 + 2, "abcd" + "def", secret_sauce))

        run_test(GolemClientMockPickle)
        run_test(GolemClientQueueMock)
        run_test(GolemClientQueue2Mock)
