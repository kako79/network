import numpy as np
import itertools
import functools

import matplotlib
matplotlib.use('agg')
import matplotlib.pyplot as plt

import pandas as pd
from mpl_toolkits import mplot3d
from matplotlib import cm
from matplotlib import colors
import networkx as nx
from collections import Counter
from itertools import chain
from collections import defaultdict
from datetime import datetime


def get_separate_date_time(datetimeentry):
    print(datetimeentry)
    if type(datetimeentry) == float:
        return datetime.max
    else:
        #this returns the date in a format where the hours and days can be accessed eg d.year or d.minute
        separate_date_time = datetime.strptime(datetimeentry,"%Y-%m-%d %H:%M:%S")
        return separate_date_time

def make_into_time(dt_entry):
    dt = datetime.strptime(dt_entry, "%Y-%m-%d")
    return dt

def get_transfer_day(date):
    strdate = str(date)
    fmt = "%Y-%m-%d"
    try:
        dd = datetime.strptime(strdate, fmt)
    except ValueError as v:
        ulr = len(v.args[0].partition('unconverted data remains: ')[2])
        if ulr:
            d = datetime.strptime(strdate[:-ulr], fmt)
            date_day = d.date()
            dd = date_day.strftime('%Y-%m-%d')
        else:
            raise v
    return dd


def select_entries_by_date(data, date_set):
    #find the entries with the given dates
    entries = data[data['day_of_transfer'].isin(date_set)]
    return entries

def make_network_for_selected_days(selected_entries):
    #returns a network for the entries given
    # count the number of times a specific transfer appears to get edge weight, need to have only the from, to columns
    transfer_counts = selected_entries.groupby(['from', 'to']).count()
    # add the old index as a column - in the above the count became the index.
    transfer_counts = transfer_counts.reset_index()
    transfer_counts = transfer_counts[transfer_counts['ptid'] > 1]
    # Get a list of tuples that contain the values from the rows.
    transfer_counts.rename(columns={"ptid": "e_weight"})
    edge_weight_data = transfer_counts[['from', 'to', 'e_weight']]
    #unweighted_edge_data = transfer_counts[['from', 'to']]
    #sum_of_all_transfers = edge_weight_data['e_weight'].sum()
    weighted_edges = list(
        itertools.starmap(lambda f, t, w: (f, t, int(w)), edge_weight_data.itertuples(index=False, name=None)))
    #unweighted_edges = list(itertools.starmap(lambda f, t: (f, t), unweighted_edge_data.itertuples(index=False, name=None)))

    G = nx.DiGraph()
    # print(weighted_edges)
    G.add_weighted_edges_from(weighted_edges)
    return G


def get_network_parameters(G):
    #returns the network analysis parameters for the given G
    en = G.number_of_edges()
    nn = G.number_of_nodes()

    #specific ICU measures - only works with dictionary that combines all the ICU together
    inter_icu = G.get_edge_data('ICU', 'ICU', default={}).get('weight', 0)
    icu_hdu = G.get_edge_data('ICU', 'HDU', default={}).get('weight', 0)


    # degrees, weighted degrees, bet centrality, flow hierarchy, density, transitivity, av shortest path,
    degrees = dict(nx.classes.function.degree(G))
    emergency_degree = degrees.get('AE', 0)
    icu_degree = degrees.get('ICU', 0)
    ct_degree = degrees.get('CT', 0)
    xr_degree= degrees.get('XR',0)
    theatres_degree = degrees.get('theatre', 0)

    #flow hierarchy
    if nn == 0:
        flow_hierarchy = 0
    else:
        flow_hierarchy = nx.algorithms.hierarchy.flow_hierarchy(G)

    density_net = nx.density(G)
    transitivity_net = nx.transitivity(G)
    assortativity_net_inout = nx.degree_assortativity_coefficient(G, x='out', y='in', weight='weights')

    #voterank ranked list of nodes that are important in the network
    vote_rank_list = nx.algorithms.centrality.voterank(G, number_of_nodes = 5, max_iter = 1000)
    first_vr_node = vote_rank_list[0]
    second_vr_node = vote_rank_list[1]
    third_vr_node = vote_rank_list[2]
    fourth_vr_node = vote_rank_list[3]
    fifth_vr_node = vote_rank_list[4]

    #betweenness centrality
    bet_centr = nx.algorithms.centrality.betweenness_centrality(G)
    if 'theatre' in bet_centr:
        theatres_bet_centrality = bet_centr['theatre']
    else:
        theatres_bet_centrality = 0
    if 'ICU' in bet_centr:
        icu_bet_centrality = bet_centr['ICU']
    else:
        icu_bet_centrality = 0

    if 'HDU' in bet_centr:
        hdu_bet_centrality = bet_centr['HDU']
    else:
        hdu_bet_centrality = 0

    #weighted degrees
    weighted_degrees = dict(nx.degree(G, weight='weight'))
    weighted_emergency_degree = weighted_degrees.get('AE', 0)
    weighted_ct_degree = weighted_degrees.get('CT',0)
    weighted_xr_degree = weighted_degrees.get('XR',0)
    weighted_icu_degree = weighted_degrees.get('ICU', 0)
    weighted_theatres_degree = weighted_degrees.get('theatre', 0)
    weighted_emergency_degree = weighted_degrees.get('AE',0)

    # weighted_in_degrees = nx.DiGraph.in_degree(G,weight = 'weights')
    weighted_in_degrees = dict(G.in_degree(weight='weight'))
    weighted_icu_in_deg = weighted_in_degrees.get('ICU', 0)
    weighted_theatres_in_deg = weighted_in_degrees('theatre', 0)


    weighted_out_degrees = dict(G.out_degree(weight='weight'))
    weighted_icu_out_deg = weighted_out_degrees.get('ICU', 0)
    weighted_theatres_out_deg = weighted_out_degrees.get('theatre', 0)


    #transfer counts between certain areas
    medical_theatre_transfers = G.get_edge_data('medical ward', 'theatre', default={}).get('weight', 0)
    medical_medical_transfers = G.get_edge_data('medical ward', 'medical ward', default={}).get('weight', 0)
    ae_med = G.get_edge_data('AE', 'medical ward', default={}).get('weight', 0) + G.get_edge_data('AE', 'rehab',default={}).get('weight', 0)
    ae_surg = G.get_edge_data('AE', 'surgical ward', default={}).get('weight', 0) + G.get_edge_data('AE','neurosurgery ward',default={}).get('weight', 0) + \
              G.get_edge_data('AE', 'orthopaedic ward', default={}).get('weight',0)+\
              G.get_edge_data('AE', 'gynae surgical ward', default={}).get('weight', 0) + G.get_edge_data('AE','surgical day ward',default={}).get('weight',0)
    if ae_surg == 0:
        ratio_wards_surg_med = 0
    else:
        ratio_wards_surg_med = ae_med/ae_surg

    return {'number_nodes': nn,'number_edges': en,
            'emergency_degrees': emergency_degree, 'emergency_strength': weighted_emergency_degree,
            'ct_degrees': ct_degree, 'ct_strength': weighted_ct_degree, 'xr_degrees': xr_degree, 'xr_strength': weighted_xr_degree,
            'theatre_degrees':theatres_degree, 'theatre_strength': weighted_theatres_degree,'theatres_instrength':weighted_theatres_in_deg,
            'theatres_outstrength':weighted_theatres_out_deg, 'theatre_bet_centr': theatres_bet_centrality,
            'medical_theatre_transfers': medical_theatre_transfers,'med_med_transfers': medical_medical_transfers, 'med_surg_ratio': ratio_wards_surg_med,
            'inter_icu_transfers': inter_icu, 'icu_hdu_transfers': icu_hdu,
            'density': density_net, 'transitivity': transitivity_net,  'flow_hierarchy': flow_hierarchy,'assortativity':assortativity_net_inout,
            'icu_bet_centr': icu_bet_centrality, 'icu_degrees': icu_degree, 'icu_strength': weighted_icu_degree, 'icu_instrength': weighted_icu_in_deg,
            'icu_outstrength': weighted_icu_out_deg}


