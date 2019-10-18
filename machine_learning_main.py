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


data_full = pd.read_csv("transfers_adult.csv")

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




    data_list.append(
        {'number nodes': nn, 'number edges': en, 'emergency degrees': emergency_degrees, 'outcentrality ed': out_ed_centrality,
         'incentrality theatres': in_theatre_centrality,
         'outcentrality theatres': out_theatre_centrality, 'bet centrality theatres': theatres_bet_centrality,
         'eigen_centr_theatre': theatres_eigen_centr, 'bet_centr_gm': gm_bet_centrality,
         'bet_centr_am': am_bet_centrality, 'bet_centr_cdu': cdu_bet_centrality, 'bet_centr_card': card_bet_centrality,
         'eigen_centr_ed': ed_eigen_centr, 'flow hierarchy': flow_hierarchy, 'density': density_net,
         'transitivity': transitivity_net, 'av_shortest_path': average_shortest_path,
         'average_ae_percentage': average_ae_perc,
         'average_beds_free': average_beds_free})
    return



#need to calculate all transfers into ICU, all out of ICU, all into theatres