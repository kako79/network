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
from datetime import datetime

#def get_weekend_list(alldata):
#    #weekend_admissions = alldata[alldata['admission_time'].get_weekday() == True]
#    weekend_admissions = alldata[alldata['admission_time'].weekday() == '5' or alldata['admission_time'].weekday() == '6']
#    #weekend_admissions = alldata.loc[alldata['admission_time'].get_weekday() == 'Saturday' ]
#    return weekend_admissions

def is_weekend(date):
    #print(date)
    strdate = str(date)
    fmt = "%Y-%m-%d %H:%M"
    try:
        d = datetime.strptime(strdate, fmt)
    except ValueError as v:
            ulr = len(v.args[0].partition('unconverted data remains: ')[2])
            if ulr:
                d = datetime.strptime(strdate[:-ulr], fmt)
            else:
                raise v
    #d = datetime.strptime(date, '%Y-%m-%d %H:%M:%S')
    #print(d)
    return d.isoweekday() % 7 < 2


#read in the data from a combined csv file
alldata= pd.read_csv("transfers_categories.csv")
#adm_data = alldata['dt_adm']
#adm_data.to_csv('adm_data_only.csv', header=True, index=False)


print('reading in done')

# now develop the network based on the transfer data

#find all the admission dates on a weekend
alldata['dt_adm'] = pd.to_datetime(alldata['dt_adm'], format="%Y-%m-%d %H:%M")
alldata['is_weekend'] = alldata['dt_adm'].map(is_weekend)
weekend_admissions = alldata[alldata['is_weekend']]
weekday_admissions = alldata[~alldata['is_weekend']]
#list_of_weekend_admissions =[get_weekend_list(data) for data in data['admission_time']]


#now make the graph
#specific_data = alldata
#specific_data = weekend_admissions
specific_data = weekday_admissions
#specific_data = pd.read_csv("combined_data.csv")
#specific_data.loc[admpoint[specific_data['admission_time'] == specific_data['extraid']].index, 'to'] = 'discharge'

#weighted edges first
#drop the columns that are not needed for the graph, also only adults
data_only_transfers = specific_data.loc[specific_data['age'] < 16].drop(['from_loc','to_loc','transfer_dt', 'dt_adm', 'dt_dis', 'spec', 'age', 'asa'], axis=1)

# count the number of times a specific transfer appears to get edge weight
transfer_counts = data_only_transfers.groupby(['from_category', 'to_category']).count()
#add the old index as a column - int he above the count became the index.
transfer_counts = transfer_counts.reset_index()
transfer_counts = transfer_counts[transfer_counts['ptid'] > 2]
# Get a list of tuples that contain the values from the rows.
edge_weight_data = transfer_counts[['from_category', 'to_category', 'ptid']]
sum_of_all_transfers = edge_weight_data['ptid'].sum()
edge_weight_data['ptid'] = edge_weight_data['ptid']/sum_of_all_transfers
edge_weight_data.to_csv('edge_wdchildcat1110.csv', header=True, index=False)

weighted_edges = list(itertools.starmap(lambda f, t, w: (f, t, int(w)), edge_weight_data.itertuples(index=False, name=None)))

G = nx.DiGraph()
#print(weighted_edges)
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
nx.draw_circular(G)
#width = [d['weight'] for _,_,d in G.edges(data=True)]

#edge_labels=dict([((u,v,), d['weight'])
#             for u,v,d in G.edges(data=True)])
#nx.draw_networkx(G, with_labels=True, font_weight='bold' )
#nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels)
#plt.show()
fig.savefig("weekendchildrennetworkgraph.png")
plt.gcf().clear()
