## _Class_ `QueuePolicy(Enum)`

An Enum for queue pop policy.

DEPTHFIRST policy is identified with pushing and popping on the same side of the queue. BREADTHFIRST is identified with pushing and popping from the opposite side of the queue.

## _Class_ `ProfilingQueue(queue.SimpleQueue)`

A simple queue to enable profiling. This queue keeps track of its size over time so that you can more easily debug performance.

Note that you do not want to use this queue for production workloads, as it adds substantial overhead.

## _Function_ `__init__(self)`

Create a new ProfilingQueue.

### Arguments

    None

### Returns

    None

## _Function_ `put(self, *args, **kwargs)`

Put a new element into the queue.

### Arguments

> -   **element** (`None`: `None`): The element to add to the queue

### Returns

    None

## _Function_ `get(self, *args, **kwargs)`

Get a new item from the queue.

### Arguments

    None

### Returns

> -   **Any** (`None`: `None`): The element popped from the queue

## _Class_ `Deque`

A double-ended queue implementation.

## _Function_ `__init__(self, policy: QueuePolicy = QueuePolicy.DEPTHFIRST)`

Create a new double-ended queue.

### Arguments

> -   **policy** (`QueuePolicy`: `None`): The policy to use when adding and removing

        elements from this queue. Defaults to depth-first.

### Returns

    None

## _Function_ `put(self, *args, **kwargs)`

Put a new element into the queue.

### Arguments

> -   **element** (`None`: `None`): The element to add to the queue

### Returns

    None

## _Function_ `get(self, *args, **kwargs)`

Get a new item from the queue.

### Arguments

    None

### Returns

> -   **Any** (`None`: `None`): The element popped from the queue

## _Function_ `empty(self)`

Returns True if the queue is empty.

### Arguments

    None

### Returns

> -   **bool** (`None`: `None`): True if the queue has nothing more to pop
