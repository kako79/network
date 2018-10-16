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
    else:
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

def get_network_analytics(month_data_reduced):
    # weighted edges first
    # count the number of times a specific transfer appears to get edge weight
    transfer_counts = month_data_reduced.groupby(['from', 'to']).count()

    # add the old index as a column - int he above the count became the index.
    transfer_counts = transfer_counts.reset_index()
    transfer_counts = transfer_counts[transfer_counts['ptid'] > 1]
    # Get a list of tuples that contain the values from the rows.
    edge_weight_data = transfer_counts[['from', 'to', 'ptid']]
    sum_of_all_transfers = edge_weight_data['ptid'].sum()
    edge_weight_data['ptid'] = edge_weight_data['ptid'] / sum_of_all_transfers
    if it_is_weekend == False:
        edge_weight_data.to_csv('edge_wdadult%s.csv' % str(i), header=True, index=False)
    else:
        edge_weight_data.to_csv('edge_weadult%s.csv' % str(i), header=True, index=False)

    weighted_edges = list(
        itertools.starmap(lambda f, t, w: (f, t, int(w)), edge_weight_data.itertuples(index=False, name=None)))

    G = nx.DiGraph()
    # print(weighted_edges)
    G.add_weighted_edges_from(weighted_edges)
    en = G.number_of_edges()
    nn = G.number_of_nodes()
    print(en)
    print(nn)
    en_list.append(en)
    nn_list.append(nn)

    # calculate the degree
    degrees = nx.classes.function.degree(G)
    degrees_list = [[n, d] for n, d in degrees]
    degrees_data = pd.DataFrame(degrees_list, columns=['node', 'degree'])
    degrees_data.to_csv('degrees_weadult%s.csv'%str(i), header =True, index=False)
    #look at degrees of the emergency department, need to change it to a dictionary to be able to look up the degree value for this node
    degrees_data.set_index('node', inplace=True)
    degrees_dict = degrees_data.to_dict()['degree']
    emergency_degrees = degrees_dict['ADD EMERGENCY DEPT']


    #degrees_list.append(list(degrees.values))
    #degrees_list.to_csv('degrees%s.csv' % str(i), header=True, index=False)
    #print('degrees')
    #print(degrees)

    # histdegrees = nx.classes.function.degree_histogram(G)
    # print('histdegrees')
    # print(histdegrees)

    # calculate the centrality of each node - fraction of nodes the incoming/outgoing edges are connected to
    incentrality = nx.algorithms.centrality.in_degree_centrality(G)
    outcentrality = nx.algorithms.centrality.out_degree_centrality(G)
    print (incentrality)
    in_theatre_centrality = incentrality['theatres']
    print(in_theatre_centrality)
    out_theatre_centrality = outcentrality['theatres']



    # flow hiearchy - finds strongly connected components
    flow_hierarchy = nx.algorithms.hierarchy.flow_hierarchy(G)
    #print('flow hierarchy')
    #print(flow_hierarchy)
    flow_h_list.append(flow_hierarchy)

    data_list.append({'month':i,'number of transfers': len(month_data_reduced['transfer_month']),'number nodes': nn,'number edges': en,'flow hierarchy': flow_hierarchy, 'emergency degrees': emergency_degrees, 'incentrality theatres': in_theatre_centrality, 'outcentrality theatres': out_theatre_centrality})
    return data_list
    # clustering - doesnt work for directed graphs
    #clustering_average = nx.algorithms.cluster.clustering(nondiG)
    #print('clustering in non directed graph')
    #print(clustering_average)





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


alldata['to'].replace(to_replace=['ADD MAIN THEATRE', 'ADD MAIN THEATRE 01','ADD MAIN THEATRE 02', 'ADD MAIN THEATRE 03', 'ADD MAIN THEATRE 04' , 'ADD MAIN THEATRE 05', 'ADD MAIN THEATRE 06', 'ADD MAIN THEATRE 07','ADD MAIN THEATRE 08', 'ADD MAIN THEATRE 09', 'ADD MAIN THEATRE 10' ,'ADD MAIN THEATRE 11', 'ADD MAIN THEATRE 12', 'ADD MAIN THEATRE 14','ADD MAIN THEATRE 15', 'ADD MAIN THEATRE 16','ADD MAIN THEATRE 17', 'ADD MAIN THEATRE 18','ADD MAIN THEATRE 19', 'ADD MAIN THEATRE 20','ADD MAIN THEATRE 21', 'ADD MAIN THEATRE 22','ADD ATC THEATRE 31', 'ADD ATC THEATRE 32','ADD ATC THEATRE 33', 'ADD ATC THEATRE 34','ADD ATC THEATRE 35', 'ADD ATC THEATRE 36'],value='theatre',inplace=True)
alldata['from'].replace(to_replace=['ADD MAIN THEATRE', 'ADD MAIN THEATRE 01','ADD MAIN THEATRE 02', 'ADD MAIN THEATRE 03', 'ADD MAIN THEATRE 04' , 'ADD MAIN THEATRE 05', 'ADD MAIN THEATRE 06', 'ADD MAIN THEATRE 07','ADD MAIN THEATRE 08', 'ADD MAIN THEATRE 09', 'ADD MAIN THEATRE 10' ,'ADD MAIN THEATRE 11', 'ADD MAIN THEATRE 12', 'ADD MAIN THEATRE 14','ADD MAIN THEATRE 15', 'ADD MAIN THEATRE 16','ADD MAIN THEATRE 17', 'ADD MAIN THEATRE 18','ADD MAIN THEATRE 19', 'ADD MAIN THEATRE 20','ADD MAIN THEATRE 21', 'ADD MAIN THEATRE 22','ADD ATC THEATRE 31', 'ADD ATC THEATRE 32','ADD ATC THEATRE 33', 'ADD ATC THEATRE 34','ADD ATC THEATRE 35', 'ADD ATC THEATRE 36'],value='theatre',inplace=True)

