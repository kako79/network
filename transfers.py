import pandas as pd
import datetime


def get_separate_date_time(datetimeentry):
    if datetimeentry == '':
        return datetime.datetime.max
    else:
        #this returns the date in a format where the hours and days can be accessed eg d.year or d.minute
        separate_date_time = datetime.datetime.strptime(datetimeentry,"%Y-%m-%d %H:%M:%S")
        return separate_date_time


#admpoint contains the transfers of all the patients
admpoint = pd.read_csv("ADM_POINT.csv")
#subADMPOINT = ADMPOINT[['depname','evttime', '']]

# Rename the 'STUDY_SUBJECT_DIGEST' column to 'ptid'.
admpoint.rename(index=str, columns={'STUDY_SUBJECT_DIGEST': 'ptid'}, inplace=True)

#adminfo contains demographic data for the patients
adminfo = pd.read_csv("ADM_INFO.csv")


#surgeriesinfo contains details about the surgery
surgeriesinfo = pd.read_csv("SURGERIES_INFO_red.csv")

print('reading in done')

#add on the information from the other files that is needed in addition to the transfer data in admpoint
#pick the columns in the secondary files that are actually needed.
adminfo = adminfo[['adm_hosp', 'dis_hosp', 'specialty', 'admAge', 'STUDY_SUBJECT_DIGEST']]

# Set the index of the adminfo dataframe to the value we want to join to.
adminfo.set_index('STUDY_SUBJECT_DIGEST', drop=True, inplace=True)

# Join the columns in adminfo onto the admpoint dataframe based on patient ID.
admpoint = admpoint.join(adminfo, on='ptid', how='left')
print('joining')

#add on the information from the surgeries dataframe
surgeriesinfo = surgeriesinfo[['asa_rating_c', 'STUDY_SUBJECT_DIGEST']]
surgeriesinfo.set_index('STUDY_SUBJECT_DIGEST', drop=True, inplace=True)
admpoint = admpoint.join(surgeriesinfo, on='ptid', how='left')


# Remove event types we don't care about.
# Event types are: Admission, Transfer Out, Transfer In, Census, Patient Update, Discharge, Hospital Outpatient
#admpoint = admpoint[admpoint.evttype != 'Census'] # removes all census lines
#admpoint = admpoint[admpoint.evttype != 'Patient Update'] # removes all patient update lines

print('deleting columns')
# Create the actual transfers - currently just a list of start positions.
# Making the two columns from and two.
admpoint['from'] = admpoint['depname'] #duplicating the column but to make it the origin of the patient
admpoint['to'] = admpoint['depname'] # duplicating it into the to column
print('duplicated the columns')

##loops through all the patient ids to get the data for each one
#list_of_patient_data = [get_data_for_patient(patientid, admpoint) for patientid in admpoint['ptid'].unique()]
#print('lopiing through patient id')

## Combine together all the dataframes.
#def append_dataframes(d1, d2):
#    return d1.append(d2)
#combined_patient_data = functools.reduce(append_dataframes, list_of_patient_data)

#do the above for all the data together to save time
admpoint['extraid'] = admpoint['ptid'].shift(-1)
#admpoint['extraid'] = admpoint['extraid'].shift(-1)
admpoint['to'] = admpoint['to'].shift(-1)  # shifting the to column up one so that the value from below is in that slot.
#print(patient_data.iloc[0].name)

#the rows where the patient id changes are discharge rows
admpoint.loc[admpoint[admpoint['ptid'] != admpoint['extraid']].index, 'to'] = 'discharge'

# Make a column that has True if the location changed.
admpoint['transfer'] = admpoint['from'] != admpoint['to']

# Drop the rows where the to and from is the same as they are not real transfers.
admpoint.drop(admpoint[admpoint['to'] == admpoint['from']].index, axis=0, inplace=True)

#renaming the dataframe
combined_patient_data = admpoint

#separate out the date and time in the transfer data for both effective time (which is the transfer date) and admission date and discharge date.
list_of_separate_transfer_date_time = [get_separate_date_time(combined_date_time) for combined_date_time in combined_patient_data['effective_time']]
combined_patient_data['transfer_time'] = list_of_separate_transfer_date_time
print('dates separated')

list_of_separate_admission_date_time = [get_separate_date_time(combined_date_time) for combined_date_time in combined_patient_data['adm_hosp']]
combined_patient_data['admission_time'] = list_of_separate_admission_date_time

list_of_separate_discharge_date_time = [get_separate_date_time(combined_date_time) for combined_date_time in combined_patient_data['dis_hosp']]
combined_patient_data['discharge_time'] = list_of_separate_discharge_date_time


#output the data developed.
print(combined_patient_data)
combined_patient_data = combined_patient_data.drop(['adm_hosp', 'dis_hosp', 'extraid'], axis=1)
combined_patient_data.to_csv('combined_data.csv', header=True, index=False)
