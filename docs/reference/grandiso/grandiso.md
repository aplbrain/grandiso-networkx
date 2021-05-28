## _Function_ `_is_node_attr_match(motif_node_id: str, host_node_id: str, motif: nx.Graph, host: nx.Graph) -> bool`

Check if a node in the host graph matches the attributes in the motif.

### Arguments

> -   **motif_node_id** (`str`: `None`): The motif node ID
> -   **host_node_id** (`str`: `None`): The host graph ID
> -   **motif** (`nx.Graph`: `None`): The motif graph
> -   **host** (`nx.Graph`: `None`): The host graph

### Returns

> -   **bool** (`None`: `None`): True if the host node matches the attributes in the motif

## _Function_ `_is_node_structural_match(motif_node_id: str, host_node_id: str, motif: nx.Graph, host: nx.Graph) -> bool`

Check if the motif node here is a valid structural match.

Specifically, this requires that a host node has at least the degree as the motif node.

### Arguments

> -   **motif_node_id** (`str`: `None`): The motif node ID
> -   **host_node_id** (`str`: `None`): The host graph ID
> -   **motif** (`nx.Graph`: `None`): The motif graph
> -   **host** (`nx.Graph`: `None`): The host graph

### Returns

> -   **bool** (`None`: `None`): True if the motif node maps to this host node

## _Function_ `get_next_backbone_candidates(backbone: dict, motif: nx.Graph, host: nx.Graph, interestingness: dict, next_node: str = None, directed: bool = True, is_node_structural_match=_is_node_structural_match, is_node_attr_match=_is_node_attr_match, isomorphisms_only: bool = False) -> List[dict]`

Get a list of candidate node assignments for the next "step" of this map.

### Arguments

> -   **backbone** (`dict`: `None`): Mapping of motif node IDs to one set of host graph IDs
> -   **motif** (`Graph`: `None`): A graph representation of the motif
> -   **host** (`Graph`: `None`): The host graph, complete
> -   **interestingness** (`dict`: `None`): A mapping of motif node IDs to interestingness
> -   **next_node** (`str`: `None`): Optional suggestion for the next node to assign
> -   **directed** (`bool`: `True`): Whether host and motif are both directed
> -   **isomorphisms_only** (`bool`: `False`): If true, only isomorphisms will be

        returned (instead of all monomorphisms)

### Returns

> -   **List[dict]** (`None`: `None`): A new list of mappings with one additional element mapped

## _Function_ `uniform_node_interestingness(motif: nx.Graph) -> dict`

Sort the nodes in a motif by their interestingness.

Most interesting nodes are defined to be those that most rapidly filter the list of nodes down to a smaller set.

## _Function_ `find_motifs_iter(motif: nx.Graph, host: nx.Graph, interestingness: dict = None, directed: bool = None, queue_=queue.SimpleQueue, isomorphisms_only: bool = False, hints: List[Dict[Hashable, Hashable]] = None, is_node_structural_match=_is_node_structural_match, is_node_attr_match=_is_node_attr_match) -> Generator[dict, None, None]`

Yield mappings from motif node IDs to host graph IDs.

### Arguments

> -   **motif** (`nx.DiGraph`: `None`): The motif graph (needle) to search for
> -   **host** (`nx.DiGraph`: `None`): The host graph (haystack) to search within
> -   **interestingness** (`dict`: `None`): A map of each node in `motif` to a float

        number that indicates an ordinality in which to address each node

> -   **directed** (`bool`: `None`): Whether direction should be considered during

        search. If omitted, this will be based upon the motif directedness.

> -   **queue\_** (`queue.Queue`: `None`): What kind of queue to use.
> -   **hints** (`dict`: `None`): A dictionary of initial starting mappings. By default,

        searches for all instances. You can constrain a node by passing a

> -   **item** (`None`: `None`): `[{motifId: hostId}]`.
> -   **isomorphisms_only** (`bool`: `False`): Whether to return isomorphisms (the

        default is monomorphisms).

### Returns

    Generator[dict, None, None]

## _Function_ `find_motifs(motif: nx.Graph,host: nx.Graph,*args,count_only: bool = False,limit: int = None,is_node_attr_match=_is_node_attr_match,is_node_structural_match=_is_node_structural_match,**kwargs) -> Union[int, List[dict]]`

Get a list of mappings from motif node IDs to host graph IDs.

See grandiso#find_motifs_iter for full argument list.

### Arguments

> -   **count_only** (`bool`: `False`): If True, return only an integer count of the

        number of motifs, rather than a list of mappings.

> -   **limit** (`int`: `None`): A limit to place on the number of returned mappings.

        The search will terminate once the limit is reached.

### Returns

> -   **int** (`None`: `None`): If `count_only` is True, return the length of the List.
> -   **List[dict]** (`None`: `None`): A list of mappings from motif node IDs to host graph IDs
