"""
In this process, we consider the following operations to be fast:

- Get degree of node
- Get downstream targets of node
- Get attributes on a node

These operations are medium:

- Get upstream sources of node
- Get degrees of all nodes in host graph
- Get nodes with a certain attribute

These operations are slow:
- Get edges where nodes have a certain attribute
    - But you can do the same with get-downstream-targets and filter an
      attribute search.
"""

from typing import Dict, Generator, Hashable, List, Union, Tuple
import itertools
from functools import lru_cache

import networkx as nx

__version__ = "2.2.0"


@lru_cache()
def _is_node_attr_match(
    motif_node_id: str, host_node_id: str, motif: nx.Graph, host: nx.Graph
) -> bool:
    """
    Check if a node in the host graph matches the attributes in the motif.

    Arguments:
        motif_node_id (str): The motif node ID
        host_node_id (str): The host graph ID
        motif (nx.Graph): The motif graph
        host (nx.Graph): The host graph

    Returns:
        bool: True if the host node matches the attributes in the motif

    """
    motif_node = motif.nodes[motif_node_id]
    host_node = host.nodes[host_node_id]

    for attr, val in motif_node.items():
        if attr not in host_node:
            return False
        if host_node[attr] != val:
            return False

    return True


@lru_cache()
def _is_node_structural_match(
    motif_node_id: str, host_node_id: str, motif: nx.Graph, host: nx.Graph
) -> bool:
    """
    Check if the motif node here is a valid structural match.

    Specifically, this requires that a host node has at least the degree as the
    motif node.

    Arguments:
        motif_node_id (str): The motif node ID
        host_node_id (str): The host graph ID
        motif (nx.Graph): The motif graph
        host (nx.Graph): The host graph

    Returns:
        bool: True if the motif node maps to this host node

    """
    return host.degree(host_node_id) >= motif.degree(motif_node_id)


@lru_cache()
def _is_edge_attr_match(
    motif_edge_id: Tuple[str, str],
    host_edge_id: Tuple[str, str],
    motif: nx.Graph,
    host: nx.Graph,
) -> bool:
    """
    Check if an edge in the host graph matches the attributes in the motif.

    Arguments:
        motif_edge_id (str): The motif edge ID
        host_edge_id (str): The host edge ID
        motif (nx.Graph): The motif graph
        host (nx.Graph): The host graph

    Returns:
        bool: True if the host edge matches the attributes in the motif

    """
    motif_edge = motif.edges[motif_edge_id]
    host_edge = host.edges[host_edge_id]

    for attr, val in motif_edge.items():
        if attr not in host_edge:
            return False
        if host_edge[attr] != val:
            return False

    return True


