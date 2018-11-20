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

def get_shortest_path(G, edge_weights):
    try:
        return nx.shortest_path_length(G,source = 'AE', target=  'discharge', weight = edge_weights)
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

def get_month(date):
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
    return d.month



data_t_strain_cat = pd.read_csv("transfers_strain_cat_noweekday.csv")
data_t_strain_cat = data_t_strain_cat.drop(['from_loc','to_loc'], axis=1)
data_t_strain_cat.rename(index=str, columns={'from_category': 'from'}, inplace = True)
data_t_strain_cat.rename(index=str, columns={'to_category': 'to'}, inplace = True)

def get_network_analytics(data_reduced):
    #calculate average breach and average beds occupied:
    average_breach_perc = data_reduced['breach_percentage'].mean()
    average_bed_occupancy = data_reduced['Total Occupied'].mean()

    # weighted edges first
    # count the number of times a specific transfer appears to get edge weight
    transfer_counts = data_reduced.groupby(['from', 'to']).count()

    # add the old index as a column - int he above the count became the index.
    transfer_counts = transfer_counts.reset_index()
    transfer_counts = transfer_counts[transfer_counts['ptid'] > 1]
    # Get a list of tuples that contain the values from the rows.
    edge_weight_data = transfer_counts[['from', 'to', 'ptid']]
    edge_weight_data.rename(index=str, columns={'ptid': 'weight'}, inplace=True)
    sum_of_all_transfers = edge_weight_data['weight'].sum()
    #print(sum_of_all_transfers)
    #edge_weight_data['ptid'] = edge_weight_data['ptid']/sum_of_all_transfers
    #edge_weight_data.to_csv('edge_wdadult%s.csv' % str(i), header=True, index=False)
    weighted_edges = list(
        itertools.starmap(lambda f, t, w: (f, t, int(w)), edge_weight_data.itertuples(index=False, name=None)))

    G = nx.DiGraph()
    # print(weighted_edges)
    G.add_weighted_edges_from(weighted_edges)


    en = G.number_of_edges()
    nn = G.number_of_nodes()


    # calculate the degree
    degrees = nx.classes.function.degree(G)


    degrees_list = [[n, d] for n, d in degrees]
    if b ==1000:
        print(degrees_list)


    degrees_data = pd.DataFrame(degrees_list, columns=['node', 'degree'])
    #degrees_data_degree = degrees_data['degree']
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
    total_medical_ward_transfers = med_to_med_acute + med_to_med_general+med_to_med_acgen+med_to_med_genac+ med_to_ortho+ med_to_surg+ med_to_surg_acute+ med_to_orth_acute+acmed_to_ns+genmed_to_ns
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

    data_list.append({'month':i,'number of transfers': len(data_reduced['transfer_day']),'number nodes': nn,'number edges': en,'flow hierarchy': flow_hierarchy, 'emergency degrees': emergency_degrees,'outcentrality ed': out_ed_centrality, 'incentrality theatres': in_theatre_centrality, 'outcentrality theatres': out_theatre_centrality, 'bet centrality theatres': theatres_bet_centrality, 'medical to theatre': total_medical_to_theatre, 'medical ward transfers': total_medical_ward_transfers, 'med surg ratio': ratio_wards_surg_med, 'average_breach_percentage': average_breach_perc, 'average bed occupancy': average_bed_occupancy})


    return data_list

data_t_strain_cat['transfer_dt'] = pd.to_datetime(data_t_strain_cat['transfer_dt'], format="%Y-%m-%d %H:%M")
data_list = []
degree_hist_file = []

data_t_strain_cat['transfer_day'] = data_t_strain_cat['transfer_dt'].map(get_transfer_day)
data_t_strain_cat['transfer_month'] = data_t_strain_cat['transfer_dt'].map(get_month)
#get the list of dates to loop over
dates_list = pd.read_csv("ed_performance_all.csv")
dates_list['date'] = pd.to_datetime(dates_list['day'], format='%d/%m/%Y')

all_datesdf = dates_list['date'].map(get_transfer_day)

data_t_strain_cat['date_number'] =  data_t_strain_cat['transfer_day'].map(get_date_number)

##load ed_performance and bedstate
##add on the information about the hospital state from the ED performance file
#ed_performance = pd.read_csv("ed_performance_all.csv")
## need transfer date only in a separate column
#ed_performance['date'] = pd.to_datetime(ed_performance['day'], format='%d/%m/%Y')
#ed_performance['date_number'] = ed_performance['date'].map(get_date_number)
#ed_performance.drop(['date', 'day'], axis=1, inplace=True)
#ed_performance.set_index('date_number', drop=True, inplace=True)
monthly_arima_data_all = data_t_strain_cat

##add on bedstate information - all beds
#bedstate_info = pd.read_csv("all_beds_info.csv")
#bedstate_info['date'] = pd.to_datetime(bedstate_info['Date'], format='%Y-%m-%d')
#bedstate_info['date_number'] = bedstate_info['date'].map(get_date_number)
#bedstate_info.drop(['date'], axis = 1, inplace = True)
#bedstate_info.set_index('date_number', drop = True, inplace = True)
#monthly_arima_data_all= monthly_arima_data_ed.join(bedstate_info, on = 'date_number', how = 'left')


monthlist=[1,2,3,4,5,6,7,8,9,10,11,12]
en_list = []
nn_list = []
degrees_list = []
flow_h_list = []
data_list = []
data_list_stress = []
data_list_calm = []
it_is_weekend = False
b=0
#data seprated by weekend weekday
for i in monthlist:
    b+=1
    print(b)
    month_data = monthly_arima_data_all[monthly_arima_data_all['transfer_month'] == i]
    number_of_transfers = len(month_data['transfer_month'])
    # drop the columns that are not needed for the graph, also select adults or children
    month_data_reduced = month_data.loc[month_data['age'] > 16].drop(['transfer_dt', 'dt_adm', 'dt_dis', 'spec', 'age', 'asa'], axis=1)
    get_network_analytics(month_data_reduced)
    print(i, number_of_transfers)


monthly_arima_df = pd.DataFrame(columns=['month', 'number of transfers', 'number nodes', 'number edges', 'flow hierarchy', 'emergency degrees', 'outcentrality ed','incentrality theatres', 'outcentrality theatres', 'bet centrality theatres','medical to theatre','medical ward transfers', 'med surg ratio', 'average_breach_percentage', 'average bed occupancy'], data = data_list)

#monthly_arima_df = monthly_arima_df.drop(['date_number', 'day', 'Date'], axis=1)
max_beds = 1154 # maximal number of beds

def get_free_beds(beds_occupied):
    return max_beds - beds_occupied


monthly_arima_df['bedsfree'] = monthly_arima_df['average bed occupancy'].map(get_free_beds)
monthly_arima_df['strain'] = monthly_arima_df.bedsfree * monthly_arima_df.breach_percentage
#now we have a file with all trasnfers and the bestate and ed performance
#now need to combine wards into categories to allow for daily network construction with enough data

monthly_arima_df.to_csv('monthly_arima_noweekday_nov20.csv', header=True, index=False)
print('performance added on file created')
