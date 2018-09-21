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


class _TestWithRedis(TestCase):
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
        if os.path.exists("./dump.rdb"):
            os.remove("./dump.rdb")
