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


def get_previous_day(date):
    date_in_date_format = get_transfer_day(date)
    prev_day = datetime.date(date_in_date_format) - dt.timedelta(1)
    prev_day = prev_day.strftime('%Y-%m-%d')
    return prev_day

def get_next_day(date_n):
    date_in_date_format = get_transfer_day(date_n)
    next_day = datetime.date(date_in_date_format) + dt.timedelta(1)
    next_day = next_day.strftime('%Y-%m-%d')
    return next_day


alltransfers = pd.read_csv("transfer_strain.csv")
#select all adult patients 16 and above
adult_transfers= alltransfers.loc[alltransfers['age']>16]
adult_transfers.to_csv('all_adult_transfers.csv')
#select transfers on specific dates with low breach percentage ie days where A&E was very full
transfers_lowed = alltransfers[alltransfers['breach_percentage'] < 0.6955]
transfers_lowed = adult_transfers[adult_transfers['breach_percentage'] < 0.6955]
#transfers_lowed.to_csv('transfers_lowedpercentage.csv')

#select patients for the day before, the day of and the day after a full A&E
#find the days with low ED percentage
print(transfers_lowed['transfer_dt'].map(get_transfer_day))
print(check)
transfers_lowed['day_of_transfer'] = transfers_lowed['transfer_dt'].map(get_transfer_day)
low_ed_perc_dates = transfers_lowed['day_of_transfer'].unique()
low_ed_prev_day = []
low_ed_next_day = []
for i in low_ed_perc_dates:
    prev_day = get_previous_day(i)
    next_day = get_next_day(i)
    low_ed_prev_day.append(prev_day)
    low_ed_next_day.append(next_day)

#import pdb; pdb.set_trace()
all_dates_low_ed = set(low_ed_prev_day + list(low_ed_perc_dates) + low_ed_next_day)
alltransfers['day_of_transfer'] = alltransfers['transfer_dt'].map(get_transfer_day)
#print(alltransfers['day_of_transfer'])
transfers_around_low_ed_ind = adult_transfers[adult_transfers['day_of_transfer'].isin(all_dates_low_ed)]
print(len(transfers_around_low_ed_ind))
transfers_around_low_ed_ind.to_csv('transfers_around_low_ed_perc.csv')

#select transfers on specific dates with low breach percentage ie days where A&E was very empty
transfers_highed = alltransfers[alltransfers['breach_percentage'] >0.9685]
transfers_highed = adult_transfers[adult_transfers['breach_percentage'] >0.9685]
#transfers_lowed.to_csv('transfers_lowedpercentage.csv')

#select patients for the day before, the day of and the day after a full A&E
#find the days with low ED percentage
transfers_highed['day_of_transfer'] = transfers_highed['transfer_dt'].map(get_transfer_day)
high_ed_perc_dates = transfers_highed['day_of_transfer'].unique()
high_ed_prev_day = []
high_ed_next_day = []
for i in high_ed_perc_dates:
    prev_day = get_previous_day(i)
    next_day = get_next_day(i)
    high_ed_prev_day.append(prev_day)
    high_ed_next_day.append(next_day)

#import pdb; pdb.set_trace()
all_dates_high_ed = set(high_ed_prev_day + list(high_ed_perc_dates) + high_ed_next_day)
#print(alltransfers['day_of_transfer'])
transfers_around_high_ed_ind = adult_transfers[adult_transfers['day_of_transfer'].isin(all_dates_high_ed)]
print(len(transfers_around_high_ed_ind))
transfers_around_high_ed_ind.to_csv('transfers_around_high_ed_perc.csv')




#select all the patients who at some point in their stay were in icu, nccu
#df = pd.DataFrame({'ptid': [1, 1, 1, 2, 2, 3, 3, 3, 3, 4], 'loc': ['a', 'b', 'c', 'a', 'c', 'a', 'b', 'a', 'b', 'd']})
#wards = {'ADD GENERAL ICU', 'ADD NEURO ICU', }
#icu_patient_ids = set(adult_transfers.loc[adult_transfers['from'].isin(wards)]['ptid'].unique())
#icu_patient_records = adult_transfers.loc[adult_transfers['ptid'].isin(icu_patient_ids)]
#icu_patient_records.to_csv('transfers_all_icu.csv', header=True, index=False)