def get_next_backbone_candidates(
    backbone: dict,
    motif: nx.Graph,
    host: nx.Graph,
    interestingness: dict,
    next_node: str = None,
    directed: bool = True,
    is_node_structural_match=_is_node_structural_match,
    is_node_attr_match=_is_node_attr_match,
    is_edge_attr_match=_is_edge_attr_match,
    isomorphisms_only: bool = False,
) -> List[dict]:
    """
    Get a list of candidate node assignments for the next "step" of this map.

    Arguments:
        backbone (dict): Mapping of motif node IDs to one set of host graph IDs
        motif (Graph): A graph representation of the motif
        host (Graph): The host graph, complete
        interestingness (dict): A mapping of motif node IDs to interestingness
        next_node (str: None): Optional suggestion for the next node to assign
        directed (bool: True): Whether host and motif are both directed
        isomorphisms_only (bool: False): If true, only isomorphisms will be
            returned (instead of all monomorphisms)

    Returns:
        List[dict]: A new list of mappings with one additional element mapped

    """

    # Get a list of the "exploration front" of the motif -- nodes that are not
    # yet assigned in the backbone but are connected to at least one assigned
    # node in the backbone.

    # For example, in the motif A -> B -> C, if A is already assigned, then the
    # front is [B] (c is not included because it has not connection to any
    # assigned node).

    # We should prefer nodes that are connected to multiple assigned backbone
    # nodes, because these will filter more rapidly to a smaller set.

    # First check if the backbone is empty. If so, we should choose the most
    # interesting node to start with:
    if next_node is None and len(backbone) == 0:
        # This is the starting-case, where we have NO backbone nodes set yet.
        next_node = max(
            interestingness.keys(), key=lambda node: interestingness.get(node, 0.0)
        )
        # Let's return ALL possible node choices for this next_node. To do this
        # without being an insane person, let's filter on max degree in host:
        for n in host.nodes:
            if is_node_attr_match(
                next_node, n, motif, host
            ) and is_node_structural_match(next_node, n, motif, host):
                print({next_node: n},"(Base Case) Next Node used to find candidate node")
                yield {next_node: n}
        return

    else:
        _nodes_with_greatest_backbone_count: List[str] = []
        _greatest_backbone_count = 0
        for motif_node_id in motif.nodes:
            if motif_node_id in backbone:
                continue
            # How many connections to existing backbone?
            # Note that this number is certainly greater than or equal to 1,
            # since a value of 0 would imply that the backbone dict is empty
            # (which we have already handled) or that the motif has more than
            # one connected component, which we check for at prep-time.
            if directed:
                motif_backbone_connections_count = sum(
                    [
                        1
                        for v in list(
                            set(motif.adj[motif_node_id]).union(
                                set(motif.pred[motif_node_id])
                            )
                        )
                        if v in backbone
                    ]
                )
            else:
                motif_backbone_connections_count = sum(
                    [1 for v in motif.adj[motif_node_id] if v in backbone]
                )
            # If this is the most highly connected node visited so far, then
            # set it as the next node to explore:
            if motif_backbone_connections_count > _greatest_backbone_count:
                _nodes_with_greatest_backbone_count.append(motif_node_id)
                _greatest_backbone_count = motif_backbone_connections_count
        # Now we have _node_with_greatest_backbone_count as the best candidate
        # for `next_node`.
        next_node = max(
            _nodes_with_greatest_backbone_count,
            key=lambda node: interestingness.get(node, 0.0),
        )
        print({next_node},"Next Node used to find candidate node")

    # Now we have a node `next_node` which we know is connected to the current
    # backbone. Get all edges between `next_node` and nodes in the backbone,
    # and verify that they exist in the host graph:
    # `required_edges` has the form (prev, self, next), with non-values filled
    # with None. That way we can easily remember and store the roles of the
    # node IDs in the next step.
    required_edges = []
    for other in list(motif.adj[next_node]):
        if other in backbone:
            # edge is (next_node, other)
            required_edges.append((None, next_node, other))
    if directed:
        for other in list(motif.pred[next_node]):
            if other in backbone:
                # edge is (other, next_node)
                required_edges.append((other, next_node, None))

    # `required_edges` now contains a list of all edges that exist in the motif
    # graph, and we must find candidate nodes that have such edges in the host.

    candidate_nodes = []

    # In the worst-case, `required_edges` has length == 1. This is the worst
    # case because it means that ALL edges from/to `other` are valid options.
    if len(required_edges) == 1:
        # :(
        (source, _, target) = required_edges[0]
        if directed:
            if source is not None:
                # this is a "from" edge:
                candidate_nodes = list(host.adj[backbone[source]])
            elif target is not None:
                # this is a "from" edge:
                candidate_nodes = list(host.pred[backbone[target]])
        else:
            candidate_nodes = list(host.adj[backbone[target]])
        # Thus, all candidates for motif ID `$next_node` are stored in the
        # candidate_nodes list.

    elif len(required_edges) > 1:
        # This is neato :) It means that there are multiple edges in the host
        # graph that we can use to downselect the number of candidate nodes.
        candidate_nodes_set = set()
        for source, _, target in required_edges:
            if directed:
                if source is not None:
                    # this is a "from" edge:
                    candidate_nodes_from_this_edge = host.adj[backbone[source]]
                # elif target is not None:
                else:  # target is not None:
                    # this is a "from" edge:
                    candidate_nodes_from_this_edge = host.pred[backbone[target]]
                # else:
                #     raise AssertionError("Encountered an impossible condition: At least one of source or target must be defined.")
            else:
                candidate_nodes_from_this_edge = host.adj[backbone[target]]
            if len(candidate_nodes_set) == 0:
                # This is the first edge we're checking, so set the candidate
                # nodes set to ALL possible candidates.
                candidate_nodes_set.update(candidate_nodes_from_this_edge)
            else:
                candidate_nodes_set = candidate_nodes_set.intersection(
                    candidate_nodes_from_this_edge
                )
        candidate_nodes = list(candidate_nodes_set)
        print(candidate_nodes,"Candidate Nodes ")

    elif len(required_edges) == 0:
        # Somehow you found a node that doesn't have any edges. This is bad.
        raise ValueError(
            f"Somehow you found a motif node {next_node} that doesn't have "
            + "any motif-graph edges. This is bad. (Did you maybe pass an "
            + "empty backbone to this function?)"
        )

    def tentative_results():
        for c in candidate_nodes:
            if (
                c not in backbone.values()
                and is_node_attr_match(next_node, c, motif, host)
                and is_node_structural_match(next_node, c, motif, host)
            ):
               
                print("tentative results", {**backbone, next_node: c})
                yield {**backbone, next_node: c}

    # One last filtering step here. This is to catch the cases where you have
    # successfully mapped each node, and the final node has some valid
    # candidate_nodes (and therefore `tentative_results`).
    # This is important: We must now check that for the assigned nodes, all
    # edges between them DO exist in the host graph. Otherwise, when we check
    # in find_motifs that len(motif) == len(mapping), we will discover that the
    # mapping is "complete" even though we haven't yet checked it at all.

    def monomorphism_candidates():
        for mapping in tentative_results():
            if len(mapping) == len(motif):
                if all(
                    [
                        host.has_edge(mapping[motif_u], mapping[motif_v])
                        and is_edge_attr_match(
                            (motif_u, motif_v),
                            (mapping[motif_u], mapping[motif_v]),
                            motif,
                            host,
                        )
                        for motif_u, motif_v in motif.edges
                    ]
                ):
                    # This is a "complete" match!
                    print("monomorphism_candidates() complete match", mapping)
                    yield mapping
            else:
                # This is a partial match, so we'll continue building.
                yield mapping

    if not isomorphisms_only:

        yield from monomorphism_candidates()
        return

    # Additionally, if isomorphisms_only == True, we can use this opportunity
    # to confirm that no spurious edges exist in the induced subgraph:
    def isomorphism_candidates():
        for result in monomorphism_candidates():
            for motif_u, motif_v in itertools.product(result.keys(), result.keys()):
                # if the motif has this edge, then it doesn't rule any of the
                # above results out as an isomorphism.
                # if the motif does NOT have the edge, then NO RESULT may have
                # the equivalent edge in the host graph:
                if not motif.has_edge(motif_u, motif_v) and host.has_edge(
                    result[motif_u], result[motif_v]
                ):
                    # this is a violation.
                    break
            else:
                print("isonomorphism_candidates() complete match", result)
                yield result

    yield from isomorphism_candidates()


