#now make networks for each day
# to follow from perf_categories
import pandas as pd
import numpy as np
from collections import deque, namedtuple
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


def get_diameter(network):
    try:
        return network.diameter(G)
    except:
        return 0

def get_shortest_path(G):
    try:
        return nx.average_shortest_path_length(G)
    except:
        return 0

def get_date_number(dt):
    return dt.year * 10000 + dt.month * 100 + dt.day

def get_transfer_day(date):
    strdate = str(date)
    fmt = "%Y-%m-%d"
    try:
        d = datetime.strptime(strdate, fmt)
    except ValueError as v:
        ulr = len(v.args[0].partition('unconverted data remains: ')[2])
        if ulr:
            d = datetime.strptime(strdate[:-ulr], fmt)
        else:
            raise v
    return d

data_t_strain_cat = pd.read_csv("transfers_strain_cat.csv")
data_t_strain_cat = data_t_strain_cat.drop(['from_loc','to_loc'], axis=1)
data_t_strain_cat.rename(index=str, columns={'from_category': 'from'}, inplace = True)
data_t_strain_cat.rename(index=str, columns={'to_category': 'to'}, inplace = True)


def get_network_analytics(data_reduced):
    # weighted edges first
    # count the number of times a specific transfer appears to get edge weight
    transfer_counts = data_reduced.groupby(['from', 'to']).count()

    # add the old index as a column - int he above the count became the index.
    transfer_counts = transfer_counts.reset_index()
    transfer_counts = transfer_counts[transfer_counts['ptid'] > 1]
    # Get a list of tuples that contain the values from the rows.
    edge_weight_data = transfer_counts[['from', 'to', 'ptid']]
    sum_of_all_transfers = edge_weight_data['ptid'].sum()
    edge_weight_data['ptid'] = edge_weight_data['ptid'] / sum_of_all_transfers
    #edge_weight_data.to_csv('edge_wdadult%s.csv' % str(i), header=True, index=False)
    weighted_edges = list(
        itertools.starmap(lambda f, t, w: (f, t, int(w)), edge_weight_data.itertuples(index=False, name=None)))

    G = nx.DiGraph()
    # print(weighted_edges)
    G.add_weighted_edges_from(weighted_edges)
    en = G.number_of_edges()
    nn = G.number_of_nodes()
    #print(en)
    #print(nn)
    #en_list.append(en)
    #nn_list.append(nn)

    # calculate the degree
    degrees = nx.classes.function.degree(G)
    degrees_list = [[n, d] for n, d in degrees]
    degrees_data = pd.DataFrame(degrees_list, columns=['node', 'degree'])
    #degrees_data.to_csv('degrees_weadult%s.csv'%str(i), header =True, index=False)
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
    #print('degrees')
    #print(degrees)

    # histdegrees = nx.classes.function.degree_histogram(G)
    # print('histdegrees')
    # print(histdegrees)

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



    #print (incentrality)
    #print(in_theatre_centrality)

    # flow hiearchy - finds strongly connected components
    if nn == 0:
        flow_hierarchy = 0
    else:
        flow_hierarchy = nx.algorithms.hierarchy.flow_hierarchy(G)
    #print('flow hierarchy')
    #print(flow_hierarchy)
    #flow_h_list.append(flow_hierarchy)



    if nn ==0:
        diameter_net = 0
    else:
        diameter_net = get_diameter(G)

    #if nn== 0:
    #    clustering_net = 0
    #else:
    #    clustering_net = nx.average_clustering(G)

    if nn==0:
        av_shortest_path_net = 0
    else:
        av_shortest_path_net = get_shortest_path(G)



    data_list.append({'date':i,'number of transfers': len(data_reduced['transfer_day']),'number nodes': nn,'number edges': en,'flow hierarchy': flow_hierarchy, 'emergency degrees': emergency_degrees, 'incentrality theatres': in_theatre_centrality, 'outcentrality theatres': out_theatre_centrality, 'diameter': diameter_net, 'shortest path': av_shortest_path_net})
    return data_list

data_t_strain_cat['transfer_dt'] = pd.to_datetime(data_t_strain_cat['transfer_dt'], format="%Y-%m-%d %H:%M")
data_list = []

data_t_strain_cat['transfer_day'] = data_t_strain_cat['transfer_dt'].map(get_transfer_day)
#get the list of dates to loop over
dates_list = pd.read_csv("ed_performance_all.csv")
dates_list['date'] = pd.to_datetime(dates_list['day'], format='%d/%m/%Y')

all_datesdf = dates_list['date'].map(get_transfer_day)
#load ed_performance and bedstate



for i in all_datesdf:
    print(i)
    day_data = data_t_strain_cat[data_t_strain_cat['transfer_day'] == i]
    number_of_transfers = len(day_data['transfer_day'])
    # drop the columns that are not needed for the graph, also select adults or children
    day_data_reduced = day_data.loc[day_data['age'] > 16].drop(['transfer_dt', 'dt_adm', 'dt_dis', 'spec', 'age', 'asa'], axis=1)
    get_network_analytics(day_data_reduced)
    print(i, number_of_transfers)


#print(data_list)


arimaprep_data = pd.DataFrame(columns=['date', 'number of transfers', 'number nodes', 'number edges', 'flow hierarchy', 'emergency degrees', 'incentrality theatres', 'outcentrality theatres', 'diameter', 'shortest path'], data = data_list)

arimaprep_data['date_number'] =  arimaprep_data['date'].map(get_date_number)

#add on the information about the hospital state from the ED performance file
ed_performance = pd.read_csv("ed_performance_all.csv")
# need transfer date only in a separate column
ed_performance['date'] = pd.to_datetime(ed_performance['day'], format='%d/%m/%Y')
ed_performance['date_number'] = ed_performance['date'].map(get_date_number)
ed_performance.drop(['date'], axis=1, inplace=True)
ed_performance.set_index('date_number', drop=True, inplace=True)
arimaprep_data_ed = arimaprep_data.join(ed_performance, on='date_number', how='left')

#add on bedstate information - all beds
bedstate_info = pd.read_csv("all_beds_info.csv")
bedstate_info['date'] = pd.to_datetime(bedstate_info['Date'], format='%Y-%m-%d')
bedstate_info['date_number'] = bedstate_info['date'].map(get_date_number)
bedstate_info.drop(['date'], axis = 1, inplace = True)
bedstate_info.set_index('date_number', drop = True, inplace = True)
arimaprep_data_all= arimaprep_data_ed.join(bedstate_info, on = 'date_number', how = 'left')


arimaprep = arimaprep_data_all.drop(['date_number', 'day', 'Date'], axis=1)
#now we have a file with all trasnfers and the bestate and ed performance
#now need to combine wards into categories to allow for daily network construction with enough data

arimaprep.to_csv('arima_prep.csv', header=True, index=False)
print('performance added on file created')



#data into csv
