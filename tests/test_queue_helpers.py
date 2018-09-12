import os
import signal
import subprocess
from unittest import TestCase

from golem_remote.queue_helpers import _RedisQueue, Queue
from golem_remote.runf_helpers import Port


def start_redis(port: Port) -> subprocess.Popen:
    p = subprocess.Popen(
        ["redis-server", "--port", str(port)],
        stdout=subprocess.PIPE,
        shell=True,
        preexec_fn=os.setsid
    )
    return p


class TestWithRedis(TestCase):
    PORT = 6379
    redis_process = None

    @classmethod
    def setUpClass(cls):
        cls.redis_process = start_redis(cls.PORT)

    def setUp(self):
        redis = _RedisQueue("abcd", port=self.PORT)
        redis._db.flushall()

    @classmethod
    def tearDownClass(cls):
        os.killpg(os.getpgid(cls.redis_process.pid), signal.SIGTERM)
        os.remove("./dump.rdb")

class TestRedisQueue(TestWithRedis):
    def test_init(self):
        key = "totem"
        r = _RedisQueue(key, "127.0.0.1", 6379)
        self.assertEqual(r.key, key)

        _ = _RedisQueue(key, "127.0.0.1")  # TODO
        _ = _RedisQueue(key, port=6379)

        with self.assertRaises(TypeError):
            _ = _RedisQueue()

    def test_empty(self):
        r = _RedisQueue("abcd")
        self.assertTrue(r.is_empty())

        r.push("defg")
        self.assertFalse(r.is_empty())
        r._pop(False)
        self.assertTrue(r.is_empty())

    def test_push_pop_noblock(self):
        r = _RedisQueue("abcd")

        vals = ["a", "b", "c", "d"]
        for v in vals:
            r.push(v)

        res = []
        for _ in range(len(vals)):
            res.append(r._pop(False))

        self.assertEqual(res, vals)

        val = r._pop(False)
        self.assertIsNone(val)

    def test_push_pop_block(self):
        r = _RedisQueue("abcd")

        vals = ["banan", "gruszka", "jabłko", "awokado"]
        for v in vals:
            r.push(v)

        res = []
        for _ in range(len(vals)):
            res.append(r._pop(False))

        self.assertEqual(res, vals)

        val = r._pop(False)
        self.assertIsNone(val)

        # Types checking
        # r.push(None)
        # val = r.pop(False)
        # self.assertEqual(val, "None")


    def test_get_set(self):
        r = _RedisQueue("abcd")

        val = r.get("key1")
        self.assertEqual(val, None)

        r.set("key1", "val1")
        val = r.get("key1")
        self.assertEqual(val, "val1")

        # Types checking
        # with self.assertRaises(TypeError):
        #     r.set(None, "abcd")
        # with self.assertRaises(TypeError):
        #     r.set([123], "abcd")

        r.set("", "val2")
        val = r.get("")
        self.assertEqual(val, "val2")


class TestQueue(TestWithRedis):

    def test_pop_noblock(self):
        r = Queue("abcd", port=self.PORT)

        r.push("id1")
        r.set("id1", "val1")
        self.assertEqual(r.pop(False), ("id1", "val1"))

        r.push("id1")
        r.set("id1", "val1")
        self.assertEqual(r.pop(False), ("id1", "val1"))

        r.push("id2")
        self.assertEqual(r.pop(False), ("id2", None))

        self.assertEqual(r.pop(False), (None, None))

    def pop_nowait(self):
        r = Queue("abcd", port=self.PORT)

        r.push("id1")
        r.set("id1", "val1")
        self.assertEqual(r.pop(False), ("id1", "val1"))
