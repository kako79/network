import pandas as pd
import datetime
import numpy as np
from collections import deque, namedtuple


#adds on the ED performance data to the transfer file as a new column

def get_separate_date_time(datetimeentry):
    print(datetimeentry)
    if type(datetimeentry) == float:
        return datetime.datetime.max
    else:
        #this returns the date in a format where the hours and days can be accessed eg d.year or d.minute
        separate_date_time = datetime.datetime.strptime(datetimeentry,"%Y-%m-%d %H:%M:%S")
        return separate_date_time


def get_date_only(date_time_entry):
    separated_date_entry = get_separate_date_time(date_time_entry)
    print(separated_date_entry)
    year_only = separated_date_entry.year
    month_only = separated_date_entry.month
    day_only = separated_date_entry.day
    date_only = datetime.datetime(year_only, month_only, day_only)
    return date_only.date()







all_transfers = pd.read_csv("all_transfers_1110.csv")

#add on the information about the hospital state from the ED performance file
ed_performance = pd.read_csv("ed_perfomance_with_average.csv")
# need transfer date only in a separate column
all_transfers['transfer_date_only'] = get_date_only(all_transfers['transfer_dt'])
ed_performance.set_index('date', drop = True, inplace = True)
all_transfers_with_performance = ed_performance.join(all_transfers, on='transfer_date_only', how='left')

all_t_with_performance = all_transfers_with_performance.drop(['transfer_date_only'], axis=1)



all_t_with_performance.to_csv('all_transfers_with_ed_perf.csv', header=True, index=False)
print('transfers file created')
##!!! finish of creating the transfers file
