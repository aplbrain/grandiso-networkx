# Grand Isomorphisms

Subgraph isomorphism is a resource-heavy (but branch-parallelizable) algorithm that is hugely impactful for large graph analysis. SotA algorithms for this (Ullmann, VF2, BB-Graph) are heavily RAM-bound, but this is due to a large number of small processes each of which hold a small portion of a traversal tree in memory.

_Grand-Iso_ is a subgraph isomorphism algorithm that exchanges this resource-limitation for a parallelizable (albeit much much longer) partial-match queue structure.

## Pseudocode for novel "Grand-Iso" algorithm

```
- Accept a motif M, and a host graph H.
- Create an empty list for result storage, R.
- Create an empty queue, Q.
- Preprocessing
    - Identify the most "interesting" node in motif M, m1.
    - Add to Q a set of mappings with a single node, with one map for all
        nodes in H that satisfy the requirements of m1: degree, attributes, etc
- Motif Search
    - "Pop" a backbone B from Q
        - Identify as m1 the most interesting node in motif M that does not yet
            have a mapping assigned in B.
        - Identify all nodes that are valid mappings from the backbone to m1,
            based upon degree, attributes, etc.
        - If multiple nodes are valid candidates, add each new backbone to Q.
        - Otherwise, when all nodes in M have a valid mapping in B to H, add
            the mapping to the results set R.
    - Continue while there are still backbones in Q.
- Reporting
    - Return the set R to the user.
```

## Example Usage

```python
import networkx as nx

host = nx.fast_gnp_random_graph(10, 0.5)

motif = nx.Graph()
motif.add_edge("A", "B")
motif.add_edge("B", "C")
motif.add_edge("C", "D")
motif.add_edge("D", "A")

len(find_motifs(motif, host))
```

Directed graph support:

```python
import networkx as nx

host = nx.fast_gnp_random_graph(10, 0.5, directed=True)

motif = nx.DiGraph()
motif.add_edge("A", "B")
motif.add_edge("B", "C")
motif.add_edge("C", "D")
motif.add_edge("D", "A")

len(find_motifs(motif, host))
```
