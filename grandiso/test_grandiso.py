import time
import copy
import random
import pytest

import networkx as nx
from networkx.algorithms.isomorphism import DiGraphMatcher, GraphMatcher

from . import find_motifs


class TestSubgraphMatching:
    def test_finds_no_triangles_in_zero_tri_graph(self):

        motif = nx.DiGraph()
        motif.add_edge("A", "B")
        motif.add_edge("B", "C")
        motif.add_edge("C", "A")

        host = nx.DiGraph()
        host.add_edge("A", "B")
        host.add_edge("B", "C")

        assert len(find_motifs(motif, host)) == 0

    def test_finds_no_rect_in_zero_rect_graph(self):

        motif = nx.DiGraph()
        motif.add_edge("A", "B")
        motif.add_edge("B", "C")
        motif.add_edge("C", "D")
        motif.add_edge("D", "A")

        host = nx.DiGraph()
        host.add_edge("A", "B")
        host.add_edge("B", "C")
        host.add_edge("C", "D")

        assert len(find_motifs(motif, host)) == 0

    def test_finds_no_triangles_in_zero_tri_graph_with_context(self):

        motif = nx.DiGraph()
        motif.add_edge("A", "B")
        motif.add_edge("B", "C")
        motif.add_edge("C", "A")
        motif.add_edge("C", "D")
        motif.add_edge("C", "E")

        host = nx.DiGraph()
        host.add_edge("A", "B")
        host.add_edge("B", "C")

        assert len(find_motifs(motif, host)) == 0

    def test_finds_no_motifs_in_small_graph(self):

        motif = nx.DiGraph()
        motif.add_edge("A", "B")
        motif.add_edge("B", "C")

        host = nx.DiGraph()
        host.add_edge("A", "B")

        assert len(find_motifs(motif, host)) == 0

    def test_subgraph_equals_graph_triangle(self):

        motif = nx.DiGraph()
        motif.add_edge("A", "B")
        motif.add_edge("B", "C")
        motif.add_edge("C", "A")

        host = nx.DiGraph()
        host.add_edge("A", "B")
        host.add_edge("B", "C")
        host.add_edge("C", "A")

        assert len(find_motifs(motif, host)) == 3

    def test_subgraph_equals_graph_triangle_count_only(self):

        motif = nx.DiGraph()
        motif.add_edge("A", "B")
        motif.add_edge("B", "C")
        motif.add_edge("C", "A")

        host = nx.DiGraph()
        host.add_edge("A", "B")
        host.add_edge("B", "C")
        host.add_edge("C", "A")

        assert find_motifs(motif, host, count_only=True) == 3

    def test_subgraph_equals_graph_rect(self):

        motif = nx.DiGraph()
        motif.add_edge("A", "B")
        motif.add_edge("B", "C")
        motif.add_edge("C", "D")
        motif.add_edge("D", "A")

        host = nx.DiGraph()
        host.add_edge("A", "B")
        host.add_edge("B", "C")
        host.add_edge("C", "D")
        host.add_edge("D", "A")

        assert len(find_motifs(motif, host)) == 4

    def test_rect_count_matches_nx(self):

        host = nx.fast_gnp_random_graph(10, 0.5, directed=True)

        motif = nx.DiGraph()
        motif.add_edge("A", "B")
        motif.add_edge("B", "C")
        motif.add_edge("C", "D")
        motif.add_edge("D", "A")

        assert len(find_motifs(motif, host)) == len(
            [i for i in DiGraphMatcher(host, motif).subgraph_monomorphisms_iter()]
        )

    def test_tri_count_matches_nx(self):

        host = nx.fast_gnp_random_graph(10, 0.5, directed=True)

        motif = nx.DiGraph()
        motif.add_edge("A", "B")
        motif.add_edge("B", "C")
        motif.add_edge("C", "A")

        assert find_motifs(motif, host, count_only=True) == len(
            [i for i in DiGraphMatcher(host, motif).subgraph_monomorphisms_iter()]
        )

    def test_two_hop_count_matches_nx(self):

        host = nx.fast_gnp_random_graph(10, 0.5, directed=True)

        motif = nx.DiGraph()
        motif.add_edge("A", "B")
        motif.add_edge("B", "C")

        assert len(find_motifs(motif, host)) == len(
            [i for i in DiGraphMatcher(host, motif).subgraph_monomorphisms_iter()]
        )

    def test_high_degree_high_density_count_matches_nx(self):

        host = nx.fast_gnp_random_graph(10, 1, directed=True)

        motif = nx.DiGraph()
        motif.add_edge("A", "B")
        motif.add_edge("A", "C")
        motif.add_edge("A", "D")
        motif.add_edge("A", "E")

        assert len(find_motifs(motif, host)) == len(
            [i for i in DiGraphMatcher(host, motif).subgraph_monomorphisms_iter()]
        )

    def test_high_degree_low_density_count_matches_nx(self):

        host = nx.fast_gnp_random_graph(10, 0.3, directed=True)

        motif = nx.DiGraph()
        motif.add_edge("A", "B")
        motif.add_edge("A", "C")
        motif.add_edge("A", "D")
        motif.add_edge("A", "E")

        assert len(find_motifs(motif, host)) == len(
            [i for i in DiGraphMatcher(host, motif).subgraph_monomorphisms_iter()]
        )

    def test_falsy_node_names(self):

        motif = nx.DiGraph()
        motif.add_edge(0, 1)
        motif.add_edge(1, 2)
        motif.add_edge(2, 0)

        host = nx.DiGraph()
        host.add_edge(0, 1)
        host.add_edge(1, 2)
        host.add_edge(2, 0)

        assert len(find_motifs(motif, host)) == 3