#theatre_dictionary = {'ADD MAIN THEATRE': 'theatre', 'ADD MAIN THEATRE 01': 'theatre',
#                       'ADD MAIN THEATRE 02': 'theatre', 'ADD MAIN THEATRE 03': 'theatre',
#                       'ADD MAIN THEATRE 04': 'theatre', 'ADD MAIN THEATRE 05': 'theatre',
#                       'ADD MAIN THEATRE 06': 'theatre', 'ADD MAIN THEATRE 07': 'theatre',
#                       'ADD MAIN THEATRE 08': 'theatre', 'ADD MAIN THEATRE 09': 'theatre',
#                          'ADD MAIN THEATRE 10': 'theatre','ADD MAIN THEATRE 11': 'theatre',
#                          'ADD MAIN THEATRE 12': 'theatre', 'ADD MAIN THEATRE 14': 'theatre',
#                          'ADD MAIN THEATRE 15': 'theatre', 'ADD MAIN THEATRE 16': 'theatre',
#                          'ADD MAIN THEATRE 17': 'theatre', 'ADD MAIN THEATRE 18': 'theatre',
#                          'ADD MAIN THEATRE 19': 'theatre', 'ADD MAIN THEATRE 20': 'theatre',
#                          'ADD MAIN THEATRE 21': 'theatre', 'ADD MAIN THEATRE 22': 'theatre',
#                          'ADD ATC THEATRE 31': 'theatre', 'ADD ATC THEATRE 32': 'theatre',
#                          'ADD ATC THEATRE 33': 'theatre', 'ADD ATC THEATRE 34': 'theatre',
#                          'ADD ATC THEATRE 35': 'theatre', 'ADD ATC THEATRE 36': 'theatre'}


#weekend and weekday transfers
weekend_transfers = alldata[alldata['is_weekend']]
weekday_transfers = alldata[~alldata['is_weekend']]




#list_of_weekend_admissions =[get_weekend_list(data) for data in data['admission_time']]


#now make the graph
#specific_data = alldata
#specific_data = weekend_admissions
#specific_data = weekday_admissions
#specific_data = pd.read_csv("combined_data.csv")
#specific_data.loc[admpoint[specific_data['admission_time'] == specific_data['extraid']].index, 'to'] = 'discharge'
#weekend_trans_by_month = [weekend_transfer[weekend_transfer['month'] == i] for i in range(1, 13)]






monthlist=[1,2,3,4,5,6,7,8,9,10,11,12]
en_list = []
nn_list = []
degrees_list = []
flow_h_list = []
data_list = []

it_is_weekend = True

for i in monthlist:
    if it_is_weekend == True:
        month_data = weekend_transfers[weekend_transfers['transfer_month'] == i]
    else:
        month_data = weekday_transfers[weekday_transfers['transfer_month'] == i]

    number_of_transfers = len(month_data['transfer_month'])
    # drop the columns that are not needed for the graph, also select adults or children
    month_data_reduced = month_data.loc[month_data['age'] > 16].drop(['transfer_dt', 'dt_adm', 'dt_dis', 'spec', 'age', 'asa'], axis=1)
    get_network_analytics(month_data_reduced)
    print(i, number_of_transfers)

#print(nn_list)
#print(en_list)
#print(degrees_list)
#print(flow_h_list)
print(data_list)

analysis_data_week = pd.DataFrame(columns=['month', 'number of transfers', 'number nodes', 'number edges', 'flow hierarchy', 'emergency degrees', 'incentrality theatres', 'outcentrality theatres'], data = data_list)
if it_is_weekend == True:
    analysis_data_week.to_csv('analysis_data_weekend.csv', header =True, index=False)
else:
    analysis_data_week.to_csv('analysis_data_weekday.csv', header = True, index = False)


#centrality_overall = defaultdict(list)
#for k,v in chain(incentrality.items(), outcentrality.items()):
#    centrality_overall[k].append(v)

#print(centrality_overall)
#dfcentrality = pd.DataFrame.from_dict(centrality_overall,orient='index')
#print(dfcentrality)



#shortest path in the directed graph, from a starting point source to a point target
#shortest_path = nx.algorithms.shortest_paths.generic.shortest_path(G, source = 'ICU', target = 'ER')
#print('shortest path is')
#print(shortest_path)


#fig = plt.figure(figsize=(7, 5))
#nx.set_node_attributes(G,'length_of_stay',los)
#pos = nx.circular_layout(G)
#widthedge = [d['weight'] *0.1 for _,_,d in G.edges(data=True)]
#nx.draw_networkx(G, pos=pos, with_labels=True, font_weight='bold', arrows = False, width= widthedge,  node_size=1300)
#nx.draw_circular(G)
#width = [d['weight'] for _,_,d in G.edges(data=True)]

#edge_labels=dict([((u,v,), d['weight'])
#             for u,v,d in G.edges(data=True)])
#nx.draw_networkx(G, with_labels=True, font_weight='bold' )
#nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels)
#plt.show()
#fig.savefig("weekendchildrennetworkgraph.png")
#plt.gcf().clear()