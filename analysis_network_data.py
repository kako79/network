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
    if (d.isoweekday() == 6 or d.isoweekday() == 7):
        return True
    else
        return False

def get_month(date):
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
    return d.month

def is_january(month):
    return month == 1


#read in the data from a combined csv file
alldata= pd.read_csv("all_transfers_1110.csv")
#adm_data = alldata['dt_adm']
#adm_data.to_csv('adm_data_only.csv', header=True, index=False)
print('reading in done')

# now develop the network based on the transfer data

#find all the transfer dates on a weekend! not the admission dates
alldata['transfer_dt'] = pd.to_datetime(alldata['transfer_dt'], format="%Y-%m-%d %H:%M")
# add on columns for the true and false for weekend and the month as a number
alldata['is_weekend'] = alldata['transfer_dt'].map(is_weekend)
alldata['transfer_month'] = alldata['transfer_dt'].map(get_month)


#weekend and weekday transfers
weekend_transfers = alldata[alldata['is_weekend']]
weekday_transfers = alldata[~alldata['is_weekend']]




# collect the data for each month
weekday_january_trans = weekday_transfers[weekday_transfers['month'] == 1]
weekday_february_trans = weekday_transfers[weekday_transfers['month'] == 2]
weekday_march_trans = weekday_transfers[weekday_transfers['month'] == 3]
weekday_april_trans = weekday_transfers[weekday_transfers['month'] == 4]
weekday_may_trans = weekday_transfers[weekday_transfers['month'] == 5]
weekday_june_trans = weekday_transfers[weekday_transfers['month'] == 6]
weekday_july_trans = weekday_transfers[weekday_transfers['month'] == 7]
weekday_august_trans = weekday_transfers[weekday_transfers['month'] == 8]
weekday_september_trans = weekday_transfers[weekday_transfers['month'] == 9]
weekday_october_trans = weekday_transfers[weekday_transfers['month'] == 10]
weekday_november_trans = weekday_transfers[weekday_transfers['month'] == 11]
weekday_december_trans = weekday_transfers[weekday_transfers['month'] == 12]

weekend_january_trans = weekend_transfers[weekend_transfers['month'] == 1]
weekend_february_trans = weekend_transfers[weekend_transfers['month'] == 2]
weekend_march_trans = weekend_transfers[weekend_transfers['month'] == 3]
weekend_april_trans = weekend_transfers[weekend_transfers['month'] == 4]
weekend_may_trans = weekend_transfers[weekend_transfers['month'] == 5]
weekend_june_trans = weekend_transfers[weekend_transfers['month'] == 6]
weekend_july_trans = weekend_transfers[weekend_transfers['month'] == 7]
weekend_august_trans = weekend_transfers[weekend_transfers['month'] == 8]
weekend_september_trans = weekend_transfers[weekend_transfers['month'] == 9]
weekend_october_trans = weekend_transfers[weekend_transfers['month'] == 10]
weekend_november_trans = weekend_transfers[weekend_transfers['month'] == 11]
weekend_december_trans = weekend_transfers[weekend_transfers['month'] == 12]

#list_of_weekend_admissions =[get_weekend_list(data) for data in data['admission_time']]


#now make the graph
#specific_data = alldata
#specific_data = weekend_admissions
specific_data = weekday_admissions
#specific_data = pd.read_csv("combined_data.csv")
#specific_data.loc[admpoint[specific_data['admission_time'] == specific_data['extraid']].index, 'to'] = 'discharge'

#weighted edges first
#drop the columns that are not needed for the graph, also select adults or children
data_only_transfers = specific_data.loc[specific_data['age'] < 16].drop(['transfer_dt', 'dt_adm', 'dt_dis', 'spec', 'age', 'asa'], axis=1)

# count the number of times a specific transfer appears to get edge weight
transfer_counts = data_only_transfers.groupby(['from', 'to']).count()
#add the old index as a column - int he above the count became the index.
transfer_counts = transfer_counts.reset_index()
transfer_counts = transfer_counts[transfer_counts['ptid'] > 2]
# Get a list of tuples that contain the values from the rows.
edge_weight_data = transfer_counts[['from', 'to', 'ptid']]
sum_of_all_transfers = edge_weight_data['ptid'].sum()
edge_weight_data['ptid'] = edge_weight_data['ptid']/sum_of_all_transfers
edge_weight_data.to_csv('edge_wdchild1110.csv', header=True, index=False)

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