#need to calculate all transfers into ICU, all out of ICU, all into theatres
def get_other_params(day_data):
    #calculate all ICU transfers in and out, theatre transfers
    icu_in_number = len(day_data[day_data['to' == 'ICU']])
    icu_out_number = len(day_data[day_data['from' == 'ICU']])

    theatre_in_number = len(day_data[day_data['to' == 'theatre']])
    theatre_out_number = len(day_data[day_data['from' == 'theatre']])
    return {'icu_in_number': icu_in_number, 'icu_out_number': icu_out_number, 'theatre_in_number': theatre_in_number, 'theatre_out_number':theatre_out_number}

#runs the analysis for one set of dates ie one window
def get_data_for_window(data, d,window_size):
    window_dates = {d - timedelta64(i, 'D') for i in range(0, window_size)}
    window_date_strings = {get_transfer_day(wd) for wd in window_dates}
    #day_data = data_t_strain_cat[data_t_strain_cat['transfer_day'].isin(window_date_strings)]
    day_data = select_entries_by_date(data, window_date_strings)
    #number_of_transfers = len(day_data['transfer_day'])
    # drop the columns that are not needed for the graph, also select adults or children
    day_data_reduced = day_data.loc[day_data['age'] > 16].drop(['transfer_dt', 'dt_adm', 'dt_dis', 'spec', 'age', 'asa'], axis=1)
    nw = make_network_for_selected_days(day_data_reduced)
    nw_analytics = get_network_parameters(nw)
    other_params = get_other_params(day_data_reduced)
    #join the two lists together
    output = nw_analytics+ other_params
    return output



#Now start of the actual work
#prepare the data set
data_full = pd.read_csv("transfers_adult.csv")
data_full = data_full.drop(['from_loc','to_loc'], axis=1)
data_full.rename(index=str, columns={'from_category': 'from'}, inplace = True)
data_full.rename(index=str, columns={'to_category': 'to'}, inplace = True)
data_full['transfer_dt'] = pd.to_datetime(data_full['transfer_dt'], format="%Y-%m-%d %H:%M")
degree_hist_file = []
#put the day of transfer into a specific column for selecting later
data_full['transfer_day'] = data_full['transfer_dt'].map(get_transfer_day)
#get the list of dates in ed performance to loop over
dates_list = pd.read_csv("ed_performance_all.csv")
dates_list['date'] = pd.to_datetime(dates_list['day'], format='%d/%m/%Y')
all_datesdf = dates_list['date'].map(get_transfer_day)

window_sizes= [0,1,3,7,10]

data_for_day = []

for d in dates_list:
    data_for_window=[]

    for m in window_sizes:
        #data_for_window[m] = [get_data_for_window(data_full, d, m) for d in dates_list['date']]
        data_for_window[m] = get_data_for_window(data_full, d , m)

    data_for_day[d] = data_for_window[0] + data_for_window[1] + data_for_window [2] + data_for_window[3] + data_for_window [4]











