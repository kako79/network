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


#select all the patients who at some point in their stay were in icu, nccu
#df = pd.DataFrame({'ptid': [1, 1, 1, 2, 2, 3, 3, 3, 3, 4], 'loc': ['a', 'b', 'c', 'a', 'c', 'a', 'b', 'a', 'b', 'd']})
wards = {'ADD GENERAL ICU', 'ADD NEURO ICU'}
icu_patient_ids = set(alltransfers.loc[alltransfers['from'].isin(wards)]['ptid'].unique())
icu_patient_records = alltransfers.loc[alltransfers['ptid'].isin(icu_patient_ids)]
icu_patient_records.to_csv('transfers_all_pts_icu.csv', header=True, index=False)

specialities = {'General Surgery'}
gensurg_patient_ids = set(alltransfers.loc[alltransfers['spec'].isin(specialities)]['ptid'].unique())
gensurg_patient_records = alltransfers.loc[alltransfers['ptid'].isin(gensurg_patient_ids)]

gensurg_patient_records.to_csv('transfers_all_pts_gensurg.csv', header=True, index=False)

asacategory= {'1','2'}
asa12_patient_ids = set(alltransfers.loc[alltransfers['asa'].isin(asacategory)]['ptid'].unique())
asa12_patient_records = alltransfers.loc[alltransfers['ptid'].isin(asa12_patient_ids)]
asa12_patient_records.to_csv('transfers_all_pts_asa12.csv', header=True, index=False)
