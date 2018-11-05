#this uses the transfers file to add on hospital strain data and combine wards into categories in preparation for ARIMA modelling ont he network parameters

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
    return dt.year * 10000 + dt.month * 100 + dt.day


def get_date_number_from_string(date_time_entry):
    dt = get_separate_date_time(date_time_entry)
    return get_date_number(dt)

def get_transfer_day(date):
    strdate = str(date)
    fmt = "%Y-%m-%d %H:%M"
    try:
        d = datetime.strptime(strdate, fmt)
    except ValueError as v:
        ulr = len(v.args[0].partition('unconverted data remains: ')[2])
        if ulr:
            d = datetime.strptime(strdate[:-ulr], fmt)
        else:
            raise v
    return d


all_transfers = pd.read_csv("all_transfers_1110.csv")
all_transfers['transfer_dt'] = all_transfers['transfer_dt'].map(get_separate_date_time)
all_transfers['transfer_date_number'] = all_transfers['transfer_dt'].map(get_date_number)
print(all_transfers['transfer_date_number'])

print("Rows: %s" % len(all_transfers))

first_date = datetime(2015, 1, 1)
last_date = datetime(2018, 7, 1)
after_last_date = all_transfers[all_transfers['transfer_dt'] > last_date]
all_transfers.drop(after_last_date.index, axis=0, inplace=True)
before_first_date = all_transfers[all_transfers['transfer_dt'] < first_date]
all_transfers.drop(before_first_date.index, axis=0, inplace=True)

print("Rows after removing bad dates: %s" % len(all_transfers))


#add on the information about the hospital state from the ED performance file
ed_performance = pd.read_csv("ed_performance_all.csv")
# need transfer date only in a separate column
ed_performance['date'] = pd.to_datetime(ed_performance['day'], format='%d/%m/%Y')
ed_performance['date_number'] = ed_performance['date'].map(get_date_number)
ed_performance.drop(['date'], axis=1, inplace=True)
ed_performance.set_index('date_number', drop=True, inplace=True)
all_transfers_with_edperf = all_transfers.join(ed_performance, on='transfer_date_number', how='left')

#add on bedstate information - all beds
bedstate_info = pd.read_csv("all_beds_info.csv")
bedstate_info['date'] = pd.to_datetime(bedstate_info['Date'], format='%Y-%m-%d')
bedstate_info['date_number'] = bedstate_info['date'].map(get_date_number)
bedstate_info.drop(['date'], axis = 1, inplace = True)
bedstate_info.set_index('date_number', drop = True, inplace = True)
all_transfers_with_ed_beds= all_transfers_with_edperf.join(bedstate_info, on = 'transfer_date_number', how = 'left')


all_t_strain = all_transfers_with_ed_beds.drop(['transfer_date_number'], axis=1)
#now we have a file with all trasnfers and the bestate and ed performance
#now need to combine wards into categories to allow for daily network construction with enough data

all_t_strain.to_csv('all_transfers_with_ed_perf.csv', header=True, index=False)
print('performance added on file created')

all_t_strain.rename(index=str, columns={'from': 'from_loc'}, inplace=True)
all_t_strain.rename(index=str, columns={'to': 'to_loc'}, inplace=True)
list_from_wards = all_t_strain.from_loc.unique()
list_to_wards = all_t_strain.to_loc.unique()


#need to make an assignment of the individual wards to a category eg surgical ward, outlier, high dependency...



