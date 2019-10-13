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
import datetime as dt

alltransfers = pd.read_csv("transfer_strain.csv")
#select all adult patients 16 and above
adult_transfers= alltransfers.loc[alltransfers['age']>16]
adult_transfers.to_csv('all_adult_transfers.csv')

#keep only the columns that are needed
tx_adult = adult_transfers[['from','to','ptid']]

tx = tx_adult.copy()
tx['transfer'] = tx['from'] + ' -> ' + tx['to']
tx = tx.drop(columns=['from', 'to'])
tx_sorted = tx.sort_values(by=['ptid', 'transfer']).reset_index(drop=True)
tx_sorted['count'] = pd.Series(np.ones(shape=len(tx_sorted)))
tx_grouped = tx_sorted.groupby(by=['ptid', 'transfer']).count()

#the unstack puts the named index (1) into separate columns, here the grouped bit had two indeces (ptid and transfer (which is the set of wards from and to))
tx_matrix = tx_grouped.unstack(1).fillna(0)

#save to csv
tx_matrix.to_csv('transfers_matrix.csv')