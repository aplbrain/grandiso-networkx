from grandiso import find_motifs
import networkx as nx
host = nx.DiGraph()
host.add_edge("1", "0")
host.add_edge("1","3")
host.add_edge("3","0")
host.add_edge("3","4")
host.add_edge("3","7")
host.add_edge("7","4")
host.add_edge("7","6")
host.add_edge("8","7")
host.add_edge("8","5")
host.add_edge("4","5")
host.add_edge("4","8")
host.add_edge("4","1")
host.add_edge("2","1")
host.add_edge("2","4")
host.add_edge("5","10")
host.add_edge("5","11")
host.add_edge("5","2")
host.add_edge("5","9")
host.add_edge("9","8")


motif = nx.DiGraph()
motif.add_edge("1", "2")
motif.add_edge("3", "1")
motif.add_edge("1", "0")
motif.add_edge("2", "3")
find_motifs(motif, host)












































