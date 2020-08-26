import time
import copy
import unittest

import networkx as nx
from networkx.algorithms.isomorphism import DiGraphMatcher, GraphMatcher

from . import find_motifs, find_motifs_parallel


class TestSubgraphMatching(unittest.TestCase):
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


class TestParallel(unittest.TestCase):
    def test_parallel(self):

        motif = nx.Graph()
        motif.add_edge("A", "B")
        motif.add_edge("B", "C")
        motif.add_edge("C", "A")

        host = nx.Graph()
        host.add_edge("A", "B")
        host.add_edge("B", "C")
        host.add_edge("C", "A")

        self.assertEqual(len(find_motifs_parallel(motif, host)), 6)

    def test_parallel_big_graph(self):

        motif = nx.Graph()
        motif.add_edge("A", "B")
        motif.add_edge("B", "C")
        motif.add_edge("C", "A")
        motif.add_edge("C", "D")
        motif.add_edge("D", "A")

        host = nx.fast_gnp_random_graph(200, 0.02, directed=False)

        tic = time.time()
        result_count_singlethread = len(find_motifs(motif, host))
        toc_singlethread = time.time() - tic
        tic = time.time()
        result_count_parallel = len(find_motifs_parallel(motif, host))
        toc_parallel = time.time() - tic
        self.assertEqual(result_count_singlethread, result_count_parallel)
        self.assertGreater(toc_singlethread, toc_parallel)


# class TestParallelFile(unittest.TestCase):
#     def test_parallel(self):
#         motif = nx.Graph()
#         motif.add_edge("A", "B")
#         motif.add_edge("B", "C")
#         motif.add_edge("C", "A")
#         motif.add_edge("C", "D")
#         motif.add_edge("D", "A")

#         host = nx.fast_gnp_random_graph(40, 0.05, directed=False)

#         tic = time.time()
#         result_count_singlethread = len(find_motifs(motif, host))
#         toc_singlethread = time.time() - tic
#         tic = time.time()
#         result_count_parallel = len(
#             find_motifs_parallel(motif, host, queue_on_disk=True)
#         )
#         toc_parallel = time.time() - tic
#         self.assertEqual(result_count_singlethread, result_count_parallel)
#         # self.assertGreater(toc_singlethread, toc_parallel)
