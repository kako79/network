#read in full transfers file and then select specific patient groups to make subset graphs
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







alltransfers = pd.read_csv("all_transfers_1110.csv")



#df = pd.DataFrame({'ptid': [1, 1, 1, 2, 2, 3, 3, 3, 3, 4], 'loc': ['a', 'b', 'c', 'a', 'c', 'a', 'b', 'a', 'b', 'd']})
icu_patient_ids = set(alltransfers.loc[alltransfers['loc'] == 'icu']['ptid'].unique())
icu_patient_records = alltransfers.loc[alltransfers['ptid'].isin(icu_patient_ids)]


icu_patient_records.to_csv('transfers_all_pts_icu.csv', header=True, index=False)