"""
- Provision a results table.
- Preprocessing
    - Identify highest-degree node in motif, M1
    - Identify second-highest degree node in motif, M2, connected to M1 by
        a single edge.
    - Identify all nodes with degree of M1 or greater in the host graph,
        which also have all required attributes of the M1 and M2 nodes. If
        neither M1 nor M2 have degree > 1 nor attributes, select M1 and M2 as
        two nodes with attributes defined.
    - Enumerate all paths in the host graph from M1 candidates to M2 candidates,
        as candidate "backbones" in a queue.
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
from typing import Dict, Hashable, List, Union

import itertools
import time
import queue

import networkx as nx

__version__ = "1.0.0"

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


def is_node_attr_match(
    motif_node_attrs: dict, host_graph_id: str, host: nx.Graph
) -> bool:
    """
    Check if a node in the host graph matches the attributes in the motif.

    Arguments:
        motif_node_attrs (dict): A dictionary of metadata on a motif node
        host_graph_id (str): The ID of metadata on the host graph
        host (nx.Graph): The host graph object

    Returns:
        bool: True if the host node matches the attributes in the motif

    """
    host_node = host.nodes[host_graph_id]

    for attr, val in motif_node_attrs.items():
        if attr not in host_node:
            return False
        if host_node[attr] != val:
            return False

    return True


def is_node_structural_match(
    motif_node_id: str, host_graph_id: str, motif: nx.Graph, host: nx.Graph
) -> bool:
    """
    Check if the motif node here is a valid structural match.

    Specifically, this requires that a host node has at least the degree as the
    motif node.

    Arguments:
        motif_node_id (str): The motif node ID
        host_graph_id (str): The host graph ID
        motif (nx.Graph): The motif graph
        host (nx.Graph): The host graph

    Returns:
        bool: True if the motif node maps to this host node

    """
    return host.degree(host_graph_id) >= motif.degree(motif_node_id)


def get_next_backbone_candidates(
    backbone: dict,
    motif: nx.Graph,
    host: nx.Graph,
    interestingness: dict,
    next_node: str = None,
    directed: bool = True,
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
        next_node = [k for k in interestingness.keys()][0]
        # Let's return ALL possible node choices for this next_node. To do this
        # without being an insane person, let's filter on max degree in host:
        return [
            {next_node: n}
            for n in host.nodes()
            if is_node_structural_match(next_node, n, motif, host)
        ]

    else:
        _node_with_greatest_backbone_count = None
        _greatest_backbone_count = 0
        for motif_node_id in motif.nodes():
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
                _node_with_greatest_backbone_count = motif_node_id
        # Now we have _node_with_greatest_backbone_count as the best candidate
        # for `next_node`.
        next_node = _node_with_greatest_backbone_count

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
        for (source, _, target) in required_edges:
            if directed:
                if source is not None:
                    # this is a "from" edge:
                    candidate_nodes_from_this_edge = list(host.adj[backbone[source]])
                elif target is not None:
                    # this is a "from" edge:
                    candidate_nodes_from_this_edge = list(host.pred[backbone[target]])
            else:
                candidate_nodes_from_this_edge = list(host.adj[backbone[target]])
            if len(candidate_nodes_set) == 0:
                # This is the first edge we're checking, so set the candidate
                # nodes set to ALL possible candidates.
                candidate_nodes_set.update(candidate_nodes_from_this_edge)
            else:
                candidate_nodes_set = candidate_nodes_set.intersection(
                    candidate_nodes_from_this_edge
                )
        candidate_nodes = list(candidate_nodes_set)

    elif len(required_edges) == 0:
        # Somehow you found a node that doesn't have any edges. This is bad.
        raise ValueError(
            f"Somehow you found a motif node {next_node} that doesn't have "
            + "any motif-graph edges. This is bad. (Did you maybe pass an "
            + "empty backbone to this function?)"
        )

    tentative_results = [
        {**backbone, next_node: c}
        for c in candidate_nodes
        if c not in backbone.values()
        and is_node_structural_match(next_node, c, motif, host)
    ]

    # One last filtering step here. This is to catch the cases where you have
    # successfully mapped each node, and the final node has some valid
    # candidate_nodes (and therefore `tentative_results`).
    # This is important: We must now check that for the assigned nodes, all
    # edges between them DO exist in the host graph. Otherwise, when we check
    # in find_motifs that len(motif) == len(mapping), we will discover that the
    # mapping is "complete" even though we haven't yet checked it at all.

    monomorphism_candidates = []

    for mapping in tentative_results:
        if len(mapping) == len(motif):
            if all(
                [
                    host.has_edge(mapping[motif_u], mapping[motif_v])
                    for motif_u, motif_v in motif.edges()
                ]
            ):
                # This is a "complete" match!
                monomorphism_candidates.append(mapping)
        else:
            # This is a partial match, so we'll continue building.
            monomorphism_candidates.append(mapping)

    if not isomorphisms_only:
        return monomorphism_candidates

    # Additionally, if isomorphisms_only == True, we can use this opportunity
    # to confirm that no spurious edges exist in the induced subgraph:
    isomorphism_candidates = []
    for result in monomorphism_candidates:
        for (motif_u, motif_v) in itertools.product(result.keys(), result.keys()):
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
            isomorphism_candidates.append(result)
    return isomorphism_candidates


def uniform_node_interestingness(motif: nx.Graph) -> dict:
    """
    Sort the nodes in a motif by their interestingness.

    Most interesting nodes are defined to be those that most rapidly filter the
    list of nodes down to a smaller set.

    """
    return {n: 1 for n in motif.nodes()}


class ProfilingQueue(queue.SimpleQueue):
    def __init__(self):
        super(ProfilingQueue, self).__init__()
        self._size_history = queue.SimpleQueue()
        self._size = 0

    def put(self, *args, **kwargs):
        res = super(ProfilingQueue, self).put(*args, **kwargs)
        self._size += 1
        self._size_history.put(self._size)
        return res

    def get(self, *args, **kwargs):
        res = super(ProfilingQueue, self).get(*args, **kwargs)
        self._size -= 1
        self._size_history.put(self._size)
        return res


def find_motifs(
    motif: nx.DiGraph,
    host: nx.DiGraph,
    interestingness: dict = None,
    count_only: bool = False,
    directed: bool = None,
    profile: bool = False,
    isomorphisms_only: bool = False,
    hints: List[Dict[Hashable, Hashable]] = None,
) -> List[dict]:
    """
    Get a list of mappings from motif node IDs to host graph IDs.

    Results are of the form:

    ```
    [{motif_id: host_id, ...}]
    ```

    Arguments:
        motif (nx.DiGraph): The motif graph (needle) to search for
        host (nx.DiGraph): The host graph (haystack) to search within
        interestingness (dict: None): A map of each node in `motif` to a float
            number that indicates an ordinality in which to address each node
        count_only (bool: False): If True, return only an integer count of the
            number of motifs, rather than a list of mappings.
        directed (bool: None): Whether direction should be considered during
            search. If omitted, this will be based upon the motif directedness.
        profile (bool: False): SLOWER! Whether to include additional metrics
            in addition to results. Note that you should only ever use this to
            debug or understand your results, not for use in production.
        isomorphisms_only (bool: False): Whether to return isomorphisms (the
            default is monomorphisms).

    Returns:
        List[dict]: A list of mappings from motif node IDs to host graph IDs
        int: If `count_only` is True, return the length of the List.

    """
    interestingness = interestingness or uniform_node_interestingness(motif)

    if directed is None:
        # guess directedness from motif
        if isinstance(motif, nx.DiGraph):
            # This will be a directed query.
            directed = True
        else:
            directed = False

    if profile:
        q = ProfilingQueue()
    else:
        q = queue.SimpleQueue()

    results = []
    results_count = 0

    # Kick off the queue with an empty candidate:
    if hints is None or hints == []:
        q.put({})
    else:
        for hint in hints:
            q.put(hint)

    while not q.empty():
        new_backbone = q.get()
        next_candidate_backbones = get_next_backbone_candidates(
            new_backbone,
            motif,
            host,
            interestingness,
            directed=directed,
            isomorphisms_only=isomorphisms_only,
        )

        for candidate in next_candidate_backbones:
            if len(candidate) == len(motif):
                if count_only:
                    results_count += 1
                else:
                    results.append(candidate)
            else:
                q.put(candidate)

    if profile:
        if count_only:
            return results_count, q
        return results, q
    if count_only:
        return results_count
    return results

