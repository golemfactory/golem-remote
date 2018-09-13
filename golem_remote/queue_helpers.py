import logging
from typing import Tuple, Optional

import redis

from golem_remote.consts import LOGGER_NAME
from golem_remote.runf_helpers import Host, Port, QueueID, SubtaskID

logger = logging  # temporary solution - should be logging.getLogger(LOGGER_NAME)


def get_result_key(subtask_id: SubtaskID) -> str:
    return f"{subtask_id}-OUT"


class _RedisQueue:
    """Simple Queue with Redis Backend
    code inspired by http://peter-hoffmann.com/2012/python-simple-queue-redis-queue.html
    """

    def __init__(self, name: str, host: Host = "127.0.0.1", port: Port = 6379) -> None:
        logger.info(f"Creating connection to {name} (host: {host}, port: {port}")
        self._db = redis.Redis(host=host, port=port, encoding='utf-8')
        self.key = f"{name}"

    def _queue_size(self) -> int:
        """Return the approximate size of the queue."""
        return self._db.llen(self.key)

    def is_empty(self) -> bool:
        """Return True if the queue is is_empty, False otherwise."""
        return self._queue_size() == 0

    def clear_queue(self):
        """Removes all items from the queue"""
        self._db.delete([self.key])

    def clear_db(self):
        """Removes all items from the database"""
        self._db.flushdb()

    def _pop(self, block: bool = True, timeout: Optional[int] = 30) -> Optional[str]:
        """Remove and return an val from the queue.

        If optional args block is true and timeout is None (the default), block
        if necessary until an val is available."""
        if block:
            val = self._db.blpop(self.key, timeout=timeout)
            if val is None:  # Would be nice to have a Maybe monad here
                return None
            val = val[1]
        else:
            val = self._db.lpop(self.key)

        if val:
            val = val.decode("utf-8")
        logger.info(f"Popping - key: {self.key}, value: {val}")
        return val

    def push(self, val: str):
        """Put val into the queue."""
        logger.info(f"Pushing - key: {self.key}, value: {val}")
        self._db.rpush(self.key, val)

    def set(self, key: str, val: str):
        """Set a key to value."""
        self._db.set(key, val)

    def get(self, key: str) -> Optional[str]:
        """Get a value from the database."""

        val = self._db.get(key)
        if val is not None:
            val = val.decode("utf-8")

        logger.info(f"Getting - key: {key}, value: {val}")
        return val


class Queue(_RedisQueue):

    def pop(self, block: bool = True, timeout: Optional[int] = None) \
            -> Tuple[Optional[QueueID], Optional[str]]:
        key = super()._pop(block, timeout)
        if key is None:
            return None, None
        return key, self.get(key)

    def pop_nowait(self) -> Tuple[Optional[QueueID], Optional[str]]:
        return self.pop(False)
