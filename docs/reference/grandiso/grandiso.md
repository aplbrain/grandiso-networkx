## _Function_ `uniform_node_interestingness(motif: nx.Graph) -> dict`

Sort the nodes in a motif by their interestingness.

Most interesting nodes are defined to be those that most rapidly filter the list of nodes down to a smaller set.

## _Function_ `find_motifs(motif: nx.Graph, host: nx.Graph) -> List[dict]`

Get a list of mappings from motif node IDs to host graph IDs.

### Arguments

> -   **motif** (`nx.Graph`: `None`): The motif graph (needle) to search for
> -   **host** (`nx.Graph`: `None`): The host graph (haystack) to search within

### Returns

> -   **List[dict]** (`None`: `None`): A list of mappings from motif node IDs to host graph IDs
