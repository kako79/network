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

#file containing all the categorised and uncategorised locations
transfers = pd.read_csv("cat_data_journeys.csv")

#make columns that allow to check later whether this is a new location

transfers['combined_from'] = transfers['from_cat'] +  transfers['from']
transfers['combined_to'] = transfers['to_cat'] + transfers['to']
transfers = transfers.drop(['from','to'], axis=1) # we dont need these anymore

#Select all the patients who at some point in their stay were in theatre
wards = {'theatre'}
theatre_patient_ids = set(transfers.loc[transfers['from_cat'].isin(wards)]['ptid'].unique())
theatre_patient_records = transfers.loc[transfers['ptid'].isin(theatre_patient_ids)]
theatre_patient_records.to_csv('transfers_all_theatre.csv', header=True, index=False)
transfers = theatre_patient_records


locations_not_needed = ['XR', 'clinic','clinic ', 'PET', 'CT', 'echo', 'US', 'angio', 'TOE','NP', 'physio', 'recovery','endoscopy', 'MRI']

#longest_journey = maxLen


def get_patient_journey(ptid, group):
    counts = dict()
    journey_row = {'ptid': ptid}
    last_loc = ""

    for i, row in group.iterrows():
        loc = row['from_cat']
        if i==1:
            last_loc = loc
            # num = counts.get(loc, 1)
            # counts[loc] = num + 1
            #num = 0
            #loc_name = f"{loc}{num}"
            loc_name = f"{loc}"
            column_name = f"loc_{str(len(journey_row)).rjust(2, '0')}"
            journey_row[column_name] = loc_name
        if (not (loc in locations_not_needed)) and (loc != last_loc) and (i>1):
            last_loc = loc
            #num = counts.get(loc, 1)
            #counts[loc] = num + 1
            #num=0
            #loc_name = f"{loc}{num}"
            loc_name = f"{loc}"
            column_name = f"loc_{str(len(journey_row)).rjust(2, '0')}"
            journey_row[column_name] = loc_name

    return journey_row


journey_data = [get_patient_journey(ptid, group) for ptid, group in transfers.groupby('ptid')]

df_journeys = pd.DataFrame(data=journey_data).fillna('dc')



adminfo = pd.read_csv("ADM_INFO_aug.csv")
#pick the columns in the secondary files that are actually needed.
#adminfo = adminfo[['adm_hosp', 'dis_hosp', 'specialty', 'admAge', 'STUDY_SUBJECT_DIGEST']]
# Set the index of the adminfo dataframe to the value we want to join to.

adminfo['adm_hosp'] = pd.to_datetime(adminfo['adm_hosp'])
adminfo['dis_hosp'] = pd.to_datetime(adminfo['dis_hosp'])
adminfo['los'] = (adminfo['dis_hosp'] - adminfo['adm_hosp']).dt.days

adminfo = adminfo[['adm_hosp', 'dis_hosp', 'specialty', 'admAge','los', 'STUDY_SUBJECT_DIGEST']]
adminfo.set_index('STUDY_SUBJECT_DIGEST', drop=True, inplace=True)
# Join the columns in adminfo onto the admpoint dataframe based on patient ID.
full_journeys = df_journeys.join(adminfo, on='ptid', how='left')

surgeriesinfo = pd.read_csv("SURGERIES_aug.csv")
surg_extra = surgeriesinfo[['asa_rating_c', 'STUDY_SUBJECT_DIGEST']]
surg_extra.set_index('STUDY_SUBJECT_DIGEST', drop=True, inplace=True)
full_info = full_journeys.join(surg_extra, on='ptid', how='left')

full_info.to_csv('journeys_notcounted_asa_theatre.csv', header=True, index=True)
full_journeys.to_csv('journeys_notcounted_theatre.csv', header = True, index = True)







