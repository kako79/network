import pandas as pd
from datetime import datetime
import numpy as np
from collections import deque, namedtuple

def get_separate_date_time(datetimeentry):
    print(datetimeentry)
    if type(datetimeentry) == float:
        return datetime.datetime.max
    else:
        #this returns the date in a format where the hours and days can be accessed eg d.year or d.minute
        separate_date_time = datetime.datetime.strptime(datetimeentry,"%Y-%m-%d %H:%M:%S")
        return separate_date_time


#admpoint contains the transfers of all the patients
admpoint = pd.read_csv("ADM_POINT_aug.csv")
# keep the columns actually needed
admpoint = admpoint[['STUDY_SUBJECT_DIGEST', 'in_dttm', 'out_dttm', 'adt_department_name']]
s_length = len(admpoint['in_dttm'])
admpoint['data_origin'] = np.repeat('adm', s_length, axis=0)
# Rename the 'STUDY_SUBJECT_DIGEST' column to 'ptid'.
admpoint.rename(index=str, columns={'STUDY_SUBJECT_DIGEST': 'ptid'}, inplace=True)




#surgeriesinfo contains details about the surgery
surgeriesinfo = pd.read_csv("SURGERIES_aug.csv")
encinfo = pd.read_csv("ENC_POINT_aug.csv")

print('reading in done')
#make the new files into df that look the same so that they can be appended onto admpoint

surg_df= surgeriesinfo[['STUDY_SUBJECT_DIGEST', 'case_start', 'case_end', 'prov_name']]
s_length = len(surg_df['case_start']) #length of series that needs to be added into the new columns
#surg_df['adt_room_id'] = np.repeat(0, s_length, axis=0)
#surg_df['adt_bed_id'] = np.repeat (0, s_length, axis=0)
surg_df['data_origin'] = np.repeat ('surg', s_length, axis = 0)
surg_df.rename(index=str, columns={'STUDY_SUBJECT_DIGEST': 'ptid'}, inplace=True)
surg_df.rename(index=str, columns={'case_start': 'in_dttm'}, inplace=True)
surg_df.rename(index=str, columns={'case_end': 'out_dttm'}, inplace=True)
surg_df.rename(index=str, columns={'prov_name': 'adt_department_name'}, inplace = True)

enc_df = encinfo[['STUDY_SUBJECT_DIGEST', 'at_time','enctype', 'dep_name']]
#replace the empty entries in the department name with the encounter type eg operation.
empty_indices = enc_df['dep_name'] == ''
enc_df.loc[empty_indices, 'dep_name'] = enc_df.loc[empty_indices, 'enctype']
enc_df = enc_df[['STUDY_SUBJECT_DIGEST', 'at_time', 'dep_name']]
s_length = len(enc_df['at_time'])
enc_df['out_dttm'] = np.repeat(1,s_length, axis =0)
enc_df['data_origin'] = np.repeat ('enc', s_length, axis = 0)
enc_df.rename(index=str, columns={'STUDY_SUBJECT_DIGEST': 'ptid'}, inplace=True)
enc_df.rename(index=str, columns={'at_time': 'in_dttm'}, inplace=True)
enc_df.rename(index=str, columns={'dep_name': 'adt_department_name'}, inplace = True)


#make dataframe containing all the information, then sort by patient id
#convert in_dttm to a datetime object to be able to sort by it later
full_info = pd.concat([admpoint, enc_df, surg_df], ignore_index=True)
full_info['in_dttm'] = pd.to_datetime(full_info['in_dttm'])
full_info['out_dttm'] = pd.to_datetime(full_info['out_dttm'])
full_info = full_info.sort_values(by = ['ptid', 'in_dttm'], ascending = [True, True])
full_info.reset_index(drop=True, inplace=True)

#add on the information from the other files that is needed in addition to the transfer data in admpoint
#adminfo contains demographic data for the patients
adminfo = pd.read_csv("ADM_INFO_aug.csv")
#pick the columns in the secondary files that are actually needed.
adminfo = adminfo[['adm_hosp', 'dis_hosp', 'specialty', 'admAge', 'STUDY_SUBJECT_DIGEST']]
# Set the index of the adminfo dataframe to the value we want to join to.
adminfo.set_index('STUDY_SUBJECT_DIGEST', drop=True, inplace=True)
# Join the columns in adminfo onto the admpoint dataframe based on patient ID.
full_info = full_info.join(adminfo, on='ptid', how='left')
print('joining on adminfo')


#add on the information from the surgeries dataframe
surg_extra = surgeriesinfo[['asa_rating_c', 'STUDY_SUBJECT_DIGEST']]
surg_extra.set_index('STUDY_SUBJECT_DIGEST', drop=True, inplace=True)
full_info = full_info.join(surg_extra, on='ptid', how='left')
full_info.to_csv('full_info_all.csv', header=True, index=False)

print('full_info created')
## Remove event types we don't care about.
## Event types are: Admission, Transfer Out, Transfer In, Census, Patient Update, Discharge, Hospital Outpatient
#admpoint = admpoint[admpoint.evttype != 'Census'] # removes all census lines
#admpoint = admpoint[admpoint.evttype != 'Patient Update'] # removes all patient update lines

# need to create the transfers list with added in rows when a patient goes back to a ward after an investigation
#first group the data into individual patients data to be able to figure out any missing rows

