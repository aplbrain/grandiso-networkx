# CHANGELOG

## v1.2.1 (Unreleased)

-   Features
    -   Memoize node match function calls, and enable the user to pass custom node match functions. This greatly improves worst-case performance by removing excess calls to the note match functions, at the cost of additional memory.

## [v1.2.0 (May 4 2021)](https://pypi.org/project/grandiso/1.2.0/)

-   Features
    -   Adds a `queues` submodule to enable customized queue construction behavior (breadth-first or depth-first traversal).
    -   Adds a new `find_motifs_iter` function call which returns a generator. You can now sip results from this iterable without waiting for the full search to complete. Thanks to @Raphtor!

## [v1.1.0 (February 26 2021)](https://pypi.org/project/grandiso/1.1.0/)

-   Features
    -   `limit` argument: Pass an integer limit of results to return in order to short-circuit and return early from long-running jobs. See [here](https://github.com/aplbrain/grandiso-networkx/wiki/Algorithm-Arguments) for more information.

## [v1.0.0 (January 11 2021)](https://pypi.org/project/grandiso/1.0.0/)

> This version adds map hinting in order to let a user specify partial matches in the `find_motifs` call.

-   Features
    -   `hints` argument: Pass a list of partial starting maps in order to condition the search results. See [this wiki page](https://github.com/aplbrain/grandiso-networkx/wiki/Using-Hints) for more details.

## v0.1.0

> This original release adds support for `find_motifs` and motif-counting with the `count_only=True` argument.