#this is the main dictionary
#ward_dictionary = {'ADD A3 WARD': 'A3 ward', 'ADD A4 WARD': 'ns ward',
#                   'ADD A5 WARD': 'ns ward', 'ADD D6 WARD': 'ns ward',
#                   'ADD CLINICAL DECN UNIT': 'CDU ward', 'ADD CT': 'CT scan',
#                   'ADD ECHO1': 'echo', 'ADD EMERGENCY DEPT': 'AE',
#                   'ADD GENRAD': 'radiology', 'ADD IRAD': 'interv rad',
#                   'ADD J2 WARD': 'surgical day ward', 'ADD J2-C3 WARD': 'PICU ward',
#                   'ADD MAIN THEATRE': 'theatre', 'ADD MAIN THEATRE 04':'emergency theatre',
#                   'ADD MAIN THEATRE 22': 'neuro theatre', 'ADD MRI': 'mri',
#                   'ADD NEURO ICU': 'nncu', 'ADD NEURO THEATRE': 'neuro theatre',
#                   'ADD NEURO THEATRE 1': 'neuro theatre', 'ADD US': 'us',
#                  'ADD CUH EXT FILM': 'external radiology', 'ADD POST-DISCHARGE': 'post-discharge',
#                   'discharge': 'discharge', 'ADD C5 WARD': 'general medical ward',
#                   'ADD D10': 'general medical ward', 'ADD D8 WARD': 'orthopaedic ward',
#                   'ADD D9 WARD': 'general medical ward', 'ADD DISCHARGE LOUNGE': 'disch lounge',
#                   'ADD FLUORO': 'fluoroscopy', 'ADD GENERAL ICU': 'icu',
#                  'ADD LSFOOT': 'outpatient', 'ADD MAIN THEATRE 20': 'theatre',
#                   'ADD NEURO THEATRE 2': 'neuro theatre', 'ADD NEURO THEATRE 3': 'neuro theatre',
#                   'ADD NEUROPHY': 'neurophys', 'ADD PET': 'PET scan',
#                   'ADD REHAB UNIT': 'rehab', 'ADD RT TRT': 'RT treatment',
#                   'Endo Ward': 'endoscopy', 'ADD D4 IDA UNIT': 'HDU','ADD L2 WARD' : 'surgical day ward',
#                   'ADD MAIN THEATRE 16': 'theatre', 'ADD R2 WARD': 'rehab',
#                   'ADD K3 WARD': 'cardiology ward', 'ADD G4 WARD': 'general medical ward',
#                   'ADD L4 WARD': 'ATC surgical ward', 'ADD L5 WARD': 'ATC surgical ward',
#                   'ADD C4 WARD': 'acute medical ward', 'ADD ATC THEATRE': 'theatre',
#                   'ADD ATC THEATRE 31': 'theatre', 'ADD ATC THEATRE 32': 'theatre',
#                   'ADD ATC THEATRE 36': 'theatre', 'ADD ATC THEATRE 33': 'theatre',
#                   'ADD ATC THEATRE 34': 'theatre', 'ADD M4 WARD': 'ATC surgical ward',
#                   'ROS DAPHNE WARD': 'gynae surgical ward', 'ADD PRE-ADMISSION':'pre-ad',
#                   'ADD ATC THEATRE 35': 'theatre', 'ADD C10 WARD': 'general medical ward','ADD C3 WARD': 'paediatric ward',
#                   'ADD D10 WARD': 'general medical ward', 'ADD CATH ROOM': 'angiography',
#                   'ADD CORONARY CARE UNIT': 'HDU', 'ADD DIALYSIS UNIT': 'dialysis',
#                   'ADD K2 WARD': 'cardiology ward', 'ADD MAIN THEATRE 17': 'theatre',
#                   'ADD D5 WARD': 'general medical ward', 'ADD D6H WARD': 'general medical ward','ADD C9 WARD': 'paediatric ward',
#                   'ADD D7 WARD': 'general medical ward', 'ADD C7 WARD': 'general surgical ward','ADD C6 WARD': 'general medical ward',
#                   'ADD C8 WARD': 'orthopaedic ward',  'ADD EAU4 WARD': 'acute medical ward', 'ADD C2 WARD': 'paediatric ward','ADD D2 WARD': 'paediatric ward',
#                   'ADD F6 WARD': 'general medical ward', 'ADD G6 WARD': 'general medical ward',
#                   'ADD F5 WARD': 'acute medical ward', 'ADD G5 WARD': 'general medical ward',
#                   'ADD F4 WARD': 'general medical ward', 'ADD G3 WARD': 'general medical ward',
#                   'ADD F3 WARD': 'paediatric ward', 'ADD K2 TOE/CARDIOVERSION': 'toe',
#                   'ADD M5 WARD': 'ATC surgical ward', 'ADD MAIN THEATRE 08': 'theatre',
#                   'ADD MED S-STAY UNIT': 'acute medical ward', 'ADD N2 WARD': 'general medical ward',
#                   'ADD N3 WARD': 'acute medical ward', 'ADD RT REV': 'outpatient',
#                   'ADD TRANSPLANT HDU': 'HDU', 'ADD ADDOPTHIMG14': 'outpatient','ADD ADDOPTHIMG3': 'outpatient','ADD ADDOPTHIMGVF': 'outpatient',
#                   'ADD BMF': 'haematology treatment', 'ADD DAY SURGERY UNIT': 'day surgery unit',
#                   'ADD MAIN THEATRE 03': 'theatre', 'ADD MAIN THEATRE 05': 'theatre',
#                   'ADD MAIN THEATRE 01': 'theatre', 'ADD MAIN THEATRE 02': 'theatre',
#                   'ADD MAIN THEATRE 09': 'theatre', 'ADD MAIN THEATRE 10': 'theatre',
#                   'ADD MAIN THEATRE 11': 'theatre', 'ADD MAIN THEATRE 12': 'theatre',
#                   'ADD MAIN THEATRE 14': 'theatre', 'ADD MAIN THEATRE 15': 'theatre',
#                   'ADD MAIN THEATRE 18': 'theatre', 'ADD MAIN THEATRE 19': 'theatre',
#                   'ADD MAIN THEATRE 23': 'theatre', 'ADD MAIN THEATRE 21': 'theatre',
#                   'ADD MAIN THEATRE 06': 'theatre', 'ADD MAIN THEATRE 07': 'theatre',
#                   'ADD OIR RECOVERY': 'oir', 'ADD SURG DISCH LOUNGE': 'disch lounge',
#                   'ADD ADREHAB': 'rehab', 'ADD DENTALX': 'radiology',
#                   'ADD EMMF': 'outpatient', 'ADD GII': 'general medical ward',
#                   'ADD ORTHOP': 'outpatient', 'ADD OTHOTMON': 'outpatient',
#                   'CUH EXT FILM': 'external radiology', 'ADD PFWON': 'outpatient',
#                   'ROS MRI SCAN': 'mri', 'VAU WARD': 'vascular access ward',
#                   'ADD EAU5 WARD': 'acute medical ward', 'ADD PPMFU': 'PPM','ADD EAU3 WARD': 'acute medical ward',
#                   'ADD CL8': 'outpatient', 'ADD OBS US': 'us',
#                   'ADD CNPHY': 'neurophys', 'ADD AAA': 'other',
#                   'ADD FANREHA': 'rehab','ADD G2 WARD': 'general medical ward',
#                   'ADD OTHOTATY': 'outpatient', 'ADD STOMA': 'outpatient',
#                   'CUHTAANKGLAU': 'outpatient', 'ADD EMEYE': 'outpatient',
#                   'ADD EMMO': 'outpatient', 'ADD EYE UNIT DAYCASES': 'theatre',
#                   'ADD EYE UNIT THEATRE': 'theatre', 'CUH ELY DAY SURG UNIT': 'theatre ely',
#                   'ADD E10 WARD': 'medical ward', 'ROS CYSTOMCS': 'investigation',
#                   'ROS GONC': 'investigation', 'ADD ENTX': 'investigation',
#                   'ADD DIAGVEST':'other','ADD JRM':'other','ADD HFT':'other','ADD LFT':'other',
#                   'ADD NM':'other', 'ADD PDHU':'investigation', 'ADD RBJNEPH': 'other',
#                   'ADD AIADAR': 'other', 'ADD TXM': 'other','ADD LVR':'other', 'ADD WTUOC':'other',
#                   'ADD JODR': 'other','ADD AHNREF':'other','ADD NJAUOC':'other','ADD JMDW':'other',
#                   'ADD ACF': 'nephro appt', 'ADD DKNAMD':'opth appt', 'ADD EABC':'gastro appt', 'ADD MRDB':'cardiology appt',
#                   'ADD UDA':'oral surgery appt', 'ADD POADSU': 'anaesthetic assess', 'ADD POAOSDSU':'anaesthetic assess',
#                   'ADD AJCUOCW':'urology appt','ADD SJM':'surgery appt','ADD SMBRECON': 'urology appt', 'ADD SRGAMB': 'surgery appt',
#                   'ADD LVRF':'trauma appt','ADD KDABI':'plastic surgery appt', 'ADD NSGYFC':'ns appt', 'ADD PSUD':'plastic surgery appt',
#                   'ADD BU':'radiology', 'POST-DISCHARGE':'post-discharge', 'PRE-ADMISSION':'pre-ad'}

