# CHANGELOG

## [v2.1.0 (December 16 2021)](https://pypi.org/project/grandiso/2.1.0/)

-   Features
    -   (#23) Adds edge-attribute matching alongside node-attribute matching (thanks @MelomanCool!), along with tests for attribute-matching (#24)
    -   (#25) Pass edge-attribute matching functions along through all methods to enable user-defined edge-attribute matching
    -   (#27) Improves usage of the `interestingness` metric for sorting nodes in candidate-finding routing (thanks @aleclearmind!)
-   Housekeeping
    -   (#26) Added a codecov config file to ignore setup.py from test suite

## [v2.0.1 (Sep 20 2021)](https://pypi.org/project/grandiso/2.0.1/)

-   Fixes
    -   Fixes an installation error where older versions of python misread the long description of the package
    -   Fixes a namespace resolution error in `queues`

## [v2.0.0 (May 28 2021)](https://pypi.org/project/grandiso/2.0.0/)

-   Features
    -   Memoize node match function calls, and enable the user to pass custom node match functions. This greatly improves worst-case performance by removing excess calls to the note match functions, at the cost of additional memory.
-   Housekeeping
    -   Remove the `profile` argument and profiling flow. (For profiling needs, you can now pass a profiling queue from the `queues` submodule.)

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
