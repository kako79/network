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
alldata= pd.read_csv("all_transfers_1110.csv")
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
#print('in and out centrality')
#print(incentrality)
#print(outcentrality)


#centrality_overall = defaultdict(list)
#for k,v in chain(incentrality.items(), outcentrality.items()):
#    centrality_overall[k].append(v)

#print(centrality_overall)
#dfcentrality = pd.DataFrame.from_dict(centrality_overall,orient='index')
#print(dfcentrality)


# calculate the degree
degrees_list = [[n, d] for n, d in degrees]
degrees_data = pd.DataFrame(degrees_list, columns=['node', 'degree'])
#degrees_data_degree = degrees_data['degree']
degrees_data.to_csv('degrees_all.csv', header =True, index=False)

#look at degrees of the emergency department, need to change it to a dictionary to be able to look up the degree value for this node
degrees_data.set_index('node', inplace=True)
degrees_dict = degrees_data.to_dict()['degree']

#check if there is data in this specific subset eg there may not be data in a weekend stress set in summer...
if 'AE' in degrees_dict:
    emergency_degrees = degrees_dict['AE']
    #print('in dict')
    no_data = False
    else:
    #print('not in dict')
    no_data = True
    emergency_degrees = 0


    #degrees_list.append(list(degrees.values))
    #degrees_list.to_csv('degrees%s.csv' % str(i), header=True, index=False)

#number of transfers from medical wards to theatre
acute_to_theatre = G.get_edge_data('acute medical ward', 'theatre', default={}).get('weight', 0)
gen_to_theatre = G.get_edge_data('general medical ward', 'theatre', default={}).get('weight', 0)
card_to_theatre = G.get_edge_data('cardiology ward', 'theatre', default={}).get('weight', 0)
rehab_to_theatre = G.get_edge_data('rehab', 'theatre', default={}).get('weight', 0)
total_medical_to_theatre = acute_to_theatre + gen_to_theatre + card_to_theatre + rehab_to_theatre

#number of circular or unnecessary ward transfers
med_to_med_acute = G.get_edge_data('acute medical ward', 'acute medical ward', default = {}).get('weight', 0)
med_to_med_acgen = G.get_edge_data('acute medical ward', 'general medical ward', default={}).get('weight', 0)
med_to_med_genac = G.get_edge_data('general medical ward', 'acute medical ward', default={}).get('weight', 0)
med_to_med_general = G.get_edge_data('general medical ward', 'general medical ward', default={}).get('weight', 0)


med_to_surg = G.get_edge_data('general medical ward', 'general surgical ward', default ={}).get('weight', 0)
med_to_ortho = G.get_edge_data('general medical ward', ' orthopaedic ward', default ={}).get('weight', 0)
med_to_surg_acute = G.get_edge_data('acute medical ward', 'general surgical ward', default={}).get('weight', 0)
med_to_orth_acute = G.get_edge_data('acute medical ward', ' orthopaedic ward', default={}).get('weight', 0)
acmed_to_ns = G.get_edge_data('acute medical ward', 'ns ward', default={}).get('weight', 0)
genmed_to_ns = G.get_edge_data('general medical ward', 'ns ward', default={}).get('weight', 0)
acmed_to_atc = G.get_edge_data('acute medical ward', 'ATC surgical ward', default={}).get('weight', 0)
genmed_to_atc = G.get_edge_data('general medical ward', 'ATC surgical ward', default={}).get('weight', 0)
total_medical_ward_transfers = med_to_med_acute + med_to_med_general+med_to_med_acgen+med_to_med_genac+ med_to_ortho+ med_to_surg+ med_to_surg_acute+ med_to_orth_acute+acmed_to_ns+genmed_to_ns+acmed_to_atc+genmed_to_atc
#print (total_medical_ward_transfers)

