import numpy as np
import itertools
import functools
#import matplotlib.pyplot as plt
import pandas as pd
#from mpl_toolkits import mplot3d
#from matplotlib import cm
#from matplotlib import colors
import networkx as nx
#from collections import Counter
#from itertools import chain
#from collections import defaultdict
import datetime



def get_data_for_patient (patientid, alldata):
    patient_data = alldata[alldata['ptid'] == patientid]
    patient_data['to'] = patient_data['to'].shift(-1)  # shifting the to column up one so that the value from below is in that slot.
    print(patient_data.iloc[0].name)
    # Make a column that has True if the location changed.
    patient_data['transfer'] = patient_data['from'] != patient_data['to']
    print(patientid)


    patient_data.fillna('discharge', inplace = True)
    #drop the columns where the to and from is the same
    patient_data.drop(patient_data[patient_data['to'] == patient_data['from']].index, axis=0, inplace=True)
    return patient_data
#read in the data from a combined csv file
data= pd.read_csv("combined_data.csv")
print('reading in done')

# now develop the network based on the transfer data

#weighted edges first
data_only_transfers = data.loc[combined_patient_data['admAge'] > 20].drop(['depname','evttype','effective_time', 'specialty', 'admAge', 'asa_rating_c', 'transfer', 'transfer_time', 'admission_time', 'discharge time'], axis=1)
transfer_counts = data_only_transfers.groupby(['from', 'to']).count().reset_index()
#transfer_counts = transfer_counts[transfer_counts['ptid'] > 1]
# Get a list of tuples that contain the values from the rows.
weighted_edges = list(itertools.starmap(lambda f, t, w: (f, t, int(w)), transfer_counts.itertuples(index=False, name=None)))

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
#flow_hierarchy = nx.algorithms.hierarchy.flow_hierarchy(G)
#print(flow_hierarchy)