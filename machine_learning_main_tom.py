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
from datetime import timedelta


def get_separate_date_time(datetimeentry):
    # print(datetimeentry)
    if type(datetimeentry) == float:
        return datetime.max
    else:
        # this returns the date in a format where the hours and days can be accessed eg d.year or d.minute
        separate_date_time = datetime.strptime(datetimeentry, "%Y-%m-%d %H:%M:%S")
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
    # find the entries with the given dates
    entries = data[data['transfer_day'].isin(date_set)]
    return entries


def make_network_for_selected_days(selected_entries):
    # returns a network for the entries given
    # count the number of times a specific transfer appears to get edge weight, need to have only the from, to columns
    transfer_counts = selected_entries.groupby(['from', 'to']).count()
    # add the old index as a column - in the above the count became the index.
    transfer_counts = transfer_counts.reset_index()
    transfer_counts = transfer_counts[transfer_counts['ptid'] > 1]
    # Get a list of tuples that contain the values from the rows.
    transfer_counts.rename(columns={"ptid": "weight"}, inplace=True)
    edge_weight_data = transfer_counts[['from', 'to', 'weight']]
    # unweighted_edge_data = transfer_counts[['from', 'to']]
    # sum_of_all_transfers = edge_weight_data['e_weight'].sum()
    weighted_edges = list(
        itertools.starmap(lambda f, t, w: (f, t, int(w)), edge_weight_data.itertuples(index=False, name=None)))
    # unweighted_edges = list(itertools.starmap(lambda f, t: (f, t), unweighted_edge_data.itertuples(index=False, name=None)))

    G = nx.DiGraph()
    # print(weighted_edges)
    G.add_weighted_edges_from(weighted_edges)
    return G


def get_network_parameters(G, ws):
    # returns the network analysis parameters for the given G
    en = G.number_of_edges()
    nn = G.number_of_nodes()
    print("nn=", nn)

    # specific ICU measures - only works with dictionary that combines all the ICU together
    inter_icu = G.get_edge_data('ICU', 'ICU', default={}).get('weight', 0)
    icu_hdu = G.get_edge_data('ICU', 'HDU', default={}).get('weight', 0)

    # degrees, weighted degrees, bet centrality, flow hierarchy, density, transitivity, av shortest path,
    degrees = dict(nx.classes.function.degree(G))
    if ws == 1:
        print(degrees(G))

    emergency_degree = degrees.get('AE', 0)
    print(emergency_degree)
    icu_degree = degrees.get('ICU', 0)
    ct_degree = degrees.get('CT', 0)
    xr_degree = degrees.get('XR', 0)
    theatres_degree = degrees.get('theatre', 0)

    # flow hierarchy
    if nn == 0:
        flow_hierarchy = 0
    else:
        flow_hierarchy = nx.algorithms.hierarchy.flow_hierarchy(G)

    density_net = nx.density(G)
    transitivity_net = nx.transitivity(G)

    try:
        assortativity_net_inout = nx.degree_assortativity_coefficient(G, x='out', y='in', weight='weights')
    except ValueError:
        assortativity_net_inout = 0

    # voterank ranked list of nodes that are important in the network
    # vote_rank_list = nx.algorithms.centrality.voterank(G, number_of_nodes=5, max_iter=1000)
    # first_vr_node = vote_rank_list[0]
    # second_vr_node = vote_rank_list[1]
    # third_vr_node = vote_rank_list[2]
    # fourth_vr_node = vote_rank_list[3]
    # fifth_vr_node = vote_rank_list[4]

    # betweenness centrality
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

    # weighted degrees
    weighted_degrees = dict(nx.degree(G, weight='weight'))
    weighted_emergency_degree = weighted_degrees.get('AE', 0)
    weighted_ct_degree = weighted_degrees.get('CT', 0)
    weighted_xr_degree = weighted_degrees.get('XR', 0)
    weighted_icu_degree = weighted_degrees.get('ICU', 0)
    weighted_theatres_degree = weighted_degrees.get('theatre', 0)
    weighted_emergency_degree = weighted_degrees.get('AE', 0)

    # weighted_in_degrees = nx.DiGraph.in_degree(G,weight = 'weights')
    weighted_in_degrees = dict(G.in_degree(weight='weight'))
    weighted_icu_in_deg = weighted_in_degrees.get('ICU', 0)
    weighted_theatres_in_deg = weighted_in_degrees.get('theatre', 0)

    weighted_out_degrees = dict(G.out_degree(weight='weight'))
    weighted_icu_out_deg = weighted_out_degrees.get('ICU', 0)
    weighted_theatres_out_deg = weighted_out_degrees.get('theatre', 0)

    # transfer counts between certain areas
    medical_theatre_transfers = G.get_edge_data('medical ward', 'theatre', default={}).get('weight', 0)
    medical_medical_transfers = G.get_edge_data('medical ward', 'medical ward', default={}).get('weight', 0)
    ae_med = G.get_edge_data('AE', 'medical ward', default={}).get('weight', 0) + G.get_edge_data('AE', 'rehab',
                                                                                                  default={}).get(
        'weight', 0)
    ae_surg = G.get_edge_data('AE', 'surgical ward', default={}).get('weight', 0) + G.get_edge_data('AE',
                                                                                                    'neurosurgery ward',
                                                                                                    default={}).get(
        'weight', 0) + \
              G.get_edge_data('AE', 'orthopaedic ward', default={}).get('weight', 0) + \
              G.get_edge_data('AE', 'gynae surgical ward', default={}).get('weight', 0) + G.get_edge_data('AE',
                                                                                                          'surgical day ward',
                                                                                                          default={}).get(
        'weight', 0)
    if ae_surg == 0:
        ratio_wards_surg_med = 0
    else:
        ratio_wards_surg_med = ae_med / ae_surg

    return {
        f'number_nodes_{ws}': nn,
        f'number_edges_{ws}': en,
        f'emergency_degrees_{ws}': emergency_degree,
        f'emergency_strength_{ws}': weighted_emergency_degree,
        f'ct_degrees_{ws}': ct_degree,
        f'ct_strength_{ws}': weighted_ct_degree,
        f'xr_degrees_{ws}': xr_degree,
        f'xr_strength_{ws}': weighted_xr_degree,
        f'theatre_degrees_{ws}': theatres_degree,
        f'theatre_strength_{ws}': weighted_theatres_degree,
        f'theatres_instrength_{ws}': weighted_theatres_in_deg,
        f'theatres_outstrength_{ws}': weighted_theatres_out_deg,
        f'theatre_bet_centr_{ws}': theatres_bet_centrality,
        f'medical_theatre_transfers_{ws}': medical_theatre_transfers,
        f'med_med_transfers_{ws}': medical_medical_transfers,
        f'med_surg_ratio_{ws}': ratio_wards_surg_med,
        f'inter_icu_transfers_{ws}': inter_icu,
        f'icu_hdu_transfers_{ws}': icu_hdu,
        f'density_{ws}': density_net,
        f'transitivity_{ws}': transitivity_net,
        f'flow_hierarchy_{ws}': flow_hierarchy,
        f'assortativity_{ws}': assortativity_net_inout,
        f'icu_bet_centr_{ws}': icu_bet_centrality,
        f'icu_degrees_{ws}': icu_degree,
        f'icu_strength_{ws}': weighted_icu_degree,
        f'icu_instrength_{ws}': weighted_icu_in_deg,
        f'icu_outstrength_{ws}': weighted_icu_out_deg
    }


