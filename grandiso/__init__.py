from typing import Union, Optional
import queue

import boto3

from grand import Graph

from uuid import uuid4


class _GrandIsoLimit:
    """
    A limit supervisor that limits the execution of a GrandIso algorithm run.

    """

    def __init__(
        self,
        parent: "GrandIso",
        lambda_count_limit: int,
        wallclock_limit_seconds: float,
    ) -> None:
        """
        Create a new GrandIso limit supervisor.

        The `lambda_count_limit` is a TOTAL number of lambda functions to run
        in the lifetime of the execution, NOT a concurrency limit.

        The wallclock limit is the total number of seconds from initial run,
        after which new lambdas will not be scheduled. A lambda that is running
        when the clock times out will continue to run to completion, and will
        not turn back into a pumpkin.

        Arguments:
            parent (GrandIso): The GrandIso algorithm pointer to monitor
            lambda_count_limit (int): The maximum number of lambdas to run
            wallclock_limit_seconds (float): The maximum number of run seconds

        Returns:
            None

        """
        self.parent = parent
        self.lambda_count_limit = lambda_count_limit
        self.wallclock_limit_seconds = wallclock_limit_seconds


class _UnboundedGrandIsoLimit(_GrandIsoLimit):
    def __init__(self, parent: "GrandIso"):
        self.parent = parent
        self.lambda_count_limit = None
        self.wallclock_limit_seconds = None


class GrandIsoQueue:
    """
    Abstract class for queue management in a Grand-Iso run.

    """

    def __init__(self):
        raise NotImplementedError()

    def exists(self) -> bool:
        """
        Return True if this resource already exists.
        """
        return False

    def provision(self, wait_for_completion: bool = True):
        """
        Provision this cloud resource.

        Arguments:
            wait_for_completion (bool: True): Whether to wait for this resource
                to be provisioned successfully.

        Returns:
            None

        """
        raise NotImplementedError()


_DEFAULT_SQS_RESOURCE_URL = "http://localhost:4566"


class SimplePythonQueueGrandIsoQueue(GrandIsoQueue):
    """
    Grand-Iso queue that uses a local Python queue object.
    """

    def __init__(self, gi_instance: "GrandIso",) -> None:
        """
        Create a new Python-memory-backed queue.

        Arguments:
            resource_url (str: _DEFAULT_SQS_RESOURCE_URL): The URL for the SQS
                resource that will be used (e.g. if you want to run locally).

        Returns:
            None

        """
        self._parent = gi_instance
        self._queue = queue.SimpleQueue()

    def queue_backbone(self, backbone):
        """
        Add a backbone graph to the queue.
        """
        self._queue.put(backbone)

    def pop_backbone(self):
        """
        Get a backbone graph from the queue.
        """
        return self._queue.get()


class SQSGrandIsoQueue(GrandIsoQueue):
    """
    Grand-Iso queue that uses AWS SQS.
    """

    def __init__(
        self,
        gi_instance: "GrandIso",
        resource_url: str = _DEFAULT_SQS_RESOURCE_URL,
        aws_access_key_id: str = "",
        aws_secret_access_key: str = "",
    ) -> None:
        """
        Create a new SQS-backed queue.

        Arguments:
            resource_url (str: _DEFAULT_SQS_RESOURCE_URL): The URL for the SQS
                resource that will be used (e.g. if you want to run locally).

        Returns:
            None

        """
        self._parent = gi_instance
        self._resource_url = resource_url
        self._sqs_client = boto3.resource(
            "sqs",
            endpoint_url=resource_url,
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
        )

    def queue_backbone(self, backbone):
        """
        Add a backbone graph to the queue.
        """
        raise NotImplementedError()

    def pop_backbone(self):
        """
        Get a backbone graph from the queue.
        """
        raise NotImplementedError()


class GrandIsoFunction:
    def __init__(self):
        raise NotImplementedError()

    def exists(self) -> bool:
        """
        Return True if this resource already exists.
        """
        return False

    def provision(self, wait_for_completion: bool = True):
        """
        Provision this cloud resource.

        Arguments:
            wait_for_completion (bool: True): Whether to wait for this resource
                to be provisioned successfully.

        Returns:
            None

        """
        raise NotImplementedError()


