<h1 align=center>Grand Isomorphisms</h1>

<p align="center">
<a href="https://codecov.io/gh/aplbrain/grandiso-networkx/"><img alt="Codecov" src="https://img.shields.io/codecov/c/github/aplbrain/grandiso-networkx?style=for-the-badge"></a>
<a href="https://github.com/aplbrain/grandiso-networkx/actions"><img alt="GitHub Workflow Status" src="https://img.shields.io/github/workflow/status/aplbrain/grandiso-networkx/Python%20package?style=for-the-badge"></a>
<a href="https://bossdb.org/tools/DotMotif"><img src="https://img.shields.io/badge/Pretty Dope-👌-00ddcc.svg?style=for-the-badge" /></a>
<img alt="GitHub" src="https://img.shields.io/github/license/aplbrain/grandiso-networkx?style=for-the-badge">
</p>

Subgraph isomorphism is a resource-heavy (but branch-parallelizable) algorithm that is hugely impactful for large graph analysis. SotA algorithms for this (Ullmann, VF2, BB-Graph) are heavily RAM-bound, but this is due to a large number of small processes each of which hold a small portion of a traversal tree in memory.

_Grand-Iso_ is a subgraph isomorphism algorithm that exchanges this resource-limitation for a parallelizable partial-match queue structure.

It performs favorably compared to other pure-python (and even some non-pure-python!) implementations:

<img width="485" alt="image" src="https://user-images.githubusercontent.com/693511/96184546-a35e0380-0f06-11eb-8475-1921e8f94256.png">


## Example Usage

```python
from grandiso import find_motifs
import networkx as nx

host = nx.fast_gnp_random_graph(10, 0.5)

motif = nx.Graph()
motif.add_edge("A", "B")
motif.add_edge("B", "C")
motif.add_edge("C", "D")
motif.add_edge("D", "A")

len(find_motifs(motif, host))
```

Directed graph support:

```python
from grandiso import find_motifs
import networkx as nx

host = nx.fast_gnp_random_graph(10, 0.5, directed=True)

motif = nx.DiGraph()
motif.add_edge("A", "B")
motif.add_edge("B", "C")
motif.add_edge("C", "D")
motif.add_edge("D", "A")

len(find_motifs(motif, host))
```

## Counts-only

For very large graphs, you may use a good chunk of RAM not only on the queue of hypotheses, but also on the list of results. If all you care about is the NUMBER of results, you should pass `count_only=True` to the `find_motifs` function. This will dramatically reduce your RAM overhead on higher-count queries.

## Pseudocode for "Grand-Iso" algorithm

```
- Accept a motif M, and a host graph H.
- Create an empty list for result storage, R.
- Create an empty queue, Q.
- Preprocessing
    - Identify the most "interesting" node in motif M, m1.
    - Add to Q a set of mappings with a single node, with one map for all
        nodes in H that satisfy the requirements of m1: degree, attributes, etc
- Motif Search
    - "Pop" a backbone B from Q
        - Identify as m1 the most interesting node in motif M that does not yet
            have a mapping assigned in B.
        - Identify all nodes that are valid mappings from the backbone to m1,
            based upon degree, attributes, etc.
        - If multiple nodes are valid candidates, add each new backbone to Q.
        - Otherwise, when all nodes in M have a valid mapping in B to H, add
            the mapping to the results set R.
    - Continue while there are still backbones in Q.
- Reporting
    - Return the set R to the user.
```

## Hacking on this repo

### Running Tests

```shell
coverage run --source=grandiso -m pytest
```


## Citing

If this tool is helpful to your research, please consider citing it with:

```
# https://www.biorxiv.org/content/10.1101/2020.06.08.140533v1
@article{matelsky_2020_dotmotif,
    doi = {10.1101/2020.06.08.140533},
    url = {https://www.biorxiv.org/content/10.1101/2020.06.08.140533v1},
    year = 2020,
    month = {june},
    publisher = {BiorXiv},
    author = {Matelsky, Jordan K. and Reilly, Elizabeth P. and Johnson,Erik C. and Wester, Brock A. and Gray-Roncal, William},
    title = {{Connectome subgraph isomorphisms and graph queries with DotMotif}},
    journal = {BiorXiv}
}
```
