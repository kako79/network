from collections import deque, namedtuple
from datetime import datetime
import pandas as pd

#making a named tuple to store the current transfer tdata
location = namedtuple("location", ["name","dt_in","dt_out","dt_adm","dt_dis","spec","age","asa"])


def get_transfers_out(ptid, location_stack, current_dt):
    # In the case of nested locations, this function generates transfers out of those locations to the
    # top-level location.

    # First check if the patient is still in the most recent location at the specified time.
    # If this is true then there are no transfers happening.
    if (len(location_stack) <= 1) or (location_stack[-1].dt_out >= current_dt):
        return []

    transfer_list = []

    # Pop locations off the stack until we find one that the patient is still in at the current time,
    # or until there are no more locations left.
    # We always leave at least one location on the stack because this function does not handle patient discharge.
    while (len(location_stack) > 1) and (location_stack[-1].dt_out < current_dt):
        loc = location_stack.pop()
        next_loc = location_stack[-1]
        transfer_list.append({'ptid': ptid, 'transfer_dt': loc.dt_out, 'from': loc.name, 'to': next_loc.name, 'dt_adm': dt_adm, 'dt_dis': dt_dis, 'spec': spec, 'age': age, 'asa': asa})

    return transfer_list


def get_patient_transfers(ptid, patient_data):
    # The stack will contain the previous (location, entry_time, exit_time) tuples.
    location_stack = []
    transfer_list = []

    for i, row in patient_data.iterrows():
        loc = row['loc']
        dt_in = row['dt_in']
        dt_out = row['dt_out']
        dt_adm = row['dt_adm']
        dt_dis = row['dt_dis']
        spec = row['spec']
        age = row['age']
        asa = row['asa']

        new_loc = location(loc, dt_in, dt_out, dt_adm, dt_dis, spec, age, asa)

        # If the stack is empty then this is the first location for the patient and we won't
        # be adding any transfers yet.
        if len(location_stack) == 0:
            location_stack.append(new_loc)
        else:
            # If there are nested locations that the patient is no longer in, we need to transfer out of them.
            transfer_list += get_transfers_out(ptid, location_stack, new_loc.dt_in)

            current_loc = location_stack[-1]

            # Check if the patient entered the next location after leaving the current location.
            # If so, this is a normal transfer, and we need to pop the current location off the stack
            # so it can be replaced by the new location.
            if new_loc.dt_in >= current_loc.dt_out:
                # This is a normal transfer.
                # Pop the previous location off the stack because we've left it.
                location_stack.pop()

            # The patient is now in the new location so put it on top of the stack.
            location_stack.append(new_loc)

            # Add a transfer from the previous location to the new location.
            transfer_list.append(
                {'ptid': ptid, 'transfer_dt': new_loc.dt_in, 'from': current_loc.name, 'to': new_loc.name, 'dt_adm': dt_adm, 'dt_dis': dt_dis, 'spec': spec, 'age': age, 'asa': asa})

    # In case we are inside a bunch of nested locations, we now need to transfer the patient out of them.
    transfer_list += get_transfers_out(ptid, location_stack, datetime.max)

    # Finally we need to discharge the patient.
    last_loc = location_stack[-1]
    transfer_list.append({'ptid': ptid, 'transfer_dt': last_loc.dt_out, 'from': last_loc.name, 'to': 'discharge','dt_adm': dt_adm, 'dt_dis': dt_dis, 'spec': spec, 'age': age, 'asa': asa })

    # Return a DataFrame with the transfers.
    return pd.DataFrame(columns=['ptid', 'transfer_dt', 'from', 'to', 'dt_adm', 'dt_dis', 'spec', 'age', 'asa'], data=transfer_list)


def get_transfers(location_data: pd.DataFrame):
    sorted_data = location_data.sort_values(['ptid', 'dt_in'])
    groups = sorted_data.groupby('ptid')
    all_transfers = None
    print(all_transfers)
    for ptid, group in groups:
        patient_transfers = get_patient_transfers(ptid, group)
        if all_transfers is None:
            all_transfers = patient_transfers
        else:
            all_transfers = all_transfers.append(patient_transfers)
    print(all_transfers)
    return all_transfers


df = pd.DataFrame({
    'ptid': [1, 1, 1, 2, 2],
    'loc': ['a', 'b', 'c', 'a', 'b'],
    'dt_in': ["2018-01-01 10:00", "2018-01-01 11:00", "2018-01-01 12:00", "2018-01-01 16:00", "2018-01-01 17:00"],
    'dt_out': ["2018-01-01 15:00", "2018-01-01 14:00", "2018-01-01 13:00", "2018-01-01 16:45", "2018-01-01 18:00"],
    'adm_time':["2018-01-01 01:00","2018-01-01 01:00","2018-01-01 01:00","2018-01-01 01:00","2018-01-01 01:00"]})
df['dt_in'] = pd.to_datetime(df['dt_in'])
df['dt_out'] = pd.to_datetime(df['dt_out'])

get_transfers(df)
print(all_transfers)