class TestUndirectedSubgraphMatching:
    def test_subgraph_equals_graph_triangle(self):

        motif = nx.Graph()
        motif.add_edge("A", "B")
        motif.add_edge("B", "C")
        motif.add_edge("C", "A")

        host = nx.Graph()
        host.add_edge("A", "B")
        host.add_edge("B", "C")
        host.add_edge("C", "A")

        assert len(find_motifs(motif, host)) == 6

    def test_subgraph_equals_graph_rect(self):

        motif = nx.Graph()
        motif.add_edge("A", "B")
        motif.add_edge("B", "C")
        motif.add_edge("C", "D")
        motif.add_edge("D", "A")

        host = nx.Graph()
        host.add_edge("A", "B")
        host.add_edge("B", "C")
        host.add_edge("C", "D")
        host.add_edge("D", "A")

        assert len(find_motifs(motif, host)) == 8

    def test_rect_count_matches_nx(self):

        host = nx.fast_gnp_random_graph(10, 0.5, directed=False)

        motif = nx.Graph()
        motif.add_edge("A", "B")
        motif.add_edge("B", "C")
        motif.add_edge("C", "D")
        motif.add_edge("D", "A")

        assert len(find_motifs(motif, host)) == len(
            [i for i in GraphMatcher(host, motif).subgraph_monomorphisms_iter()]
        )

    def test_tri_count_matches_nx(self):

        host = nx.fast_gnp_random_graph(10, 0.5, directed=False)

        motif = nx.Graph()
        motif.add_edge("A", "B")
        motif.add_edge("B", "C")
        motif.add_edge("C", "A")

        assert len(find_motifs(motif, host)) == len(
            [i for i in GraphMatcher(host, motif).subgraph_monomorphisms_iter()]
        )

    def test_two_hop_count_matches_nx(self):

        host = nx.fast_gnp_random_graph(10, 0.5, directed=False)

        motif = nx.Graph()
        motif.add_edge("A", "B")
        motif.add_edge("B", "C")

        assert len(find_motifs(motif, host)) == len(
            [i for i in GraphMatcher(host, motif).subgraph_monomorphisms_iter()]
        )

    def test_high_degree_high_density_count_matches_nx(self):

        host = nx.fast_gnp_random_graph(10, 1, directed=False)

        motif = nx.Graph()
        motif.add_edge("A", "B")
        motif.add_edge("A", "C")
        motif.add_edge("A", "D")
        motif.add_edge("A", "E")

        assert len(find_motifs(motif, host)) == len(
            [i for i in GraphMatcher(host, motif).subgraph_monomorphisms_iter()]
        )

    def test_high_degree_low_density_count_matches_nx(self):

        host = nx.fast_gnp_random_graph(10, 0.3, directed=False)

        motif = nx.Graph()
        motif.add_edge("A", "B")
        motif.add_edge("A", "C")
        motif.add_edge("A", "D")
        motif.add_edge("A", "E")

        assert len(find_motifs(motif, host)) == len(
            [i for i in GraphMatcher(host, motif).subgraph_monomorphisms_iter()]
        )


def _random_motif():
    g = nx.graph_atlas(random.randint(7, 30))
    while len([c for c in nx.connected_components(g)]) != 1:
        g = nx.graph_atlas(random.randint(7, 30))
    return nx.relabel_nodes(g, lambda x: str(x + 1))


