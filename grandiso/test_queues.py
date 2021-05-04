import pytest

from .queues import ProfilingQueue, Deque, QueuePolicy

all_queues = [
    (ProfilingQueue, ()),
    (Deque, ()),
    (Deque, (QueuePolicy.DEPTHFIRST,)),
    (Deque, (QueuePolicy.BREADTHFIRST,)),
]


@pytest.mark.parametrize(
    "queue,queue_args", all_queues,
)
def test_empty(queue, queue_args):
    q = queue(*queue_args)
    assert q.empty()
    q.put(1)
    assert q.empty() == False
    q.get()
    assert q.empty()


@pytest.mark.parametrize(
    "queue,queue_args", all_queues,
)
def test_can_put_and_pop(queue, queue_args):
    q = queue(*queue_args)
    q.put(1)
    assert q.get() == 1
    q.put(2)
    q.put(3)
    q.put(lambda x: x)

    q.get()
    q.get()
    q.get()
    assert q.empty()


def test_bfs_dfs():
    bfs = Deque(QueuePolicy.BREADTHFIRST)
    dfs = Deque(QueuePolicy.DEPTHFIRST)

    bfs.put(1)
    dfs.put(1)
    bfs.put(2)
    dfs.put(2)

    assert bfs.get() == 2
    assert dfs.get() == 1
