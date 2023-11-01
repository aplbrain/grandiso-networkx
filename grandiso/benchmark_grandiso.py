import networkx as nx
from . import find_motifs


def test_benchmark_complete_graph_triangles(benchmark):
    """Find all triangles in a complete graph of 25 nodes."""
    benchmark(find_motifs, nx.complete_graph(3), nx.complete_graph(25), count_only=True)


def test_benchmark_complete_graph_4cliques(benchmark):
    """Find all 4-cliques in a complete graph of 10 nodes."""
    benchmark(find_motifs, nx.complete_graph(4), nx.complete_graph(10), count_only=True)


def test_benchmark_karate_karate(benchmark):
    """Find the correct isomorphism between the karate club graph and itself."""
    benchmark(
        find_motifs, nx.karate_club_graph(), nx.karate_club_graph(), count_only=True
    )


def test_benchmark_weight_attributes(benchmark):
    """Finds all triangles in the Les Miserables graph with weighted edges."""
    motif = nx.complete_graph(3)
    motif.add_edge(0, 1, weight=4)
    motif.add_edge(1, 2, weight=4)
    motif.add_edge(0, 2, weight=4)
    benchmark(
        find_motifs,
        motif,
        nx.les_miserables_graph(),
        count_only=True,
    )