def _random_host(directed=False, n=20, p=0.1):
    g = nx.fast_gnp_random_graph(n, p, directed=directed)
    while (
        len(
            [
                c
                for c in (
                    nx.weakly_connected_components(g)
                    if directed
                    else nx.connected_components(g)
                )
            ]
        )
        != 1
    ):
        g = nx.fast_gnp_random_graph(n, p, directed=directed)
    return nx.relabel_nodes(g, lambda x: str(x + 1))


def _random_directed_motif():
    motif = _random_motif()
    dmotif = nx.DiGraph()
    for (u, v) in motif.edges():
        dmotif.add_edge(*random.choice([(u, v), (v, u)]))
    return dmotif


class TestRandomGraphIsomorphisms:
    @pytest.mark.parametrize(
        "host,motif",
        [(_random_host(directed=False), _random_motif()) for _ in range(5)],
    )
    def test_isomorphisms_on_undirected_random_graph(self, host, motif):
        assert find_motifs(motif, host, isomorphisms_only=True, count_only=True) == len(
            [i for i in GraphMatcher(host, motif).subgraph_isomorphisms_iter()]
        )

    @pytest.mark.parametrize(
        "host,motif",
        [(_random_host(directed=True), _random_directed_motif()) for _ in range(15)],
    )
    def test_isomorphisms_on_directed_random_graph(self, host, motif):
        assert find_motifs(
            motif, host, directed=True, isomorphisms_only=True, count_only=True
        ) == len([i for i in DiGraphMatcher(host, motif).subgraph_isomorphisms_iter()])


class TestRandomGraphMonomorphisms:
    @pytest.mark.parametrize(
        "host,motif",
        [(_random_host(directed=False), _random_motif()) for _ in range(5)],
    )
    def test_monomorphisms_on_undirected_random_graph(self, host, motif):
        assert find_motifs(motif, host, count_only=True) == len(
            [i for i in GraphMatcher(host, motif).subgraph_monomorphisms_iter()]
        )

    @pytest.mark.parametrize(
        "host,motif",
        [(_random_host(directed=True), _random_directed_motif()) for _ in range(15)],
    )
    def test_monomorphisms_on_directed_random_graph(self, host, motif):
        assert find_motifs(motif, host, directed=True, count_only=True) == len(
            [i for i in DiGraphMatcher(host, motif).subgraph_monomorphisms_iter()]
        )


class TestSubcliques:
    def test_subcliques_slow(self):
        host = nx.star_graph(30000)
        host.add_edge(6, 9)

        motif = nx.complete_graph(3)

        assert find_motifs(motif, host, count_only=True) == 6


class TestHints:
    @pytest.mark.parametrize(
        "host,motif",
        [(_random_host(directed=False), _random_motif()) for _ in range(5)],
    )
    def test_empty_hints(self, host, motif):
        assert find_motifs(motif, host, count_only=True, hints=[]) == len(
            [i for i in GraphMatcher(host, motif).subgraph_monomorphisms_iter()]
        )

    def test_broken_hints_have_no_results(self):
        host = nx.DiGraph()
        nx.add_path(host, ["A", "B", "C", "A"])
        motif = nx.DiGraph()
        nx.add_path(motif, ["A", "B", "C", "A"])
        assert (
            find_motifs(motif, host, count_only=True, hints=[{"A": "A", "B": "A"}]) == 0
        )
        assert (
            find_motifs(motif, host, count_only=True, hints=[{"A": "A", "B": "C"}]) == 0
        )

    def test_some_hints_have_values(self):
        # One mapping will fail, the other is valid:
        host = nx.DiGraph()
        nx.add_path(host, ["A", "B", "C", "A"])
        motif = nx.DiGraph()
        nx.add_path(motif, ["A", "B", "C", "A"])
        assert (
            find_motifs(
                motif,
                host,
                count_only=True,
                hints=[{"A": "A", "B": "C"}, {"A": "A", "B": "B"}],
            )
            == 1
        )

    def test_basic_hints(self):
        host = nx.DiGraph()
        nx.add_path(host, ["A", "B", "C", "A"])
        motif = nx.DiGraph()
        nx.add_path(motif, ["a", "b", "c", "a"])
        assert find_motifs(motif, host, count_only=True, hints=[{"a": "A"}]) == 1
        assert (
            find_motifs(motif, host, count_only=True, hints=[{"a": "A"}, {"b": "A"}])
            == 2
        )