grouped = full_info.groupby('ptid')

#'ptid', 'transfer_dt', 'from', 'to', 'dt_adm', 'dt_dis', 'spec', 'age', 'asa'
##!!! starting the transfers code

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
        transfer_list.append({'ptid': ptid, 'transfer_dt': loc.dt_out, 'from': loc.name, 'to': next_loc.name, 'dt_adm': loc.dt_adm, 'dt_dis': loc.dt_dis, 'spec': loc.spec, 'age': loc.age, 'asa': loc.asa})

    return transfer_list


def get_patient_transfers(ptid, patient_data):
    # The stack will contain the previous (location, entry_time, exit_time) tuples.
    location_stack = []
    transfer_list = []

    for i, row in patient_data.iterrows():
        loc = row['adt_department_name']
        dt_in = row['in_dttm']
        dt_out = row['out_dttm']
        dt_adm = row['adm_hosp']
        dt_dis = row['dis_hosp']
        spec = row['specialty']
        age = row['admAge']
        asa = row['asa_rating_c']

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
                {'ptid': ptid, 'transfer_dt': new_loc.dt_in, 'from': current_loc.name, 'to': new_loc.name, 'dt_adm': new_loc.dt_adm, 'dt_dis': new_loc.dt_dis, 'spec': new_loc.spec, 'age': new_loc.age, 'asa': new_loc.asa})

    # In case we are inside a bunch of nested locations, we now need to transfer the patient out of them.
    transfer_list += get_transfers_out(ptid, location_stack, datetime.max)

    # Finally we need to discharge the patient.
    last_loc = location_stack[-1]
    transfer_list.append({'ptid': ptid, 'transfer_dt': last_loc.dt_out, 'from': last_loc.name, 'to': 'discharge','dt_adm': last_loc.dt_adm, 'dt_dis': last_loc.dt_dis, 'spec': last_loc.spec, 'age': last_loc.age, 'asa': last_loc.asa })

    # Return a DataFrame with the transfers.
    return pd.DataFrame(columns=['ptid', 'transfer_dt', 'from', 'to', 'dt_adm', 'dt_dis', 'spec', 'age', 'asa'], data=transfer_list)


def get_transfers(location_data: pd.DataFrame):
    sorted_data = location_data.sort_values(['ptid', 'in_dttm'])
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

all_transfers = get_transfers(full_info)
all_transfers.to_csv('all_transfers_file.csv', header=True, index=False)
print('transfers file created')
##!!! finish of creating the transfers file
























## Create the actual transfers - currently just a list of start positions.
## Making the two columns from and to.
#full_info['from'] = full_info['adt_department_name'] #duplicating the column but to make it the origin of the patient
#full_info['to'] = full_info['adt_department_name'] # duplicating it into the to column
#print('duplicated the columns')

###loops through all the patient ids to get the data for each one
##list_of_patient_data = [get_data_for_patient(patientid, admpoint) for patientid in admpoint['ptid'].unique()]
##print('lopiing through patient id')

### Combine together all the dataframes.
##def append_dataframes(d1, d2):
##    return d1.append(d2)
##combined_patient_data = functools.reduce(append_dataframes, list_of_patient_data)

##do the above for all the data together to save time
#admpoint['extraid'] = admpoint['ptid'].shift(-1)
##admpoint['extraid'] = admpoint['extraid'].shift(-1)
#admpoint['to'] = admpoint['to'].shift(-1)  # shifting the to column up one so that the value from below is in that slot.
##print(patient_data.iloc[0].name)

##the rows where the patient id changes are discharge rows
#admpoint.loc[admpoint[admpoint['ptid'] != admpoint['extraid']].index, 'to'] = 'discharge'

### Make a column that has True if the location changed.
##admpoint['transfer'] = admpoint['from'] != admpoint['to']

## Drop the rows where the to and from is the same as they are not real transfers.
#admpoint.drop(admpoint[admpoint['to'] == admpoint['from']].index, axis=0, inplace=True)

##drop the rows where information is duplicated
#admpoint.drop(admpoint[admpoint['effective_time'] == admpoint['effective_time'].shift(-1)].index, axis=0, inplace=True)


##renaming the dataframe
#combined_patient_data = admpoint

##separate out the date and time in the transfer data for both effective time (which is the transfer date) and admission date and discharge date.
#list_of_separate_transfer_date_time = [get_separate_date_time(combined_date_time) for combined_date_time in combined_patient_data['effective_time']]
#combined_patient_data['transfer_time'] = list_of_separate_transfer_date_time
#print('dates separated')
#print('admissions')
#list_of_separate_admission_date_time = [get_separate_date_time(combined_date_time) for combined_date_time in combined_patient_data['adm_hosp']]
#combined_patient_data['admission_time'] = list_of_separate_admission_date_time
#print('discharges')
#list_of_separate_discharge_date_time = [get_separate_date_time(combined_date_time) for combined_date_time in combined_patient_data['dis_hosp']]
#combined_patient_data['discharge_time'] = list_of_separate_discharge_date_time


##output the data developed.
#print(combined_patient_data)
#combined_patient_data = combined_patient_data.drop(['adm_hosp', 'dis_hosp'], axis=1)
#combined_patient_data.to_csv('combined_data.csv', header=True, index=False)

