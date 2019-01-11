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
import datetime as dt


def get_separate_date_time(datetimeentry):
    print(datetimeentry)
    if type(datetimeentry) == float:
        return datetime.max
    else:
        #this returns the date in a format where the hours and days can be accessed eg d.year or d.minute
        separate_date_time = datetime.strptime(datetimeentry,"%Y-%m-%d %H:%M:%S")
        return separate_date_time


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


def get_previous_day(date):
    date_in_date_format = get_transfer_day(date)
    prev_day = datetime.date(date_in_date_format) - dt.timedelta(1)
    return prev_day



alltransfers = pd.read_csv("transfer_strain.csv")

#select transfers on specific dates with low breach percentage ie days where A&E was very full
transfers_lowed = alltransfers[alltransfers['breach_percentage'] < 0.6955]
#transfers_lowed.to_csv('transfers_lowedpercentage.csv')

#select patients for the day before, the day of and the day after a full A&E
#find the days with low ED percentage
transfers_lowed['day_of_transfer'] = transfers_lowed['transfer_dt'].map(get_transfer_day)
low_ed_perc_dates = transfers_lowed['day_of_transfer'].unique()
low_ed_prev_day = []
j=0
for i in low_ed_perc_dates:
    print(j,i)
    prev_day= get_previous_day(i)
    print(j,i, prev_day)
    j=j+1

print(low_ed_perc_dates)
print(low_ed_prev_day)






#select all the patients who at some point in their stay were in icu, nccu
#df = pd.DataFrame({'ptid': [1, 1, 1, 2, 2, 3, 3, 3, 3, 4], 'loc': ['a', 'b', 'c', 'a', 'c', 'a', 'b', 'a', 'b', 'd']})
#wards = {'ADD GENERAL ICU', 'ADD NEURO ICU'}
#icu_patient_ids = set(alltransfers.loc[alltransfers['from'].isin(wards)]['ptid'].unique())
#icu_patient_records = alltransfers.loc[alltransfers['ptid'].isin(icu_patient_ids)]
#icu_patient_records.to_csv('transfers_all_pts_icu.csv', header=True, index=False)

#specialities = {'Trauma', 'Orthopaedics'}
#t_o_patient_ids = set(alltransfers.loc[alltransfers['spec'].isin(specialities)]['ptid'].unique())
#t_o_patient_records = alltransfers.loc[alltransfers['ptid'].isin(t_o_patient_ids)]

#age_old = {'80','81','82','83','84','85','86','87','88','89','90','91','92','93','94','95'}
#t_o_old_patient_ids = set(t_o_patient_records.loc[t_o_patient_records['age'].isin(age_old)]['ptid'].unique())
#t_o_old_patient_records = t_o_patient_records.loc[t_o_patient_records['ptid'].isin(t_o_old_patient_ids)]
#t_o_old_patient_records.to_csv('transfers_old_to_1221.csv', header=True, index=False)

#asacategory= {'3','4'}
#asa34_patient_ids = set(alltransfers.loc[alltransfers['asa'].isin(asacategory)]['ptid'].unique())
#asa34_patient_records = alltransfers.loc[alltransfers['ptid'].isin(asa34_patient_ids)]
#asa34_patient_records.to_csv('transfers_all_pts_asa34.csv', header=True, index=False)


