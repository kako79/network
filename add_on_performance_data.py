import pandas as pd
from datetime import datetime
import numpy as np
from collections import deque, namedtuple

# adds on the ED performance data to the transfer file as a new column
def get_separate_date_time(datetimeentry):
    #print(datetimeentry)
    strdate = str(datetimeentry)
    fmt = "%Y-%m-%d %H:%M"
    try:
        d = datetime.strptime(strdate, fmt)
    except ValueError as v:
        ulr = len(v.args[0].partition('unconverted data remains: ')[2])
        if ulr:
            d = datetime.strptime(strdate[:-ulr], fmt)
        else:
            raise v

    if type(d) == float:
        return datetime.max
    else:
        # this returns the date in a format where the hours and days can be accessed eg d.year or d.minute
        dstr = str(d)
        separate_date_time = datetime.strptime(dstr, "%Y-%m-%d %H:%M:%S")
        return separate_date_time


def get_date_number(dt):
    return dt.year * 1000 + dt.month * 100 + dt.day


def get_date_number_from_string(date_time_entry):
    dt = get_separate_date_time(date_time_entry)
    return get_date_number(dt)


all_transfers = pd.read_csv("all_transfers_1110.csv")

#add on the information about the hospital state from the ED performance file
ed_performance = pd.read_csv("ed_performance_with_average.csv")
# need transfer date only in a separate column
all_transfers['transfer_date_number'] = all_transfers['transfer_dt'].map(get_date_number_from_string())
ed_performance['date'] = pd.to_datetime(ed_performance['day'], format='%d/%m/%Y')
ed_performance['date_number'] = ed_performance['date'].map(get_date_number)
ed_performance.set_index('date_number', drop=True, inplace=True)
all_transfers_with_performance = all_transfers.join(ed_performance, on='transfer_date_number', how='left')

all_t_with_performance = all_transfers_with_performance.drop(['transfer_date_number'], axis=1)



all_t_with_performance.to_csv('all_transfers_with_ed_perf.csv', header=True, index=False)
print('transfers file created')
##!!! finish of creating the transfers file
