## *Function* `sort_motif_nodes_by_interestingness(motif: nx.Graph) -> dict`


Sort the nodes in a motif by their interestingness.

Most interesting nodes are defined to be those that most rapidly filter the list of nodes down to a smaller set.



## *Function* `find_motifs(motif: nx.DiGraph, host: nx.DiGraph) -> List[dict]`


Get a list of mappings from motif node IDs to host graph IDs.

### form

```
> - **motif_id** (`None`: `None`): host_id, ...}] ```

### Arguments
> - **motif** (`nx.DiGraph`: `None`): The motif graph (needle) to search for
> - **host** (`nx.DiGraph`: `None`): The host graph (haystack) to search within

### Returns
> - **List[dict]** (`None`: `None`): A list of mappings from motif node IDs to host graph IDs

