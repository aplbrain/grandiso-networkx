## *Class* `_GrandIsoLimit`


A limit supervisor that limits the execution of a GrandIso algorithm run.



## *Class* `GrandIso`


A high-level class for managing cloud-scale subgraph isomorphism using the novel grand-iso backbone algorithm.

### Pseudocode

    - Provision a DynamoDB table for result storage.     - Preprocessing
        - Identify highest-degree node in motif, M1         - Identify second-highest degree node in motif, M2, connected to M1 by
            a single edge.
        - Identify all nodes with degree of M1 or greater in the host graph,
            which also have all required attributes of the M1 and M2 nodes. If             neither M1 nor M2 have degree > 1 nor attributes, select M1 and M2 as             two nodes with attributes defined.
        - Enumerate all paths in the host graph from M1 candidates to M2 candidates,
            as candidate "backbones" in AWS SQS.
    - Motif Search
### candidate
### Lambda
                - Pop the backbone from the queue.                 - Traverse all shortest paths in the motif starting at the nearest
                    of either M1 or M2
                - If multiple nodes are valid candidates, queue a new backbone with
                    each option, and terminate the current Lambda.
                - When all paths are valid paths in the host graph, add the list
                    of participant nodes to a result in the DynamoDB table.
    - Reporting
        - Return a serialization of the results from the DynamoDB table.
    - Cleanup
        - Delete the backbone queue         - Delete the results table (after collection)



## *Function* `instance_id(self)`


Get the unique instance ID for this run-instance of Grand-Iso.



## *Function* `ready(self)`


Returns True if the instance is ready to begin execution.


## *Function* `set_graph(self, graph: grand.Graph)`


Set a pointer to the dynamo-backed grand Graph object.

### Arguments
> - **graph** (`grand.Graph`: `None`): The graph to use (must be dynamo-backed)

### Returns
    None



## *Function* `_provision_queue(self)`


Provision the SQS for this run.



## *Function* `_provision_backbone_lambda(self)`


Provision a new lambda function to run each backbone check.



## *Function* `_provision_results_table(self)`


Provision a new DynamoDB table to hold the results of this run.



## *Function* `provision_resources(self, wait: bool = True)`


Provision all cloud resources that will be required for this run.

### Arguments
> - **wait** (`bool`: `True`): Whether to wait for all resources before
        returning from this call. If False, the user must await the         creation of resources manually.

### Returns
> - **any]** (`None`: `None`): A tuple containing the provisioned resources



## *Function* `destroy(self)`


Destroy this instance, force-terminating any running tasks.

Destroys and terminates all cloud resources associated with this instance, so exercise proper caution.

This function is best reserved for when a run appears to have gone astray and is running for too long.