class GrandIsoResultsTable:
    def __init__(self):
        raise NotImplementedError()

    def exists(self) -> bool:
        """
        Return True if this resource already exists.
        """
        return False

    def provision(self, wait_for_completion: bool = True):
        """
        Provision this cloud resource.

        Arguments:
            wait_for_completion (bool: True): Whether to wait for this resource
                to be provisioned successfully.

        Returns:
            None

        """
        raise NotImplementedError()


class GrandIso:
    """
    A high-level class for managing cloud-scale subgraph isomorphism using the
    novel grand-iso backbone algorithm.

    Pseudocode:

        - Provision a DynamoDB table for result storage.
        - Preprocessing
            - Identify highest-degree node in motif, M1
            - Identify second-highest degree node in motif, M2, connected to M1 by
                a single edge.
            - Identify all nodes with degree of M1 or greater in the host graph,
                which also have all required attributes of the M1 and M2 nodes. If
                neither M1 nor M2 have degree > 1 nor attributes, select M1 and M2 as
                two nodes with attributes defined.
            - Enumerate all paths in the host graph from M1 candidates to M2 candidates,
                as candidate "backbones" in AWS SQS.
        - Motif Search
            - For each backbone candidate:
                - Schedule an AWS Lambda:
                    - Pop the backbone from the queue.
                    - Traverse all shortest paths in the motif starting at the nearest
                        of either M1 or M2
                    - If multiple nodes are valid candidates, queue a new backbone with
                        each option, and terminate the current Lambda.
                    - When all paths are valid paths in the host graph, add the list
                        of participant nodes to a result in the DynamoDB table.
        - Reporting
            - Return a serialization of the results from the DynamoDB table.
        - Cleanup
            - Delete the backbone queue
            - Delete the results table (after collection)

    """

    def __init__(
        self,
        graph: Optional[Union[grand.Graph]] = None,
        exact_match: bool = False,
        limits: _GrandIsoLimit = None,
        **kwargs
    ):
        """
        Initialize a new GrandIso management instance.

        Arguments:
            exact_match (bool: False): Whether to allow edges in the host graph
                that were not explicitly specified in the motif

        """
        # Whether to allow edges in the host graph that were not explicitly
        # specified in the motif
        self._exact_match = exact_match

        # Attach a limit handler to prevent runaway jobs. By default, there is
        # no limit (¡CUIDADO!)
        self._limits = limits if limits else _UnboundedGrandIsoLimit(self)

        # Assign a unique identifier to this instance so that all resources
        # (such as db tables, queues, lambdas) run in isolation from other
        # Grand-Iso runs.
        self._instance_id = str(uuid4())

        # Save a pointer to the graph. If the graph is not set, then proceed
        # as usual but do not let the user run an execution until it is set.
        self._graph = graph
        self._graph_specified = True if self._graph else False

    @property
    def instance_id(self):
        """
        Get the unique instance ID for this run-instance of Grand-Iso.

        """
        return self._instance_id

    def is_ready(self) -> bool:
        """
        Returns True if the instance is ready to begin execution.
        """
        return self._graph_specified

    def set_graph(self, graph: grand.Graph):
        """
        Set a pointer to the dynamo-backed grand Graph object.

        Arguments:
            graph (grand.Graph): The graph to use (must be dynamo-backed)

        Returns:
            None

        """
        self._graph = graph
        self._graph_specified = True

    def _provision_queue(self):
        """
        Provision the SQS for this run.

        """
        raise NotImplementedError()

    def _provision_backbone_lambda(self):
        """
        Provision a new lambda function to run each backbone check.

        """
        raise NotImplementedError()

    def _provision_results_table(self):
        """
        Provision a new DynamoDB table to hold the results of this run.

        """
        raise NotImplementedError()

    def provision_resources(self, wait: bool = True):
        """
        Provision all cloud resources that will be required for this run.

        Arguments:
            wait (bool: True): Whether to wait for all resources before
                returning from this call. If False, the user must await the
                creation of resources manually.

        Returns:
            Tuple[any, any, any]: A tuple containing the provisioned resources

        """
        queue = self._provision_queue()
        function = self._provision_backbone_lambda()
        table = self._provision_results_table()

        if wait:
            raise NotImplementedError()

        return (queue, function, table)

    def destroy(self):
        """
        Destroy this instance, force-terminating any running tasks.

        Destroys and terminates all cloud resources associated with this
        instance, so exercise proper caution.

        This function is best reserved for when a run appears to have gone
        astray and is running for too long.

        """
        raise NotImplementedError()

    @property
    def limits(self):
        return self._limits
