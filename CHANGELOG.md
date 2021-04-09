# CHANGELOG

## v1.2.0 (Unreleased)

- Features
    -   Adds a `queues` submodule to enable customized queue construction behavior (breadth-first or depth-first traversal).


## [v1.1.0 (February 26 2021)](https://pypi.org/project/grandiso/1.1.0/)

-   Features
    -   `limit` argument: Pass an integer limit of results to return in order to short-circuit and return early from long-running jobs. See [here](https://github.com/aplbrain/grandiso-networkx/wiki/Algorithm-Arguments) for more information.

## [v1.0.0 (January 11 2021)](https://pypi.org/project/grandiso/1.0.0/)

> This version adds map hinting in order to let a user specify partial matches in the `find_motifs` call.

-   Features
    -   `hints` argument: Pass a list of partial starting maps in order to condition the search results. See [this wiki page](https://github.com/aplbrain/grandiso-networkx/wiki/Using-Hints) for more details.

## v0.1.0

> This original release adds support for `find_motifs` and motif-counting with the `count_only=True` argument.
