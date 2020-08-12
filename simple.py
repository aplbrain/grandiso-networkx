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

from typing import List
import time
import queue
import numpy as np

import networkx as nx
from networkx.algorithms.isomorphism import DiGraphMatcher

"""
In this process, the following operations are fast:

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
    Check if a node in the host graph matches the attributes in the motif
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
    """
    return host.degree(host_graph_id) >= motif.degree(motif_node_id)


def get_next_backbone_candidates(
    backbone: dict,
    motif: nx.Graph,
    host: nx.Graph,
    interestingness: dict,
    next_node: str = None,
    enforce_inequality: bool = True,
) -> List[dict]:
    """
    Get a list of candidate node assignments for the next "step" of this map.

    Arguments:
        backbone (dict): Mapping of motif node IDs to one set of host graph IDs
        motif (Graph): A graph representation of the motif
        host (Graph): The host graph, complete
        interestingness (dict): A mapping of motif node IDs to interestingness
        next_node (str: None): Optional suggestion for the next node to assign
        enforce_inequality (bool: True): If true, two nodes in backbone cannot
            be assigned to the same host-graph

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
        (source, me, target) = required_edges[0]
        if source:
            # this is a "from" edge:
            candidate_nodes = list(host.adj[backbone[source]])
        elif target:
            # this is a "from" edge:
            candidate_nodes = list(host.pred[backbone[target]])
        # Thus, all candidates for motif ID `$next_node` are stored in the
        # candidate_nodes list.

    elif len(required_edges) > 1:
        # This is neato :) It means that there are multiple edges in the host
        # graph that we can use to downselect the number of candidate nodes.
        candidate_nodes_set = set()
        for (source, me, target) in required_edges:
            if source:
                # this is a "from" edge:
                candidate_nodes_from_this_edge = list(host.adj[backbone[source]])
            elif target:
                # this is a "from" edge:
                candidate_nodes_from_this_edge = list(host.pred[backbone[target]])

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

    return [
        {**backbone, next_node: c}
        for c in candidate_nodes
        if c not in backbone.values()
    ]


def sort_motif_nodes_by_interestingness(motif: nx.Graph) -> dict:
    """
    Sort the nodes in a motif by their interestingness.

    Most interesting nodes are defined to be those that most rapidly filter the
    list of nodes down to a smaller set.

    """
    Warning("Bad implementation for sort_motif_nodes_by_interestingness")
    return {n: 1 for n in motif.nodes()}


def find_motifs(motif: nx.DiGraph, host: nx.DiGraph) -> List[dict]:

    interestingness = sort_motif_nodes_by_interestingness(motif)

    q = queue.SimpleQueue()
    results = []

    q.put({})

    while q.qsize():
        new_backbone = q.get()
        next_candidate_backbones = get_next_backbone_candidates(
            new_backbone, motif, host, interestingness
        )

        for candidate in next_candidate_backbones:
            if len(candidate) == len(motif):
                results.append(candidate)
            else:
                q.put(candidate)

    return results


def main():

    host = nx.fast_gnp_random_graph(20, 0.8, directed=True)

    motif = nx.DiGraph()
    motif.add_edge("A", "B")
    motif.add_edge("B", "C")
    motif.add_edge("C", "D")
    motif.add_edge("D", "A")

    import pandas as pd

    ours = pd.DataFrame([i for i in find_motifs(motif, host)])

    gm = DiGraphMatcher(host, motif)
    theirs = pd.DataFrame(
        [{v: k for k, v in i.items()} for i in gm.subgraph_monomorphisms_iter()]
    )

    diff_rows_count = len(pd.concat([ours, theirs]).drop_duplicates(keep=False))
    print("Difference count between results: ", diff_rows_count)


if __name__ == "__main__":
    main()
    # import cProfile

    # cProfile.run("main()")

