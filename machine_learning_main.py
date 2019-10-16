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

def make_network_for_selected_days(selected_entries)
    # count the number of times a specific transfer appears to get edge weight, need to have only the from, to columns
    transfer_counts = selected_entries.groupby(['from', 'to']).count()
    # add the old index as a column - int he above the count became the index.
    transfer_counts = transfer_counts.reset_index()
    transfer_counts = transfer_counts[transfer_counts['ptid'] > 1]
    # Get a list of tuples that contain the values from the rows.
    edge_weight_data = transfer_counts[['from', 'to', 'ptid']]
    unweighted_edge_data = transfer_counts[['from', 'to']]
    sum_of_all_transfers = edge_weight_data['ptid'].sum()
    edge_weight_data['ptid'] = edge_weight_data['ptid']  # /sum_of_all_transfers

    weighted_edges = list(
        itertools.starmap(lambda f, t, w: (f, t, int(w)), edge_weight_data.itertuples(index=False, name=None)))
    unweighted_edges = list(
        itertools.starmap(lambda f, t: (f, t), unweighted_edge_data.itertuples(index=False, name=None)))

    G = nx.DiGraph()
    # print(weighted_edges)
    G.add_weighted_edges_from(weighted_edges)

def get_network_parameters():
    return