#all adult HDU or ICU patients
wards = {'ADD GENERAL ICU', 'ADD NEURO ICU', 'ADD D4 IDA UNIT', 'ADD CORONARY CARE UNIT', 'ADD TRANSPLANT HDU'}
icu_patient_ids = set(adult_transfers.loc[adult_transfers['from'].isin(wards)]['ptid'].unique())
icu_patient_records = adult_transfers.loc[adult_transfers['ptid'].isin(icu_patient_ids)]
icu_patient_records.to_csv('transfers_icu.csv', header=True, index=False)

#select the patients who got to HDU but on busy and non busy days
#busy

wards = {'ADD GENERAL ICU', 'ADD NEURO ICU', 'ADD D4 IDA UNIT', 'ADD CORONARY CARE UNIT', 'ADD TRANSPLANT HDU'}
icu_patient_ids = set(transfers_around_low_ed_ind.loc[transfers_around_low_ed_ind['from'].isin(wards)]['ptid'].unique())
icu_patient_records = transfers_around_low_ed_ind.loc[transfers_around_low_ed_ind['ptid'].isin(icu_patient_ids)]
icu_patient_records.to_csv('transfers_lowed_hdu_2309.csv', header=True, index=False)

#calm ED
wards = {'ADD GENERAL ICU', 'ADD NEURO ICU', 'ADD D4 IDA UNIT', 'ADD CORONARY CARE UNIT', 'ADD TRANSPLANT HDU'}
icu_patient_ids = set(transfers_around_high_ed_ind.loc[transfers_around_high_ed_ind['from'].isin(wards)]['ptid'].unique())
icu_patient_records = transfers_around_high_ed_ind.loc[transfers_around_high_ed_ind['ptid'].isin(icu_patient_ids)]
icu_patient_records.to_csv('transfers_high_hdu_2309.csv', header=True, index=False)




specialities = {'Trauma', 'Orthopaedics'}
t_o_patient_ids = set(alltransfers.loc[alltransfers['spec'].isin(specialities)]['ptid'].unique())
t_o_patient_records = alltransfers.loc[alltransfers['ptid'].isin(t_o_patient_ids)]

trauma_spec={'Trauma'}
trauma_ids = set(alltransfers.loc[alltransfers['spec'].isin(trauma_spec)]['ptid'].unique())
trauma_records = alltransfers.loc[alltransfers['ptid'].isin(trauma_ids)]
trauma_adult_records = trauma_records.loc[trauma_records['age'] >16]
trauma_adult_records.to_csv('transfers_trauma_adult.csv', header = True, index = False)

#age_old = {'80','81','82','83','84','85','86','87','88','89','90','91','92','93','94','95'}
#t_o_old_patient_ids = set(t_o_patient_records.loc[t_o_patient_records['age'].isin(age_old)]['ptid'].unique())
#t_o_old_patient_records = t_o_patient_records.loc[t_o_patient_records['ptid'].isin(t_o_old_patient_ids)]
#t_o_old_patient_records.to_csv('transfers_old_tando.csv', header=True, index=False)

#ASA 3 and 4 adult patients
#asacategory= {'3','4'}
#asa34_adult_ids = set(adult_transfers.loc[adult_transfers['asa'].isin(asacategory)]['ptid'].unique())
#asa34_adult_records = adult_transfers.loc[adult_transfers['ptid'].isin(asa34_adult_ids)]
#asa34_adult_records.to_csv('transfers_adult_asa34.csv', header=True, index=False)

#paeds patients
#paeds_transfers = alltransfers.loc[alltransfers['age'] < 16]
#paeds_transfers.to_csv('transfers_paeds_all.csv', header=True, index=False)


