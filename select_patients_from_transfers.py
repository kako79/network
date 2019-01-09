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







alltransfers = pd.read_csv("transfers_2018_12_21.csv")


#select all the patients who at some point in their stay were in icu, nccu
#df = pd.DataFrame({'ptid': [1, 1, 1, 2, 2, 3, 3, 3, 3, 4], 'loc': ['a', 'b', 'c', 'a', 'c', 'a', 'b', 'a', 'b', 'd']})
#wards = {'ADD GENERAL ICU', 'ADD NEURO ICU'}
#icu_patient_ids = set(alltransfers.loc[alltransfers['from'].isin(wards)]['ptid'].unique())
#icu_patient_records = alltransfers.loc[alltransfers['ptid'].isin(icu_patient_ids)]
#icu_patient_records.to_csv('transfers_all_pts_icu.csv', header=True, index=False)

specialities = {'Trauma', 'Orthopaedics'}
t_o_patient_ids = set(alltransfers.loc[alltransfers['spec'].isin(specialities)]['ptid'].unique())
t_o_patient_records = alltransfers.loc[alltransfers['ptid'].isin(t_o_patient_ids)]

age_old = {'80','81','82','83','84','85','86','87','88','89','90','91','92','93','94','95'}
t_o_old_patient_ids = set(t_o_patient_records.loc[t_o_patient_records['age'].isin(age_old)]['ptid'].unique())
t_o_old_patient_records = t_o_patient_records.loc[t_o_patient_records['ptid'].isin(t_o_old_patient_ids)]
t_o_old_patient_records.to_csv('transfers_old_to_1221.csv', header=True, index=False)

#asacategory= {'3','4'}
#asa34_patient_ids = set(alltransfers.loc[alltransfers['asa'].isin(asacategory)]['ptid'].unique())
#asa34_patient_records = alltransfers.loc[alltransfers['ptid'].isin(asa34_patient_ids)]
#asa34_patient_records.to_csv('transfers_all_pts_asa34.csv', header=True, index=False)
