<h1 align=center>Grand Isomorphisms</h1>

<p align="center">
<a href="https://codecov.io/gh/aplbrain/grandiso-networkx/"><img alt="Codecov" src="https://img.shields.io/codecov/c/github/aplbrain/grandiso-networkx?style=for-the-badge"></a>
<a href="https://github.com/aplbrain/grandiso-networkx/actions"><img alt="GitHub Workflow Status" src="https://img.shields.io/github/workflow/status/aplbrain/grandiso-networkx/Python%20package?style=for-the-badge"></a>
<a href="https://bossdb.org/tools/DotMotif"><img src="https://img.shields.io/badge/Pretty Dope-👌-00ddcc.svg?style=for-the-badge" /></a>
<img alt="GitHub" src="https://img.shields.io/github/license/aplbrain/grandiso-networkx?style=for-the-badge">
<a href="https://pypi.org/project/grandiso/"><img alt="PyPI" src="https://img.shields.io/pypi/v/grandiso?style=for-the-badge"></a>
</p>

Subgraph isomorphism is a resource-heavy (but branch-parallelizable) algorithm that is hugely impactful for large graph analysis. SotA algorithms for this (Ullmann, VF2, BB-Graph) are heavily RAM-bound, but this is due to a large number of small processes each of which hold a small portion of a traversal tree in memory.

_Grand-Iso_ is a subgraph isomorphism algorithm that exchanges this resource-limitation for a parallelizable partial-match queue structure.

It performs favorably compared to other pure-python (and even some non-pure-python!) implementations:

<img width="485" alt="image" src="https://user-images.githubusercontent.com/693511/96184546-a35e0380-0f06-11eb-8475-1921e8f94256.png">

See the [wiki](https://github.com/aplbrain/grandiso-networkx/wiki) for more documentation.

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

There are many other arguments that you can pass to the motif search algorithm. For a full list, see [here](https://github.com/aplbrain/grandiso-networkx/wiki/Algorithm-Arguments).


## Hacking on this repo

### Running Tests

```shell
coverage run --source=grandiso -m pytest
```

## Citing

If this tool is helpful to your research, please consider citing it with:

```bibtex
# https://doi.org/10.1038/s41598-021-91025-5
@article{Matelsky_Motifs_2021, 
    title={{DotMotif: an open-source tool for connectome subgraph isomorphism search and graph queries}},
    volume={11}, 
    ISSN={2045-2322}, 
    url={http://dx.doi.org/10.1038/s41598-021-91025-5}, 
    DOI={10.1038/s41598-021-91025-5}, 
    number={1}, 
    journal={Scientific Reports}, 
    publisher={Springer Science and Business Media LLC}, 
    author={Matelsky, Jordan K. and Reilly, Elizabeth P. and Johnson, Erik C. and Stiso, Jennifer and Bassett, Danielle S. and Wester, Brock A. and Gray-Roncal, William},
    year={2021}, 
    month={Jun}
}
```

---

<p align=center><b>Made with 💙 at <a href="https://jhuapl.edu"><img alt="JHU APL" src="https://user-images.githubusercontent.com/693511/116814564-9b268800-ab27-11eb-98bb-dfddb2e405a1.png" height="23px" /></a></b></p>
