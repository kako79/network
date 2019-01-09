

import matplotlib
#from mpl_toolkits import mplot3d
#from matplotlib import cm
#from matplotlib import colors
import networkx as nx
#from collections import Counter
#from itertools import chain
#from collections import defaultdict
from datetime import datetime
import pandas as pd

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




transfer_data = pd.read_csv("transfers_2019_01_09.csv")
transfer_data['date'] = pd.to_datetime(transfer_data['transfer_dt'], format='%d/%m/%Y')
transfer_data['date_as_number'] = transfer_data['date'].map(get_date_number)

ed_performance = pd.read_csv("ed_performance_all.csv")
# need transfer date only in a separate column
ed_performance['date'] = pd.to_datetime(ed_performance['day'], format='%d/%m/%Y')
ed_performance['date_number'] = ed_performance['date'].map(get_date_number)
ed_performance.drop(['date'], axis=1, inplace=True)
ed_performance.set_index('date_number', drop=True, inplace=True)
transfer_data_ed = transfer_data.join(ed_performance, on='date_as_number', how='left')


#add on bedstate information - all beds
bedstate_info = pd.read_csv("all_beds_info.csv")
bedstate_info['date'] = pd.to_datetime(bedstate_info['Date'], format='%Y-%m-%d')
bedstate_info['date_number'] = bedstate_info['date'].map(get_date_number)
bedstate_info.drop(['date'], axis = 1, inplace = True)
bedstate_info.set_index('date_number', drop = True, inplace = True)
transfer_data_beded= transfer_data_beded.join(bedstate_info, on = 'date_as_number', how = 'left')


transfer_strain = transfer_data_beded.drop(['date_as_number','date'], axis=1)
max_beds = 1154 # maximal number of beds

def get_free_beds(beds_occupied):
    return max_beds - beds_occupied

transfer_strain.to_csv('transfer_strain.csv', header=True, index=False)