ae_surg = G.get_edge_data('AE', 'general surgical ward', default={}).get('weight', 0)+ G.get_edge_data('AE', 'orthopaedic ward', default={}).get('weight', 0) +G.get_edge_data('AE', 'ATC surgical ward', default={}).get('weight', 0) + G.get_edge_data('AE', 'gynae ward', default={}).get('weight', 0)+  G.get_edge_data('AE', 'ns ward', default={}).get('weight', 0)
print(ae_surg)
ae_med = G.get_edge_data('AE', 'acute medical ward', default={}).get('weight', 0) + G.get_edge_data('AE', 'general medical ward', default={}).get('weight', 0) + G.get_edge_data('AE', 'cardiology ward', default={}).get('weight', 0) + G.get_edge_data('AE', 'rehab', default={}).get('weight', 0) +  G.get_edge_data('AE', 'cdu', default={}).get('weight', 0)
if ae_surg == 0:
    ratio_wards_surg_med = 0
else:
    ratio_wards_surg_med = ae_med/ae_surg


# calculate the centrality of each node - fraction of nodes the incoming/outgoing edges are connected to
incentrality = nx.algorithms.centrality.in_degree_centrality(G)
# check if the theatre node exists in this data subset
if 'theatre' in incentrality:
    in_theatre_centrality = incentrality['theatre']
else:
    in_theatre_centrality = 0

outcentrality = nx.algorithms.centrality.out_degree_centrality(G)
if 'theatre' in outcentrality:
    out_theatre_centrality = outcentrality['theatre']
else:
    out_theatre_centrality = 0

if 'AE' in outcentrality:
    out_ed_centrality = outcentrality['AE']
else:
    out_ed_centrality = 0

# flow hiearchy - finds strongly connected components
if nn == 0:
    flow_hierarchy = 0
else:
    flow_hierarchy = nx.algorithms.hierarchy.flow_hierarchy(G)


bet_centr = nx.algorithms.centrality.betweenness_centrality(G)
if 'theatre' in bet_centr:
    theatres_bet_centrality = bet_centr['theatre']
else:
    theatres_bet_centrality = 0


if en == 0:
    theatres_eigen_centr = 0
    ed_eigen_centr = 0
    assortativity_net_inout = 0
else:
    eigen_centr = nx.eigenvector_centrality_numpy(G)
    assortativity_net_inout = nx.degree_assortativity_coefficient(G, x='out', y='in', weight='weights')
    if 'theatre' in eigen_centr:
        theatres_eigen_centr = eigen_centr['theatre']
    else:
        theatres_eigen_centr = 0

    if 'AE' in eigen_centr:
        ed_eigen_centr = eigen_centr['AE']
    else:
        ed_eigen_centr = 0

density_net = nx.density(G)
transitivity_net = nx.transitivity(G)




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

data_list.append({'month':i,'number of transfers': len(data_reduced['transfer_day']),'number nodes': nn,'number edges': en,'flow hierarchy': flow_hierarchy,
                      'emergency degrees': emergency_degrees,'outcentrality ed': out_ed_centrality, 'incentrality theatres': in_theatre_centrality,
                      'outcentrality theatres': out_theatre_centrality, 'bet centrality theatres': theatres_bet_centrality, 'medical to theatre': total_medical_to_theatre,
                      'medical ward transfers': total_medical_ward_transfers, 'med surg ratio': ratio_wards_surg_med, 'eigen_centr_theatre': theatres_eigen_centr,
                      'eigen_centr_ed': ed_eigen_centr, 'density': density_net, 'transitivity':transitivity_net,'average_breach_percentage': average_breach_perc,
                      'average bed occupancy': average_bed_occupancy})

all_network_info_df = pd.DataFrame(columns=['month', 'number of transfers', 'number nodes', 'number edges', 'flow hierarchy', 'emergency degrees', 'outcentrality ed',
                                         'incentrality theatres', 'outcentrality theatres', 'bet centrality theatres','medical to theatre','medical ward transfers',
                                         'med surg ratio','eigen_centr_theatre','eigen_centr_ed', 'density', 'transitivity', 'average_breach_percentage', 'average bed occupancy'], data = data_list)


all_network_info_df.to_csv('all_network_info.csv', header=True, index=False)
print('all network infor file created')



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
