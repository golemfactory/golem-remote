from typing import Type

import mock

from golem_remote import decode_str_to_obj, encode_obj_to_str
from golem_remote.golem_client import GolemClientInterface, GolemClient
from golem_remote.golem_remote import RemoteFunction
from golem_remote.queue_helpers import Queue, get_result_key
from golem_remote.runf_helpers import SubtaskData
from tests.helpers import _TestWithRedis


class MockQueue(Queue):
    """Does not connect to redis, computes function by itself"""
    def __init__(self, *args, **kwargs):
        self.subtasks = []
        self.d = {}

    def pop(self, block = True, timeout = None):
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


class MockQueue2(Queue):
    """This one actually inserts stuff to redis
    but still computes functions by itself, not using golem"""

    def set(self, key, value):
        super().set(key, value)
        p: SubtaskData = decode_str_to_obj(value)
        res = p.function(*p.args, **p.kwargs)
        super().set(get_result_key(key), encode_obj_to_str(res))


class GolemClientQueueMock(GolemClient):
    """Does not connect to redis, computes function by itself"""

    def initialize_task(self):
        if self.task_id:
            raise Exception("Task already initialized")

        self.task_id = "123"
        self.queue = MockQueue(self.task_id)


class GolemClientQueue2Mock(GolemClient):
    """This one actually inserts stuff to redis
    but computes functions by itself, not using golem"""

    def initialize_task(self):
        if self.task_id:
            raise Exception("Task already initialized")

        self.task_id = "123"
        self.queue = MockQueue2(self.task_id)


class TestGolemClient(_TestWithRedis):

    def test_workflow(self):
        def run_test(class_: Type[GolemClientInterface]):
            g = class_()
            g.initialize_task()

            secret_sauce = "Secret"

            def func(arg1, arg2, kwarg1="abc", kwarg2="def"):
                print(f"Running func: {arg1} {arg2} {kwarg1} {kwarg2}")
                return (arg1 + arg2, kwarg1 + kwarg2, secret_sauce)

            func = RemoteFunction(func, g)
            res_id1 = func.remote(1, 2, kwarg1="abcd")
            res1 = g.get(res_id1)
            self.assertEqual(res1, (1 + 2, "abcd" + "def", secret_sauce))

        run_test(GolemClientQueueMock)
        run_test(GolemClientQueue2Mock)
