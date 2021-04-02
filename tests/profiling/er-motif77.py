from grandiso import find_motifs
from grandiso.queues import Deque
import networkx as nx
import time
import numpy as np
from tqdm.auto import tqdm

TRIALS = 1
N = 100
p = 0.3

# motif = nx.complete_graph(4)
motif = nx.Graph()
motif.add_edge("A", "B")
motif.add_edge("B", "C")
motif.add_edge("C", "D")

# default_times = []
# for i in tqdm(range(TRIALS)):
#     tic = time.time()
#     host = nx.fast_gnp_random_graph(N, p)
#     find_motifs(motif, host)
#     default_times.append(time.time() - tic)

# print(np.mean(default_times), default_times)

dfs_times = []
for i in tqdm(range(TRIALS)):
    tic = time.time()
    host = nx.fast_gnp_random_graph(N, p)
    find_motifs(motif, host, queue_=Deque)
    dfs_times.append(time.time() - tic)

print(np.mean(dfs_times), dfs_times)


"""

k4:
400052224
314437632
341626880
410984448
404492288
389517312
378990592

paths:
812449792
727121920
768499712
764166144
743747584

---

dq:

k4:
384868352
375828480
360460288
347901952
368664576
383623168

paths:
752033792
695926784
802398208
772034560
866852864
"""