#dictionary for removing weekday influence on node numbers
ward_dictionary = {'ADD A3 WARD': 'A3 ward', 'ADD A4 WARD': 'ns ward',
                   'ADD A5 WARD': 'ns ward', 'ADD D6 WARD': 'ns ward',
                   'ADD CLINICAL DECN UNIT': 'CDU ward', 'ADD CT': 'CT scan',
                   'ADD ECHO1': 'echo', 'ADD EMERGENCY DEPT': 'AE',
                   'ADD GENRAD': 'radiology', 'ADD IRAD': 'interv rad',
                   'ADD J2 WARD': 'surgical day ward', 'ADD J2-C3 WARD': 'PICU ward',
                   'ADD MAIN THEATRE': 'theatre', 'ADD MAIN THEATRE 04':'emergency theatre',
                   'ADD MAIN THEATRE 22': 'neuro theatre', 'ADD MRI': 'mri',
                   'ADD NEURO ICU': 'nncu', 'ADD NEURO THEATRE': 'neuro theatre',
                   'ADD NEURO THEATRE 1': 'neuro theatre', 'ADD US': 'us',
                   'ADD CUH EXT FILM': 'external radiology', 'ADD POST-DISCHARGE': 'post-discharge',
                   'discharge': 'discharge', 'ADD C5 WARD': 'general medical ward',
                   'ADD D10': 'general medical ward', 'ADD D8 WARD': 'orthopaedic ward',
                   'ADD D9 WARD': 'general medical ward', 'ADD DISCHARGE LOUNGE': 'disch lounge',
                   'ADD FLUORO': 'fluoroscopy', 'ADD GENERAL ICU': 'icu',
                   'ADD LSFOOT': 'weekday', 'ADD MAIN THEATRE 20': 'theatre',
                   'ADD NEURO THEATRE 2': 'neuro theatre', 'ADD NEURO THEATRE 3': 'neuro theatre',
                   'ADD NEUROPHY': 'weekday', 'ADD PET': 'PET scan',
                   'ADD REHAB UNIT': 'rehab', 'ADD RT TRT': 'weekday',
                   'Endo Ward': 'weekday', 'ADD D4 IDA UNIT': 'HDU','ADD L2 WARD' : 'surgical day ward',
                   'ADD MAIN THEATRE 16': 'theatre', 'ADD R2 WARD': 'rehab',
                   'ADD K3 WARD': 'cardiology ward', 'ADD G4 WARD': 'general medical ward',
                   'ADD L4 WARD': 'ATC surgical ward', 'ADD L5 WARD': 'ATC surgical ward',
                   'ADD C4 WARD': 'acute medical ward', 'ADD ATC THEATRE': 'theatre',
                   'ADD ATC THEATRE 31': 'theatre', 'ADD ATC THEATRE 32': 'theatre',
                   'ADD ATC THEATRE 36': 'theatre', 'ADD ATC THEATRE 33': 'theatre',
                   'ADD ATC THEATRE 34': 'theatre', 'ADD M4 WARD': 'ATC surgical ward',
                   'ROS DAPHNE WARD': 'gynae surgical ward', 'ADD PRE-ADMISSION':'pre-ad',
                   'ADD ATC THEATRE 35': 'theatre', 'ADD C10 WARD': 'general medical ward','ADD C3 WARD': 'paediatric ward',
                   'ADD D10 WARD': 'general medical ward', 'ADD CATH ROOM': 'angiography',
                   'ADD CORONARY CARE UNIT': 'HDU', 'ADD DIALYSIS UNIT': 'weekday',
                   'ADD K2 WARD': 'cardiology ward', 'ADD MAIN THEATRE 17': 'theatre',
                   'ADD D5 WARD': 'general medical ward', 'ADD D6H WARD': 'general medical ward','ADD C9 WARD': 'paediatric ward',
                   'ADD D7 WARD': 'general medical ward', 'ADD C7 WARD': 'general surgical ward','ADD C6 WARD': 'general medical ward',
                   'ADD C8 WARD': 'orthopaedic ward',  'ADD EAU4 WARD': 'acute medical ward', 'ADD C2 WARD': 'paediatric ward','ADD D2 WARD': 'paediatric ward',
                   'ADD F6 WARD': 'general medical ward', 'ADD G6 WARD': 'general medical ward',
                   'ADD F5 WARD': 'acute medical ward', 'ADD G5 WARD': 'general medical ward',
                   'ADD F4 WARD': 'general medical ward', 'ADD G3 WARD': 'general medical ward',
                   'ADD F3 WARD': 'paediatric ward', 'ADD K2 TOE/CARDIOVERSION': 'toe',
                   'ADD M5 WARD': 'ATC surgical ward', 'ADD MAIN THEATRE 08': 'theatre',
                   'ADD MED S-STAY UNIT': 'acute medical ward', 'ADD N2 WARD': 'general medical ward',
                   'ADD N3 WARD': 'acute medical ward', 'ADD RT REV': 'weekday',
                   'ADD TRANSPLANT HDU': 'HDU', 'ADD ADDOPTHIMG14': 'weekday','ADD ADDOPTHIMG3': 'weekday','ADD ADDOPTHIMGVF': 'weekday',
                   'ADD BMF': 'weekday', 'ADD DAY SURGERY UNIT': 'weekday',
                   'ADD MAIN THEATRE 03': 'theatre', 'ADD MAIN THEATRE 05': 'theatre',
                   'ADD MAIN THEATRE 01': 'theatre', 'ADD MAIN THEATRE 02': 'theatre',
                   'ADD MAIN THEATRE 09': 'theatre', 'ADD MAIN THEATRE 10': 'theatre',
                   'ADD MAIN THEATRE 11': 'theatre', 'ADD MAIN THEATRE 12': 'theatre',
                   'ADD MAIN THEATRE 14': 'theatre', 'ADD MAIN THEATRE 15': 'theatre',
                   'ADD MAIN THEATRE 18': 'theatre', 'ADD MAIN THEATRE 19': 'theatre',
                   'ADD MAIN THEATRE 23': 'theatre', 'ADD MAIN THEATRE 21': 'theatre',
                   'ADD MAIN THEATRE 06': 'theatre', 'ADD MAIN THEATRE 07': 'theatre',
                   'ADD OIR RECOVERY': 'weekday', 'ADD SURG DISCH LOUNGE': 'disch lounge',
                   'ADD ADREHAB': 'rehab', 'ADD DENTALX': 'radiology',
                   'ADD EMMF': 'weekday', 'ADD GII': 'general medical ward',
                   'ADD ORTHOP': 'weekday', 'ADD OTHOTMON': 'weekday',
                   'CUH EXT FILM': 'external radiology', 'ADD PFWON': 'weekday',
                   'ROS MRI SCAN': 'mri', 'VAU WARD': 'vascular access ward',
                   'ADD EAU5 WARD': 'acute medical ward', 'ADD PPMFU': 'weekday','ADD EAU3 WARD': 'acute medical ward',
                   'ADD CL8': 'weekday', 'ADD OBS US': 'us',
                   'ADD CNPHY': 'neurophys', 'ADD AAA': 'weekday',
                   'ADD FANREHA': 'rehab','ADD G2 WARD': 'general medical ward',
                   'ADD OTHOTATY': 'weekday', 'ADD STOMA': 'weekday',
                   'CUHTAANKGLAU': 'weekday', 'ADD EMEYE': 'weekday',
                   'ADD EMMO': 'weekday', 'ADD EYE UNIT DAYCASES': 'weekday',
                   'ADD EYE UNIT THEATRE': 'theatre', 'CUH ELY DAY SURG UNIT': 'weekday',
                   'ADD E10 WARD': 'medical ward', 'ROS CYSTOMCS': 'weekday',
                   'ROS GONC': 'weekday', 'ADD ENTX': 'weekday',
                   'ADD DIAGVEST':'weekday','ADD JRM':'weekday','ADD HFT':'weekday','ADD LFT':'weekday',
                   'ADD NM':'weekday', 'ADD PDHU':'investigation', 'ADD RBJNEPH': 'weekday',
                   'ADD AIADAR': 'weekday', 'ADD TXM': 'weekday','ADD LVR':'weekday', 'ADD WTUOC':'weekday',
                   'ADD JODR': 'weekday','ADD AHNREF':'weekday','ADD NJAUOC':'weekday','ADD JMDW':'weekday',
                   'ADD ACF': 'weekday', 'ADD DKNAMD':'weekday', 'ADD EABC':'weekday', 'ADD MRDB':'weekday',
                   'ADD UDA':'weekday', 'ADD POADSU': 'weekday', 'ADD POAOSDSU':'weekday',
                   'ADD AJCUOCW':'weekday','ADD SJM':'weekday','ADD SMBRECON': 'weekday', 'ADD SRGAMB': 'weekday',
                   'ADD LVRF':'weekday','ADD KDABI':'weekday', 'ADD NSGYFC':'weekday', 'ADD PSUD':'weekday',
                   'ADD BU':'radiology', 'POST-DISCHARGE':'post-discharge', 'PRE-ADMISSION':'pre-ad'}


location_category_map = ward_dictionary

all_t_strain['from_category'] = all_t_strain['from_loc'].map(location_category_map)

missing_locations = all_t_strain[all_t_strain['from_category'].isnull()]['from_loc'].unique()
print(missing_locations)


all_t_strain['to_category'] = all_t_strain['to_loc'].map(location_category_map)

list_from_wards = all_t_strain.from_category.unique()
print(list_from_wards)
all_t_strain.to_csv('transfers_strain_cat_noweekday.csv', header=True, index=False)
print('transfer file with cat and strain written')

#
#
#
#
