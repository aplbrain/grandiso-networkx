# Grand Isomorphisms

Grand is a virtual graph database. Because DynamoDB is a true-serverless database, it makes sense to use serverless scalable technologies to run graph queries against Grand.

In particular, subgraph isomorphism is a resource-heavy (but branch-parallelizable) algorithm that is hugely impactful for large graph analysis. SotA algorithms for this (Ullmann, VF2, BB-Graph) are heavily RAM-bound, but this is due to a large number of small processes each of which hold a small portion of a traversal tree in memory.

_Grand-Iso_ is a subgraph isomorphism algorithm that leverages serverless technology to run in the AWS cloud at infinite scale.\*

> <small>\* You may discover that "infinite" here is predominantly bounded by your wallet, which is no joke.</small>

## Pseudocode for novel "Grand-Iso" algorithm

```
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
```
