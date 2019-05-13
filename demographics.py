#collect demographc information on the data
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
sorted_data = alltransfers.sort_values(['ptid', 'transfer_dt'])
num_patients = len(sorted_data['ptid'].unique())



groups = sorted_data.groupby('ptid')
print(groups)

all_transfers = []
num_bad_patients = 0
num_good_patients = 0
good_patient_data =[]
bad_patient_data = []

for ptid, group in groups:
    #patient_transfers, patient_data = get_patient_transfers(ptid, group)
    if patient_transfers is None:
        num_bad_patients += 1
        if patient_data is not None:
            bad_patient_data.append(patient_data)
    else:
        num_good_patients += 1
        good_patient_data.append(patient_transfers)
    i += 1
    if (i % 100) == 0:
        print("Finished %s of %s patients. Good patients: %s, bad patients: %s." % (i, num_patients, num_good_patients, num_bad_patients))

print("Good patients: %s. Bad patients: %s." % (num_good_patients, num_bad_patients))

good_patient_data.to_csv('good_patient_130519.csv', header=True, index=False)
bad_patient_data.to_csv('bad_patient_130519.csv', header = True, index=False)