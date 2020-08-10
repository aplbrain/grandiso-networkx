## _Class_ `_GrandIsoLimit`

A limit supervisor that limits the execution of a GrandIso algorithm run.

## _Class_ `GrandIso`

A high-level class for managing cloud-scale subgraph isomorphism using the novel grand-iso backbone algorithm.

## _Function_ `instance_id(self)`

Get the unique instance ID for this run-instance of Grand-Iso.

## _Function_ `ready(self)`

Returns True if the instance is ready to begin execution.

## _Function_ `set_graph(self, graph: grand.Graph)`

Set a pointer to the dynamo-backed grand Graph object.

### Arguments

> -   **graph** (`grand.Graph`: `None`): The graph to use (must be dynamo-backed)

### Returns

    None

## _Function_ `_provision_queue(self)`

Provision the SQS for this run.

## _Function_ `_provision_backbone_lambda(self)`

Provision a new lambda function to run each backbone check.

## _Function_ `_provision_results_table(self)`

Provision a new DynamoDB table to hold the results of this run.

## _Function_ `provision_resources(self, wait: bool = True)`

Provision all cloud resources that will be required for this run.

### Arguments

> -   **wait** (`bool`: `True`): Whether to wait for all resources before

        returning from this call. If False, the user must await the         creation of resources manually.

### Returns

> -   **any]** (`None`: `None`): A tuple containing the provisioned resources

## _Function_ `destroy(self)`

Destroy this instance, force-terminating any running tasks.

Destroys and terminates all cloud resources associated with this instance, so exercise proper caution.

This function is best reserved for when a run appears to have gone astray and is running for too long.
