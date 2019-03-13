import networkx as nx
import matplotlib.pyplot as plt

pos = {0: (40, 20), 1: (20, 30), 2: (40, 30), 3: (30, 10)}

X=nx.Graph()
nx.draw_networkx_nodes(X,pos,node_size=300,nodelist=[0,1,2,3],node_color='r')

#pos = {'A': (1,1), 'B': (2,2), 'C': (3,3)}
#nx.set_node_attributes(H,pos)

plt.show()
