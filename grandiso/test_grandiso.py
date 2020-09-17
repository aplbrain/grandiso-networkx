import time
import copy
import unittest

import networkx as nx
from networkx.algorithms.isomorphism import DiGraphMatcher, GraphMatcher

from . import find_motifs


class TestSubgraphMatching(unittest.TestCase):
    def test_finds_no_triangles_in_zero_tri_graph(self):

        motif = nx.DiGraph()
        motif.add_edge("A", "B")
        motif.add_edge("B", "C")
        motif.add_edge("C", "A")

        host = nx.DiGraph()
        host.add_edge("A", "B")
        host.add_edge("B", "C")

        self.assertEqual(len(find_motifs(motif, host)), 0)

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

        self.assertEqual(len(find_motifs(motif, host)), 0)

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

        self.assertEqual(len(find_motifs(motif, host)), 0)

    def test_finds_no_motifs_in_small_graph(self):

        motif = nx.DiGraph()
        motif.add_edge("A", "B")
        motif.add_edge("B", "C")

        host = nx.DiGraph()
        host.add_edge("A", "B")

        self.assertEqual(len(find_motifs(motif, host)), 0)

    def test_subgraph_equals_graph_triangle(self):

        motif = nx.DiGraph()
        motif.add_edge("A", "B")
        motif.add_edge("B", "C")
        motif.add_edge("C", "A")

        host = nx.DiGraph()
        host.add_edge("A", "B")
        host.add_edge("B", "C")
        host.add_edge("C", "A")

        self.assertEqual(len(find_motifs(motif, host)), 3)

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

        self.assertEqual(len(find_motifs(motif, host)), 4)

    def test_rect_count_matches_nx(self):

        host = nx.fast_gnp_random_graph(10, 0.5, directed=True)

        motif = nx.DiGraph()
        motif.add_edge("A", "B")
        motif.add_edge("B", "C")
        motif.add_edge("C", "D")
        motif.add_edge("D", "A")

        self.assertEqual(
            len(find_motifs(motif, host)),
            len([i for i in DiGraphMatcher(host, motif).subgraph_monomorphisms_iter()]),
        )

    def test_tri_count_matches_nx(self):

        host = nx.fast_gnp_random_graph(10, 0.5, directed=True)

        motif = nx.DiGraph()
        motif.add_edge("A", "B")
        motif.add_edge("B", "C")
        motif.add_edge("C", "A")

        self.assertEqual(
            len(find_motifs(motif, host)),
            len([i for i in DiGraphMatcher(host, motif).subgraph_monomorphisms_iter()]),
        )

    def test_two_hop_count_matches_nx(self):

        host = nx.fast_gnp_random_graph(10, 0.5, directed=True)

        motif = nx.DiGraph()
        motif.add_edge("A", "B")
        motif.add_edge("B", "C")

        self.assertEqual(
            len(find_motifs(motif, host)),
            len([i for i in DiGraphMatcher(host, motif).subgraph_monomorphisms_iter()]),
        )

    def test_high_degree_high_density_count_matches_nx(self):

        host = nx.fast_gnp_random_graph(10, 1, directed=True)

        motif = nx.DiGraph()
        motif.add_edge("A", "B")
        motif.add_edge("A", "C")
        motif.add_edge("A", "D")
        motif.add_edge("A", "E")

        self.assertEqual(
            len(find_motifs(motif, host)),
            len([i for i in DiGraphMatcher(host, motif).subgraph_monomorphisms_iter()]),
        )

    def test_high_degree_low_density_count_matches_nx(self):

        host = nx.fast_gnp_random_graph(10, 0.3, directed=True)

        motif = nx.DiGraph()
        motif.add_edge("A", "B")
        motif.add_edge("A", "C")
        motif.add_edge("A", "D")
        motif.add_edge("A", "E")

        self.assertEqual(
            len(find_motifs(motif, host)),
            len([i for i in DiGraphMatcher(host, motif).subgraph_monomorphisms_iter()]),
        )


class TestUndirectedSubgraphMatching(unittest.TestCase):
    def test_subgraph_equals_graph_triangle(self):

        motif = nx.Graph()
        motif.add_edge("A", "B")
        motif.add_edge("B", "C")
        motif.add_edge("C", "A")

        host = nx.Graph()
        host.add_edge("A", "B")
        host.add_edge("B", "C")
        host.add_edge("C", "A")

        self.assertEqual(len(find_motifs(motif, host)), 6)

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

        self.assertEqual(len(find_motifs(motif, host)), 8)

    def test_rect_count_matches_nx(self):

        host = nx.fast_gnp_random_graph(10, 0.5, directed=False)

        motif = nx.Graph()
        motif.add_edge("A", "B")
        motif.add_edge("B", "C")
        motif.add_edge("C", "D")
        motif.add_edge("D", "A")

        self.assertEqual(
            len(find_motifs(motif, host)),
            len([i for i in GraphMatcher(host, motif).subgraph_monomorphisms_iter()]),
        )

    def test_tri_count_matches_nx(self):

        host = nx.fast_gnp_random_graph(10, 0.5, directed=False)

        motif = nx.Graph()
        motif.add_edge("A", "B")
        motif.add_edge("B", "C")
        motif.add_edge("C", "A")

        self.assertEqual(
            len(find_motifs(motif, host)),
            len([i for i in GraphMatcher(host, motif).subgraph_monomorphisms_iter()]),
        )

    def test_two_hop_count_matches_nx(self):

        host = nx.fast_gnp_random_graph(10, 0.5, directed=False)

        motif = nx.Graph()
        motif.add_edge("A", "B")
        motif.add_edge("B", "C")

        self.assertEqual(
            len(find_motifs(motif, host)),
            len([i for i in GraphMatcher(host, motif).subgraph_monomorphisms_iter()]),
        )

    def test_high_degree_high_density_count_matches_nx(self):

        host = nx.fast_gnp_random_graph(10, 1, directed=False)

        motif = nx.Graph()
        motif.add_edge("A", "B")
        motif.add_edge("A", "C")
        motif.add_edge("A", "D")
        motif.add_edge("A", "E")

        self.assertEqual(
            len(find_motifs(motif, host)),
            len([i for i in GraphMatcher(host, motif).subgraph_monomorphisms_iter()]),
        )

    def test_high_degree_low_density_count_matches_nx(self):

        host = nx.fast_gnp_random_graph(10, 0.3, directed=False)

        motif = nx.Graph()
        motif.add_edge("A", "B")
        motif.add_edge("A", "C")
        motif.add_edge("A", "D")
        motif.add_edge("A", "E")

        self.assertEqual(
            len(find_motifs(motif, host)),
            len([i for i in GraphMatcher(host, motif).subgraph_monomorphisms_iter()]),
        )

