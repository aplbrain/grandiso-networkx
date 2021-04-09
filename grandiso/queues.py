from collections import deque
import queue
from enum import Enum


class QueuePolicy(Enum):
    DEPTHFIRST = 1
    BREADTHFIRST = 2


class ProfilingQueue(queue.SimpleQueue):
    def __init__(self):
        super(ProfilingQueue, self).__init__()
        self._size_history = queue.SimpleQueue()
        self._size = 0

    def put(self, *args, **kwargs):
        res = super(ProfilingQueue, self).put(*args, **kwargs)
        self._size += 1
        self._size_history.put(self._size)
        return res

    def get(self, *args, **kwargs):
        res = super(ProfilingQueue, self).get(*args, **kwargs)
        self._size -= 1
        self._size_history.put(self._size)
        return res


class Deque:
    def __init__(self, policy: QueuePolicy = QueuePolicy.DEPTHFIRST):
        self._dq = deque()
        if policy == QueuePolicy.DEPTHFIRST:
            self._put = self._dq.append
            self._get = self._dq.popleft
        elif policy == QueuePolicy.BREADTHFIRST:
            self._get = self._dq.pop
            self._put = self._dq.append

    def put(self, *args, **kwargs):
        return self._put(args[0])

    def get(self, *args, **kwargs):
        return self._get()

    def empty(self):
        return False if self._dq else True