# need to calculate all transfers into ICU, all out of ICU, all into theatres
def get_other_params(day_data, ws):
    # calculate all ICU transfers in and out, theatre transfers
    icu_in_number = len(day_data[day_data['to'] == 'ICU'])
    icu_out_number = len(day_data[day_data['from'] == 'ICU'])

    theatre_in_number = len(day_data[day_data['to'] == 'theatre'])
    theatre_out_number = len(day_data[day_data['from'] == 'theatre'])

    return {
        f'icu_in_number_{ws}': icu_in_number,
        f'icu_out_number_{ws}': icu_out_number,
        f'theatre_in_number_{ws}': theatre_in_number,
        f'theatre_out_number_{ws}': theatre_out_number
    }


# runs the analysis for one set of dates ie one window
def get_data_for_window(data, d, window_size):
    # print('window size', window_size)
    window_dates = {d - timedelta(days=i) for i in range(0, window_size)}
    window_date_strings = {get_transfer_day(wd) for wd in window_dates}

    # print(window_date_strings)
    # print("window")
    # print(window_dates)
    # day_data = data_t_strain_cat[data_t_strain_cat['transfer_day'].isin(window_date_strings)]
    day_data = select_entries_by_date(data, window_date_strings)
    # number_of_transfers = len(day_data['transfer_day'])
    # drop the columns that are not needed for the graph, also select adults or children
    day_data_reduced = day_data.loc[day_data['age'] > 16].drop(
        ['transfer_dt', 'dt_adm', 'dt_dis', 'spec', 'age', 'asa'], axis=1)

    if len(day_data_reduced) == 0:
        return dict()

    nw = make_network_for_selected_days(day_data_reduced)
    nw_analytics = get_network_parameters(nw, window_size)
    other_params = get_other_params(day_data_reduced, window_size)
    # join the two lists together
    nw_analytics.update(other_params)
    return nw_analytics


# Now start of the actual work
# prepare the data set
data_full = pd.read_csv("adult_transfers.csv")
# data_full = data_full.drop(['from_loc','to_loc'], axis=1)
# data_full.rename(index=str, columns={'from_category': 'from'}, inplace = True)
# data_full.rename(index=str, columns={'to_category': 'to'}, inplace = True)
data_full = data_full[
    ['ptid', 'transfer_dt', 'dt_adm', 'dt_dis', 'spec', 'age', 'asa', 'breach_percentage', 'strain', 'bedsfree', 'from',
     'to']]
data_full['transfer_dt'] = pd.to_datetime(data_full['transfer_dt'], format="%Y-%m-%d %H:%M")
degree_hist_file = []

# put the day of transfer into a specific column for selecting later
data_full['transfer_day'] = data_full['transfer_dt'].map(get_transfer_day)

# get the list of dates to loop over
unique_dates = pd.Series(data_full['transfer_day'].unique())
dates_list = pd.to_datetime(unique_dates, format='%Y-%m-%d')

window_sizes = [1, 3, 7, 10]

all_row_data = list()

for d in dates_list:
    row_data = dict()

    for m in window_sizes:
        # data_for_window[m] = [get_data_for_window(data_full, d, m) for d in dates_list['date']]
        row_data.update(get_data_for_window(data_full, d, m))

    if len(row_data) > 0:
        row_data['dt'] = d
        all_row_data.append(row_data)
    # print(all_row_data[d])

ML_data = pd.DataFrame(data=all_row_data)
ML_data.to_csv('ML_data.csv', header=True, index=False)
