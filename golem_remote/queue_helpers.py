import logging
from typing import Tuple, Optional

import redis

from golem_remote.runf_helpers import Host, Port, QueueID

logger = logging.getLogger("golem_remote")


class _RedisQueue:
    """Simple Queue with Redis Backend
    code inspired by
    http://peter-hoffmann.com/2012/python-simple-queue-redis-queue.html
    """

    def __init__(self, name: str, host: Host = "127.0.0.1", port: Port = 6379):
        logger.info(f"Creating connection to {name} "
                    f"(host: {host}, port: {port}")
        self._db = redis.Redis(host=host, port=port, encoding='utf-8')
        self.key = f"{name}"

    def _queue_size(self) -> int:
        """Return the approximate size of the queue."""
        return self._db.llen(self.key)

    def empty(self) -> bool:
        """Return True if the queue is empty, False otherwise."""
        return self._queue_size() == 0

    def pop(self, block: bool, timeout: int=Optional[int]) -> Optional[str]:
        """Remove and return an item from the queue.

        If optional args block is true and timeout is None (the default), block
        if necessary until an item is available."""
        if block:
            item = self._db.blpop(self.key, timeout=timeout)
        else:
            item = self._db.lpop(self.key)

        if item:
            item = item.decode("utf-8")
        logger.info(f"Popping - key: {self.key}, value: {item}")
        return item

    def push(self, item: str):
        """Put item into the queue."""
        logger.info(f"Pushing - key: {self.key}, value: {item}")
        self._db.rpush(self.key, item)

    def set(self, key: str, item: str):
        self._db.set(key, item)

    def get(self, key: str) -> Optional[str]:
        val = self._db.get(key)
        if val is not None:
            val = val.decode("utf-8")

        logger.info(f"Getting - key: {key}, value: {val}")
        return val


class Queue(_RedisQueue):

    def pop(self, block: bool=True, timeout: Optional[int]=None) -> Tuple[QueueID, Optional[str]]:
        key = super().pop(block, timeout)
        return key, self.get(key)

    def pop_nowait(self) -> Tuple[QueueID, Optional[str]]:
        return self.pop(False)
