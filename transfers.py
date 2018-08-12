import pandas as pd
import datetime
import numpy as np


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
admpoint = admpoint[['STUDY_SUBJECT_DIGEST', 'in_dttm', 'out_dttm', 'adt_department_name', 'adt_room_id', 'adt_bed_id' ]]
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
surg_df['adt_room_id'] = np.repeat(0, s_length, axis=0)
surg_df['adt_bed_id'] = np.repeat (0, s_length, axis = 0)
surg_df['data_origin'] = np.repeat ('surg', s_length, axis = 0)
surg_df.rename(index=str, columns={'STUDY_SUBJECT_DIGEST': 'ptid'}, inplace=True)
surg_df.rename(index=str, columns={'case_start': 'in_dttm'}, inplace=True)
surg_df.rename(index=str, columns={'case_end': 'out_dttm'}, inplace=True)
surg_df.rename(index=str, columns={'prov_name': 'adt_department_name'}, inplace = True)

enc_df = encinfo[['STUDY_SUBJECT_DIGEST', 'case_start', 'dep_name']]
s_length = len(enc_df['case_start'])
enc_df['adt_room_id'] = np.repeat(0,s_length, axis =0)
enc_df['adt_bed_id'] = np.repeat(0,s_length, axis =0)
enc_df['case_end'] = np.repeat(0,s_length, axis =0)
enc_df['data_origin'] = np.repeat ('enc', s_length, axis = 0)
enc_df.rename(index=str, columns={'STUDY_SUBJECT_DIGEST': 'ptid'}, inplace=True)
enc_df.rename(index=str, columns={'case_start': 'in_dttm'}, inplace=True)
enc_df.rename(index=str, columns={'dep_name': 'adt_department_name'}, inplace = True)


#make dataframe containing all the information, then sort by patient id
#convert in_dttm to a datetime object to be able to sort by it later
full_info = pd.concat([admpoint, enc_df, surg_df], ignore_index=True)
full_info['in_dttm'] = pd.to_datetime(full_info['in_dttm'])

full_info = full_info.sort_values(by = ['ptid', 'in_dttm'], ascending = [True, True])

#adminfo contains demographic data for the patients
adminfo = pd.read_csv("ADM_INFO_aug.csv")

#add on the information from the other files that is needed in addition to the transfer data in admpoint
#pick the columns in the secondary files that are actually needed.
adminfo = adminfo[['adm_hosp', 'dis_hosp', 'specialty', 'admAge', 'STUDY_SUBJECT_DIGEST']]

# Set the index of the adminfo dataframe to the value we want to join to.
adminfo.set_index('STUDY_SUBJECT_DIGEST', drop=True, inplace=True)

# Join the columns in adminfo onto the admpoint dataframe based on patient ID.
full_info = full_info.join(adminfo, on='ptid', how='left')
print('joining')


#add on the information from the surgeries dataframe
surg_extra = surgeriesinfo[['asa_rating_c', 'STUDY_SUBJECT_DIGEST']]
surg_extra.set_index('STUDY_SUBJECT_DIGEST', drop=True, inplace=True)
admpoint = admpoint.join(surg_extra, on='ptid', how='left')

full_info.to_csv('full_info_all.csv', header=True, index=False)

## Remove event types we don't care about.
## Event types are: Admission, Transfer Out, Transfer In, Census, Patient Update, Discharge, Hospital Outpatient
#admpoint = admpoint[admpoint.evttype != 'Census'] # removes all census lines
#admpoint = admpoint[admpoint.evttype != 'Patient Update'] # removes all patient update lines

#print('deleting columns')
## Create the actual transfers - currently just a list of start positions.
## Making the two columns from and two.
#admpoint['from'] = admpoint['depname'] #duplicating the column but to make it the origin of the patient
#admpoint['to'] = admpoint['depname'] # duplicating it into the to column
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