def uniform_node_interestingness(motif: nx.Graph) -> dict:
    """
    Sort the nodes in a motif by their interestingness.

    Most interesting nodes are defined to be those that most rapidly filter the
    list of nodes down to a smaller set.

    """
    return {n: 1 for n in motif.nodes}


def find_motifs_iter(
    motif: nx.Graph,
    host: nx.Graph,
    interestingness: dict = None,
    directed: bool = None,
    isomorphisms_only: bool = False,
    hints: List[Dict[Hashable, Hashable]] = None,
    is_node_structural_match=_is_node_structural_match,
    is_node_attr_match=_is_node_attr_match,
    is_edge_attr_match=_is_edge_attr_match,
) -> Generator[dict, None, None]:
    """
    Yield mappings from motif node IDs to host graph IDs.

    Results are of the form:

    ```
    {motif_id: host_id, ...}
    ```

    Arguments:
        motif (nx.DiGraph): The motif graph (needle) to search for
        host (nx.DiGraph): The host graph (haystack) to search within
        interestingness (dict: None): A map of each node in `motif` to a float
            number that indicates an ordinality in which to address each node
        directed (bool: None): Whether direction should be considered during
            search. If omitted, this will be based upon the motif directedness.
        hints (dict): A dictionary of initial starting mappings. By default,
            searches for all instances. You can constrain a node by passing a
            list with a single dict item: `[{motifId: hostId}]`.
        isomorphisms_only (bool: False): Whether to return isomorphisms (the
            default is monomorphisms).

    Returns:
        Generator[dict, None, None]

    """
    interestingness = interestingness or uniform_node_interestingness(motif)
    if directed is None:
        # guess directedness from motif
        if isinstance(motif, nx.DiGraph):
            # This will be a directed query.
            directed = True
        else:
            directed = False

    # List of starting paths, defaults to searching all instances if hints is empty
    paths = hints if hints else [{}]

    # Graph path traversal function
    recursive_depth_states = {}
    def walk(path,recursive_level = 1,recursive_id = [0]):
        recursive_id[0] += 1
        print(recursive_level,"recursive_level _")
        print(recursive_id[0],"recursive_id _")

        print('\n')
        if path and len(path) == len(motif):
            # Path complete
            print(path,"path complete from find_motifs iter() loop")
            yield path
        else:
            # Iterate over path candidates
            candidate_paths = []
            for candidate in get_next_backbone_candidates(
                path,
                motif,
                host,
                interestingness,
                directed=directed,
                isomorphisms_only=isomorphisms_only,
                is_node_structural_match=is_node_structural_match,
                is_node_attr_match=is_node_attr_match,
                is_edge_attr_match=is_edge_attr_match,
            ):  
                print(candidate," candidate extracted from next backbone walk() function from  find_motifs iter")
                print(recursive_level,"recursive_level -")
                print(recursive_id[0],"recursive_id -")
                print('\n')
                candidate_paths.append(candidate)
                print(candidate_paths,"candidate paths")
                yield from walk(candidate,recursive_level + 1, recursive_id)

            
            if recursive_level not in recursive_depth_states:
                recursive_depth_states[recursive_level] = []
            recursive_depth_states[recursive_level].extend(candidate_paths)


    # Traverse graph and yield mappings
    
    for path in paths:
        print(path,"path from find_motifs_iter() loop")
        yield from walk(path)

    states = []
    for key in recursive_depth_states:
        states.append({key:recursive_depth_states[key]})

    print(recursive_depth_states,'recursive_depth_states')
    print('\n')
    print('tree_root_paths')
    root_trees = make_root_trees(recursive_depth_states)
    print_root_trees(root_trees)


