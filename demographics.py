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
import statistics

allpatients = pd.read_csv("ADM_INFO_aug.csv")

reduced_data = allpatients[['STUDY_SUBJECT_DIGEST','specialty','admAge']]
reduced_data.rename(index=str, columns={'STUDY_SUBJECT_DIGEST': 'ptid'}, inplace=True)
reduced_data = reduced_data.loc[reduced_data['admAge']>16]
print("all admissions", len(reduced_data['admAge']))
grouped_data = reduced_data.groupby(['specialty']).count()
grouped_data.reset_index()
print(grouped_data)



#spec_count['adm_specialty'] =
print( reduced_data['specialty'].unique())

#spec_count['count'] = reduced_data['specialty'].value_counts()


#surgeriesinfo = pd.read_csv("SURGERIES_aug.csv")
#surg_extra = surgeriesinfo[['asa_rating_c', 'STUDY_SUBJECT_DIGEST']]

#replace the empty asa entries with
#surg_extra['asa_rating_c'] = surg_extra['asa_rating_c'].replace("", np.nan, regex=True)
#surg_extra['asa_rating_c'] = surg_extra['asa_rating_c'].fillna(0)

#surg_extra.set_index('STUDY_SUBJECT_DIGEST', drop=True, inplace=True)


#all_demographics_data = reduced_data.join(surg_extra, on='ptid', how='left')

#unique_pt_set = set(all_demographics_data['ptid'].unique())

#unique_demographics=[]
#for n in unique_pt_set:
#    unique_row = all_demographics_data[all_demographics_data['ptid'] == n].iloc[0]
#    unique_demographics.append({'ptid':unique_row.ptid, 'age': unique_row.admAge, 'asa' : unique_row.asa_rating_c})

#df_demo= all_demographics_data.set_index('ptid')
#df_demo_first = df_demo.sort_index().groupby(level=0).first()


#print(df_demo_first)
#unique_demographics = all_demographics_data.loc[all_demographics_data['ptid'].isin(unique_demographics_set)]


#mean_age = statistics.mean(df_demo_first['admAge'])
#print(mean_age)
#print(len(df_demo_first['admAge']))
#print('mean ASA', statistics.mean(df_demo_first['asa_rating_c']))
#df_demo_first.to_csv('demographics_data.csv', header=True, index=False)


#sorted_data = alltransfers.sort_values(['ptid', 'transfer_dt'])
#num_patients = len(sorted_data['ptid'].unique())
#print("number of patient", num_patients)

#ptids_unique = sorted_data['ptid'].unique()
#ages_ptids = alltransfers.loc[ptids_unique]['age']
#ASA_ptids = alltransfers.loc[ptids_unique]['age']


#mean_age = statistics.mean()



#groups = sorted_data.groupby('ptid')
#print(groups)

#all_transfers = []
#num_bad_patients = 0
#num_good_patients = 0
#good_patient_data =[]
#bad_patient_data = []

#for ptid, group in groups:
#    #patient_transfers, patient_data = get_patient_transfers(ptid, group)
#    if patient_transfers is None:
 #       num_bad_patients += 1
#        if patient_data is not None:
#            bad_patient_data.append(patient_data)
#    else:
#        num_good_patients += 1
#        good_patient_data.append(patient_transfers)
#    i += 1
#    if (i % 100) == 0:
#        print("Finished %s of %s patients. Good patients: %s, bad patients: %s." % (i, num_patients, num_good_patients, num_bad_patients))

#print("Good patients: %s. Bad patients: %s." % (num_good_patients, num_bad_patients))


#good_patient_data.to_csv('good_patient_130519.csv', header=True, index=False)
#bad_patient_data.to_csv('bad_patient_130519.csv', header = True, index=False)