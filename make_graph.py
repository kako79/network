import numpy as np
import itertools
import functools

import matplotlib
matplotlib.use('agg')
import matplotlib.pyplot as plt

import pandas as pd
#from mpl_toolkits import mplot3d
#from matplotlib import cm
#from matplotlib import colors
import networkx as nx
#from collections import Counter
#from itertools import chain
#from collections import defaultdict
import datetime


#read in the data from a combined csv file
data= pd.read_csv("combined_data.csv")
print('reading in done')

# now develop the network based on the transfer data

#weighted edges first
data_only_transfers = data.loc[data['admAge'] > 18].drop(['depname','evttype', 'effective_time', 'specialty', 'admAge', 'asa_rating_c', 'transfer', 'transfer_time', 'admission_time', 'discharge_time'], axis=1)
transfer_counts = data_only_transfers.groupby(['from', 'to']).count()
transfer_counts = transfer_counts.reset_index()
#transfer_counts = transfer_counts[transfer_counts['ptid'] > 1]
# Get a list of tuples that contain the values from the rows.
edge_weight_data = transfer_counts[['from', 'to', 'ptid']]
weighted_edges = list(itertools.starmap(lambda f, t, w: (f, t, int(w)), edge_weight_data.itertuples(index=False, name=None)))

G = nx.DiGraph()
print(weighted_edges)
G.add_weighted_edges_from(weighted_edges)
en=G.number_of_edges()
nn=G.number_of_nodes()
print(en)
print(nn)

#undirected graph of the same data
nondiG = nx.Graph()
nondiG.add_weighted_edges_from(weighted_edges)


#calculate the degree
degrees = nx.classes.function.degree(G)
print('degrees')
print(degrees)
histdegrees = nx.classes.function.degree_histogram(G)
print('histdegrees')
print(histdegrees)

# calculate the centrality of each node - fraction of nodes the incoming/outgoing edges are connected to
incentrality = nx.algorithms.centrality.in_degree_centrality(G)
outcentrality = nx.algorithms.centrality.out_degree_centrality(G)
print('in and out centrality')
print(incentrality)
print(outcentrality)


#centrality_overall = defaultdict(list)
#for k,v in chain(incentrality.items(), outcentrality.items()):
#    centrality_overall[k].append(v)

#print(centrality_overall)
#dfcentrality = pd.DataFrame.from_dict(centrality_overall,orient='index')
#print(dfcentrality)

#clustering - doesnt work for directed graphs
clustering_average = nx.algorithms.cluster.clustering(nondiG)
print('clustering in non directed graph')
print(clustering_average)

#shortest path in the directed graph, from a starting point source to a point target
#shortest_path = nx.algorithms.shortest_paths.generic.shortest_path(G, source = 'ICU', target = 'ER')
#print('shortest path is')
#print(shortest_path)

#flow hiearchy - finds strongly connected components
flow_hierarchy = nx.algorithms.hierarchy.flow_hierarchy(G)
print('flow hierarchy')
print(flow_hierarchy)

fig = plt.figure(figsize=(7, 5))
#nx.set_node_attributes(G,'length_of_stay',los)
#pos = nx.circular_layout(G)
#widthedge = [d['weight'] *0.1 for _,_,d in G.edges(data=True)]
#nx.draw_networkx(G, pos=pos, with_labels=True, font_weight='bold', arrows = False, width= widthedge,  node_size=1300)
nx.draw_networkx(G)
#width = [d['weight'] for _,_,d in G.edges(data=True)]

#edge_labels=dict([((u,v,), d['weight'])
#             for u,v,d in G.edges(data=True)])
#nx.draw_networkx(G, with_labels=True, font_weight='bold' )
#nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels)
#plt.show()
fig.savefig("allnetworkgraph.png")
plt.gcf().clear()