def get_roots(trees):
    roots = []
    for path in trees.keys():
        if len(path.split(",")) == 1:
            roots.append(path)
    return roots

def print_edges(level, is_last_child):
    """Generates a string with the appropriate edges for the current tree level."""
    edge = ""
    for i in range(level):
        edge += "|  "
    if level > 0:
        edge += "|--" if not is_last_child else "`--"
    return edge


def dfs(graph, node, level=0):
    """Performs a depth-first search and prints each node with a visual representation of edges."""
    children = graph.get(node, [])
    for i, child in enumerate(children):
        is_last_child = i == (len(children) - 1)
        edge = print_edges(level, is_last_child)
        print(f"{edge}{child}")
        dfs(graph, child, level + 1)

def print_root_trees(trees):
    roots = get_roots(trees)
    for root in roots:
        print(root)
        dfs(trees, root, 0)



        
def make_root_trees(recursive_depth_states):
    levels = sorted(list(recursive_depth_states.keys()))
    
    trees = {}
    for i in range(len(levels)):

        level = levels[i]
        for path in recursive_depth_states[level]:

            trees[get_path_str(path)] = []

            if i == len(levels)-1:
                continue
            
            next_level = level+1
           
            for next_path in recursive_depth_states[next_level]:

                keys = list(path.keys())
                isExpanded = True
                for i in range(len(keys)):
                    key_one = keys[i]
                    
                    if key_one not in next_path:
                        isExpanded = False
                        break
                    if path[key_one] != next_path[key_one]:
                        isExpanded = False
                        break
              
                if isExpanded:
                    trees[get_path_str(path)].append(get_path_str(next_path))

    return trees


def get_path_str(path):
    res = []
    for key in path.keys():
        res.append(key+':'+path[key])
    return ",".join(res)


def print_trees(trees):
    complete_paths =[]
    all_paths = []
    for path in trees:
        if len(path.split(",")) == 4:
            complete_paths.append(path)
        all_paths.append(path)

    for path in complete_paths:
        print_tree(path,trees)

    
def print_tree(complete_path,trees):
    res = []
    current_path = complete_path
    while current_path != None:
        res.append(current_path)
        current_path = trees[current_path]
    res = res[::-1]
    print(res)
    print('\n')





def find_motifs(
    motif: nx.Graph,
    host: nx.Graph,
    *args,
    count_only: bool = False,
    limit: int = None,
    is_node_attr_match=_is_node_attr_match,
    is_node_structural_match=_is_node_structural_match,
    is_edge_attr_match=_is_edge_attr_match,
    **kwargs,
) -> Union[int, List[dict]]:
    """
    Get a list of mappings from motif node IDs to host graph IDs.

    Results are of the form:

    ```
    [{motif_id: host_id, ...}]
    ```

    See grandiso#find_motifs_iter for full argument list.

    Arguments:
        count_only (bool: False): If True, return only an integer count of the
            number of motifs, rather than a list of mappings.
        limit (int: None): A limit to place on the number of returned mappings.
            The search will terminate once the limit is reached.


    Returns:
        int: If `count_only` is True, return the length of the List.
        List[dict]: A list of mappings from motif node IDs to host graph IDs

    """
    print("find_motifs() called")
    results = []
    results_count = 0
    for qresult in find_motifs_iter(
        motif,
        host,
        *args,
        is_node_attr_match=is_node_attr_match,
        is_node_structural_match=is_node_structural_match,
        is_edge_attr_match=is_edge_attr_match,
        **kwargs,
    ):

        result = qresult

        results_count += 1
        if limit and results_count >= limit:
            if count_only:
                return results_count
            else:
                # Subtract 1 from results_count because we have not yet
                # added the new result to the results list, but we HAVE
                # already added +1 to the count.
                if limit and (results_count - 1) >= limit:
                    return results
        if not count_only:
            results.append(result)

    if count_only:
        return results_count
    print("results",results)
    return results
