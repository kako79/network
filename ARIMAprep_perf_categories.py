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


#all_transfers = pd.read_csv("transfers_all_icu.csv")
all_transfers = pd.read_csv("all_adult_transfers.csv")
all_transfers['transfer_dt'] = all_transfers['transfer_dt'].map(get_separate_date_time)
all_transfers['transfer_date_number'] = all_transfers['transfer_dt'].map(get_date_number)
print(min(all_transfers['transfer_date_number']))
print(max(all_transfers['transfer_date_number']))
print("Rows: %s" % len(all_transfers))

first_date = datetime(2015, 1, 1)
last_date = datetime(2018, 7, 1)
after_last_date = all_transfers[all_transfers['transfer_dt'] > last_date]
print("after last date",after_last_date)
all_transfers.drop(after_last_date.index, axis=0, inplace=True)
before_first_date = all_transfers[all_transfers['transfer_dt'] < first_date]
all_transfers.drop(before_first_date.index, axis=0, inplace=True)


print("Rows after removing bad dates: %s" % len(all_transfers))
print("transfer date number %s"% all_transfers['transfer_date_number'])

#add on the information about the hospital state from the ED performance file
ed_performance = pd.read_csv("ed_performance_all.csv")
# need transfer date only in a separate column
ed_performance['date'] = pd.to_datetime(ed_performance['day'], format='%d/%m/%Y')
ed_performance['date_number'] = ed_performance['date'].map(get_date_number)
ed_performance.drop(['date'], axis=1, inplace=True)
print("ed performance")
print(ed_performance['date_number'])
ed_performance.set_index('date_number', drop=True, inplace=True)

all_transfers_with_edperf = all_transfers.join(ed_performance, on='transfer_date_number', how='left', lsuffix="abbv", rsuffix="arrv")
all_transfers_with_edperf.drop(['breach_percentageabbv'], axis=1, inplace=True)
all_transfers_with_edperf.rename(index=str, columns={'breach_percentagearrv': 'breach_percentage'}, inplace=True)

#add on bedstate information - all beds
#bedstate_info = pd.read_csv("all_beds_info.csv")
#bedstate_info['date'] = pd.to_datetime(bedstate_info['Date'], format='%Y-%m-%d')
#bedstate_info['date_number'] = bedstate_info['date'].map(get_date_number)
#bedstate_info.drop(['date'], axis = 1, inplace = True)
#bedstate_info.set_index('date_number', drop = True, inplace = True)
#all_transfers_with_ed_beds= all_transfers_with_edperf.join(bedstate_info, on = 'transfer_date_number', how = 'left')


all_t_strain = all_transfers_with_edperf.drop(['transfer_date_number'], axis=1)
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
                  'ADD LSFOOT': 'outpatient', 'ADD MAIN THEATRE 20': 'theatre',
                   'ADD NEURO THEATRE 2': 'neuro theatre', 'ADD NEURO THEATRE 3': 'neuro theatre',
                   'ADD NEUROPHY': 'neurophys', 'ADD PET': 'PET scan',
                   'ADD REHAB UNIT': 'rehab', 'ADD RT TRT': 'RT treatment',
                   'Endo Ward': 'endoscopy', 'ADD D4 IDA UNIT': 'HDU','ADD L2 WARD' : 'surgical day ward',
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
                   'ADD CORONARY CARE UNIT': 'HDU', 'ADD DIALYSIS UNIT': 'dialysis',
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
                   'ADD N3 WARD': 'acute medical ward', 'ADD RT REV': 'outpatient',
                   'ADD TRANSPLANT HDU': 'HDU', 'ADD ADDOPTHIMG14': 'ophth appt','ADD ADDOPTHIMG3': 'ophth appt','ADD ADDOPTHIMGVF': 'ophth appt',
                   'ADD BMF': 'medical appt', 'ADD DAY SURGERY UNIT': 'day surgery unit',
                   'ADD MAIN THEATRE 03': 'theatre', 'ADD MAIN THEATRE 05': 'theatre',
                   'ADD MAIN THEATRE 01': 'theatre', 'ADD MAIN THEATRE 02': 'theatre',
                   'ADD MAIN THEATRE 09': 'theatre', 'ADD MAIN THEATRE 10': 'theatre',
                   'ADD MAIN THEATRE 11': 'theatre', 'ADD MAIN THEATRE 12': 'theatre',
                   'ADD MAIN THEATRE 14': 'theatre', 'ADD MAIN THEATRE 15': 'theatre',
                   'ADD MAIN THEATRE 18': 'theatre', 'ADD MAIN THEATRE 19': 'theatre',
                   'ADD MAIN THEATRE 23': 'theatre', 'ADD MAIN THEATRE 21': 'theatre',
                   'ADD MAIN THEATRE 06': 'theatre', 'ADD MAIN THEATRE 07': 'theatre',
                   'ADD OIR RECOVERY': 'oir', 'ADD SURG DISCH LOUNGE': 'disch lounge',
                   'ADD ADREHAB': 'rehab', 'ADD DENTALX': 'radiology',
                   'ADD EMMF': 'medical appt', 'ADD GII': 'general medical ward',
                   'ADD ORTHOP': 'ortho appt', 'ADD OTHOTMON': 'ophth appt',
                   'CUH EXT FILM': 'external radiology', 'ADD PFWON': 'medical appt',
                   'ROS MRI SCAN': 'mri', 'VAU WARD': 'vascular access ward',
                   'ADD EAU5 WARD': 'acute medical ward', 'ADD PPMFU': 'PPM','ADD EAU3 WARD': 'acute medical ward',
                   'ADD CL8': 'ortho appt', 'ADD OBS US': 'us',
                   'ADD CNPHY': 'neurophys', 'ADD AAA': 'other',
                   'ADD FANREHA': 'rehab','ADD G2 WARD': 'general medical ward',
                   'ADD OTHOTATY': 'ophth appt', 'ADD STOMA': 'medical appt',
                   'CUHTAANKGLAU': 'ophth appt', 'ADD EMEYE': 'ophth appt',
                   'ADD EMMO': 'medical appt', 'ADD EYE UNIT DAYCASES': 'theatre eye',
                   'ADD EYE UNIT THEATRE': 'theatre eye', 'CUH ELY DAY SURG UNIT': 'theatre ely',
                   'ADD E10 WARD': 'medical ward', 'ROS CYSTOMCS': 'gynae appt',
                   'ROS GONC': 'gynae appt', 'ADD ENTX': 'ent appt',
                   'ADD DIAGVEST':'other','ADD JRM':'other','ADD HFT':'other','ADD LFT':'other',
                   'ADD NM':'other', 'ADD PDHU':'general surgical appt', 'ADD RBJNEPH': 'other',
                   'ADD AIADAR': 'medical appt', 'ADD TXM': 'transplant appt','ADD LVR':'ortho appt', 'ADD WTUOC':'other',
                   'ADD JODR': 'general surgical appt','ADD AHNREF':'medical appt','ADD NJAUOC':'other','ADD JMDW':'general surgical appt',
                   'ADD ACF': 'nephro appt', 'ADD DKNAMD':'opth appt', 'ADD EABC':'gastro appt', 'ADD MRDB':'cardiology appt',
                   'ADD UDA':'oral surgery appt', 'ADD POADSU': 'anaesthetic assess', 'ADD POAOSDSU':'anaesthetic assess',
                   'ADD AJCUOCW':'urology appt','ADD SJM':'surgery appt','ADD SMBRECON': 'urology appt', 'ADD SRGAMB': 'surgery appt',
                   'ADD LVRF':'trauma appt','ADD KDABI':'plastic surgery appt', 'ADD NSGYFC':'ns appt', 'ADD PSUD':'plastic surgery appt',
                   'ADD BU':'radiology', 'POST-DISCHARGE':'post-discharge', 'PRE-ADMISSION':'pre-ad', 'ADD J3-C3 WARD': 'surgical day ward', 'ADD PAED ICU': 'picu',
                   'ADD R3': 'general medical ward', 'ADD PLASTIC SURG UNIT': 'surgical day ward',
                   'ADD KDA': 'weekday', 'ADDFLEXCYSOP': 'urology appt', 'ROS SARA WARD': 'gynae surgical ward', 'ROS MFM': 'maternity', 'ROS DELIVERY UNIT': 'maternity',
                   'ROS ROSIE THEATRE 2': 'rosie theatre', 'ADD GDC': 'medical appt', 'ADD ONCOLOGY DAY UNIT': 'medical appt', 'ADD AECLINIC': 'paed appt',
                   'ROS OBS US': 'us', 'ADD OTHOTESP': 'ophth appt', 'ADD SNSKF': 'trauma appt', 'ADDOPTHIMG14':'ophth appt', 'ADD EMENT': 'other',
                   'ADD DSK': 'medical appt', 'ADD PMT': 'medical appt', 'ROS ROSIE THEATRE 1': 'rosie theatre', 'ROS LADY MARY WARD': 'maternity', 'ADD PACV': 'general surgical appt',
                   'ADD DKNVR': 'other',  'ADD EYE UNIT THEATRE 41': 'theatre eye', 'ADD SURGAMB': 'general surgery appt', 'ADD OTHOTRMC':'ophth appt',
                   'ADD J3 PICU WARD': 'picu', 'ADD NEUROONC': 'medical appt', 'CUH ELY THEATRE 3': 'theatre ely', 'ROS UROG': 'gynae appt',
                   'ADD FCHEM': 'medical appt', 'ADD RMAC': 'trauma appt', 'ADD C9 DAY UNIT': 'general medicl ward', 'ADD MKTMF': 'general surgical appt',
                   'ADD EYE UNIT THEATRE 42': 'theatre', 'ADD ORALCF': 'general surgical appt', 'ADD ALA':'medical appt' , 'ADD ADCA': 'ortho appt', 'ADD DCHIR': 'medical appt',
                   'L4 WARD': 'general surgical ward', 'ADD LITHO': 'urology appt','ADD MLBV': 'ENT appt', 'ADDKKSTPHCL1': 'gastro appt', 'ADD ARNO': 'ortho appt', 'ADD ENT': 'ent appt',
                   'ADD ORALNK': 'maxfax appt', 'ADDSALHSTONE': 'appt', 'ADD DVT': 'appt', 'ADD LEAP': 'ophth appt', 'ADD ANGED': 'neuro appt', 'ADD MP': 'general surgical appt',
                   'ADD ARNOF': 'ortho appt', 'F3 WARD': 'paediatric ward', 'ADD KKSTF':'general surgical appt',  'ADD SO': 'appt', 'ADD CROPP': 'rehab', 'ADD PJM3': 'appt',
                   'ADD TPBAC': 'other', 'ADD HHSC': 'other', 'ADD PAED DAY UNIT': 'paed day unit', 'ADD JOMR': 'other', 'ADD SM': 'appt',
                   'ADDOPTHIMGVF': 'ophth appt', 'ADD AMBIPN3': 'general surgical appt', 'ADD PAEDAUD': 'paed appt' ,'ADD NASHC': 'hepat appt', 'ADD BPHYT': 'medical appt',
                   'ADD CARDPP': 'medical appt', 'ADD PDHUF': 'appt', 'NICU WARD': 'picu', 'M5 WARD': 'ATC surgical ward', 'ADD CJGG': 'appt',  'ADD TXT': 'transplant appt',
                   'ADD PDCCAP': 'urology appt', 'ADD EIUNET': 'other', 'ADD POAF2F': 'anaesthetic assess ', 'ADD ALC43': 'general surgical appt', 'ADD NSGYPAED': 'paed appt',
                   'ADD EMEWA': 'ophth appt', 'ADD LVA': 'ophth appt', 'ADD RMIL': 'general surgical appt',  'ADD CAUFUTEL': 'appt', 'ADD HMF': 'maternity', 'ADD JTKM': 'other',
                   'PDU WARD': 'paediatric day ward', 'ADD BMUTN': 'other', 'ADD EMSAC': 'appt', 'ADD PPMBS': 'appt', 'ADD ACPRUOC':'appt', 'ADD OPLAOP': 'general surgical appt',
                   'ADD GICH': 'medical appt', 'ADD PENT': 'paediatric appt', 'ADD RATRG': 'neuro appt',  'ADD COLSB': ' general surgical appt', 'ADD CRG': 'urology appt', 'ADD LCWVASC': 'general surgical appt',
                   'ROS MADU': 'maternity', 'ADD HAEMOP': 'medical appt', 'ADD PRIMARY': 'other', 'ADD TNM':'urology appt' , 'ADD DXACCESS': 'transplant appt', 'G2 WARD' : 'general medical ward',
                   'ADD PPMBSK2': 'cardiology appt', 'ADD MAIN RECOVERY': 'recovery', 'ADD PDH': 'ortho appt', 'ADD AIAD': 'medical appt' ,
                   'ADD ENDOSCOPY UNIT': 'endoscopy', 'ADD IMPREHAB': 'rehab', 'ADD CDMSLD': 'paed appt', 'ADD PJPU': 'cardiology appt', 'ADD YML': 'physio',
                   'ADD PJNK': 'ent appt', 'ADD NEUROTR': 'trauma appt', 'ADD MSR': 'ophth appt', 'ADD KRM': 'ophth appt', 'ADD PJ': 'paed appt', 'ADD PHYL': 'physio',
                   'ADD ORALVSAN':'appt',  'ADD MOSOP': 'maxfax appt', 'ADD AJCUOC': 'urology appt', 'ADD TKKHL': 'medical appt', 'ADD EMSMHC':'medical appt',
                   'ADD NEJENT': 'ent appt', 'ADD JPF': 'general surgical appt', 'ADD EIACA': 'medical appt', 'ADD UROLA': 'urology appt', 'E10 WARD': 'general medical ward', 'ADD GMTSEF': 'ortho appt',
                   'ADD APCCOMB': 'medical appt', 'ADD MLEDAR': 'medical appt', 'ADD NPDV': 'ortho appt', 'ADDOTHOTORTH': 'ortho appt', 'ADD AJM': 'medical appt',
                   'ADD PDHUEF': 'general surgical appt', 'ADD SNSKEF': 'ortho appt', 'ADD D5 DAY CASE UNIT': 'day surgery ward', 'ADD MPFC': 'trauma appt','ADD MPS': 'ophth appt',
                   'ADD PHYE': 'physio', 'ADD PMTSN':'medical appt', 'ADD CNPHYR3': 'neurophysiology', 'ADD PHYSD': 'physio', 'ROS GAH': 'gynae appt', 'ADD GMTSF': 'ortho appt',
                   'ADD KFTE': 'medical appt', 'ADD MPMPP': 'other', 'ADD VASC ACC DAY UNIT': 'vascular access appt', 'ADD JNAUOC': 'urology appt', 'ROS EGDW': 'radiology',
                   'CUH SW RAD': 'medical appt', 'ADD SMC':'paed appt',  'ADD AHNRD': 'urology appt', 'ADD VK': 'medical appt', 'ADD DRWJT': 'medical appt' ,'G5 WARD': 'general medical ward',
                   'ADD NTRECON': 'appt', 'ADD AMBPEN3': 'other', 'ADD MRB': 'cardiology appt', 'ADD NEUROREG': 'neurol appt', 'ADD IBDTEL': 'gastro appt',
                   'ADD RGTD2': 'medical appt', 'ADD THR': 'ent appt', 'ADD CBUR': 'general surgical appt', 'ADD THEATRE 12 DC UNIT': 'theatre', 'ADD MKF': 'trauma appt',
                   'ADD DEXA': 'radiology', 'ADD CARDK2': 'cardiology', 'ADD DSCP': 'other', 'ADD MSI': 'general surgical appt' ,'ADD OTHOTDST': 'ophth appt', 'ADD ENTOTO': 'ent appt',
                   'ROS CHARLES WOLFSON WD': 'paediatric ward', 'ROS ROSIE BIRTH CENTRE': 'maternity', 'ADD GYNRT': 'gynae appt', 'ROS EPUDW': 'maternity',
                   'ADD PSOPGN': 'medical appt', 'ADD DGUGI':'medical appt',  'ADD NRH': 'general surgical appt', 'ADD ECEP': 'medical appt', 'ADD DMOS': 'cardiology appt', 'ADD LDC': 'transplant appt',
                   'ADD AR1F': 'trauma appt', 'ADD AMFU': 'medical appt', 'ADD CATARACT': 'ophth appt', 'ROS SCHDPROC': 'maternity', 'ADD CAMHS': 'medical appt',
                   'ADD OPLAKDA': 'general surgical appt', 'CUH TKKHC': 'medical appt', 'ADD MGEND': 'medical appt', 'ADD GPRC': 'medical appt', 'ALGYDC WARD': 'other',
                   'ADD ALLERGY DAY UNIT': 'medical appt', 'ADD CR': 'other', 'ADD NEUREG': 'neurol appt', 'ADD TXW':'transplant appt', 'CUH HOME BIRTH': 'maternity',
                   'ADD FCH': 'gynae appt', 'ADD PHG': 'general surgical appt', 'ADD CRJAPSUR': 'paed appt', 'ADD CORNREV': 'ophth appt', 'ADD MKO': 'medical appt', 'ADD CNPHY43': 'neurophysiology',
                   'ADD LEAPCON': 'paed appt', 'ADD CAU': 'other', 'ADD AHNR':'ortho appt',  'ADD UROLP': 'urology appt', 'ADDFIBROSCAN': 'medical appt',
                   'ADD VASCSURV':'general surgical appt',  'ADD MBR': 'general surgical appt', 'ADD DE': 'other', 'ROS NURSEPMB': 'maternity', 'ADD PMIC':'paed appt', 'ADD JMW': 'medical appt',
                   'ADD RJW': 'general surgical appt', 'ADD ALCC': 'medical appt', 'ADD UVP': 'cardiology appt', 'ADD AJCGEN': 'medical appt', 'ADD CCH': 'medical appt', 'ADD DMOSVRC': 'cardiolgy appt',
                   'ADD PUVATL':'other', 'ADD JOAMD' : 'medical appt','ADD AGO': 'other', 'C8 WARD': 'orthopaedic ward', 'ADD GPRCB':'other',  'ADD PFWO': 'neurol appt',
                   'ADD JB':'other',  'ADD SMK': 'general surgical appt', 'ADD CJB': 'general surgical appt',  'CUH PFWON': 'neurol appt' ,'ADD LMSH': 'medical appt', 'ADD JLU': ',edical appt',
                   'ADD CONSFOOT': 'medical appt', 'ADD HEPNEW': 'medical appt', 'ADD KESPB': 'medical appt', 'ADD OTHOTNEU': 'other', 'ADD SKIN': 'medical appt',
                   'ADD GMTS': 'ortho appt', 'ADD SMCEF': 'trauma appt', 'ROS PPMD': 'maternity', 'ADD NFLL': 'medical appt', 'ADD LTX': 'transplant appt', 'CUH GPRCN': 'medical appt',
                   'ADD SNSK': 'ortho appt', 'ADD KV': 'general surgical appt', 'ADD NS': 'medical appt', 'CUH NGSHAV': 'medical appt', 'ADD SKAMP': 'other', 'CCRC Endo':'other',  'ADD RDPFP': 'other'}

#dictionary for removing weekday influence on node numbers
noweekday_ward_dictionary = {'ADD A3 WARD': 'A3 ward', 'ADD A4 WARD': 'ns ward',
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
                   'ADD BU':'radiology', 'POST-DISCHARGE':'post-discharge', 'PRE-ADMISSION':'pre-ad',
                   'ADD J3-C3 WARD': 'surgical day ward', 'ADD PAED ICU': 'picu', 'ADD R3': 'general medical ward', 'ADD PLASTIC SURG UNIT': 'surgical day ward',
                   'ADD KDA': 'weekday', 'ADDFLEXCYSOP': 'weekday', 'ROS SARA WARD': 'gynae surgical ward', 'ROS MFM': 'maternity', 'ROS DELIVERY UNIT': 'maternity',
                   'ROS ROSIE THEATRE 2': 'rosie theatre', 'ADD GDC': 'weekday', 'ADD ONCOLOGY DAY UNIT': 'weekday', 'ADD AECLINIC': 'weekday',
                   'ROS OBS US': 'us', 'ADD OTHOTESP': 'weekday', 'ADD SNSKF': 'weekday', 'ADDOPTHIMG14':'weekday', 'ADD EMENT': 'weekday',
                   'ADD DSK': 'weekday', 'ADD PMT': 'weekday', 'ROS ROSIE THEATRE 1': 'rosie theatre', 'ROS LADY MARY WARD': 'maternity', 'ADD PACV': 'general surgical appt',
                   'ADD DKNVR': 'weekday',  'ADD EYE UNIT THEATRE 41': 'weekday', 'ADD SURGAMB': 'general surgery appt', 'ADD OTHOTRMC':'weekday',
                   'ADD J3 PICU WARD': 'picu', 'ADD NEUROONC': 'weekday', 'CUH ELY THEATRE 3': 'weekday', 'ROS UROG': 'weekday',
                   'ADD FCHEM': 'weekday', 'ADD RMAC': 'weekday', 'ADD C9 DAY UNIT': 'general medicl ward', 'ADD MKTMF': 'general surgical appt','ADD EYE UNIT THEATRE 42': 'theatre', 'ADD ORALCF': 'general surgical appt', 'ADD ALA':'medical appt' , 'ADD ADCA': 'ortho appt', 'ADD DCHIR': 'medical appt',
                   'L4 WARD': 'general surgical ward', 'ADD LITHO': 'weekday','ADD MLBV': 'weekday', 'ADDKKSTPHCL1': 'weekday', 'ADD ARNO': 'weekday', 'ADD ENT': 'weekday',
                   'ADD ORALNK': 'weekday', 'ADDSALHSTONE': 'weekday', 'ADD DVT': 'weekday', 'ADD LEAP': 'weekday', 'ADD ANGED': 'weekday', 'ADD MP': 'weekday',
                   'ADD ARNOF': 'weekday', 'F3 WARD': 'paediatric ward', 'ADD KKSTF':'weekday',  'ADD SO': 'weekday', 'ADD CROPP': 'rehab', 'ADD PJM3': 'weekday',
                   'ADD TPBAC': 'weekday', 'ADD HHSC': 'weekday', 'ADD PAED DAY UNIT': 'weekday', 'ADD JOMR': 'weekday', 'ADD SM': 'weekday',
                   'ADDOPTHIMGVF': 'weekday', 'ADD AMBIPN3': 'weekday', 'ADD PAEDAUD': 'weekday' ,'ADD NASHC': 'weekday', 'ADD BPHYT': 'weekday',
                   'ADD CARDPP': 'medical appt', 'ADD PDHUF': 'appt', 'NICU WARD': 'picu', 'M5 WARD': 'ATC surgical ward', 'ADD CJGG': 'weekday',  'ADD TXT': 'weekday',
                   'ADD PDCCAP': 'weekday', 'ADD EIUNET': 'v', 'ADD POAF2F': 'weekday ', 'ADD ALC43': 'weekday', 'ADD NSGYPAED': 'weekday',
                   'ADD EMEWA': 'weekday', 'ADD LVA': 'weekday', 'ADD RMIL': 'weekday',  'ADD CAUFUTEL': 'weekday', 'ADD HMF': 'maternity', 'ADD JTKM': 'weekday',
                   'PDU WARD': 'weekday', 'ADD BMUTN': 'weekday', 'ADD EMSAC': 'weekday', 'ADD PPMBS': 'weekday', 'ADD ACPRUOC':'weekday', 'ADD OPLAOP': 'weekday',
                   'ADD GICH': 'medical appt', 'ADD PENT': 'paediatric appt', 'ADD RATRG': 'neuro appt',  'ADD COLSB': ' general surgical appt', 'ADD CRG': 'weekday', 'ADD LCWVASC': 'weekday',
                   'ROS MADU': 'maternity', 'ADD HAEMOP': 'weekday', 'ADD PRIMARY': 'weekday', 'ADD TNM':'weekday' , 'ADD DXACCESS': 'weekday', 'G2 WARD' : 'general medical ward',
                   'ADD PPMBSK2': 'weekdayt', 'ADD MAIN RECOVERY': 'recovery', 'ADD PDH': 'weekday', 'ADD AIAD': 'weekday' ,
                   'ADD ENDOSCOPY UNIT': 'endoscopy', 'ADD IMPREHAB': 'rehab', 'ADD CDMSLD': 'weekday', 'ADD PJPU': 'weekday', 'ADD YML': 'physio',
                   'ADD PJNK': 'weekday', 'ADD NEUROTR': 'weekday', 'ADD MSR': 'weekday', 'ADD KRM': 'weekdayt', 'ADD PJ': 'weekday', 'ADD PHYL': 'physio',
                   'ADD ORALVSAN':'appt',  'ADD MOSOP': 'weekday', 'ADD AJCUOC': 'weekday', 'ADD TKKHL': 'weekday', 'ADD EMSMHC':'weekday',
                   'ADD NEJENT': 'weekday', 'ADD JPF': 'weekday', 'ADD EIACA': 'weekday', 'ADD UROLA': 'weekday', 'E10 WARD': 'general medical ward', 'ADD GMTSEF': 'weekday',
                   'ADD APCCOMB': 'weekday', 'ADD MLEDAR': 'weekday', 'ADD NPDV': 'weekday', 'ADDOTHOTORTH': 'weekday', 'ADD AJM': 'weekday',
                   'ADD PDHUEF': 'weekday', 'ADD SNSKEF': 'weekday', 'ADD D5 DAY CASE UNIT': 'day surgery ward', 'ADD MPFC': 'weekday','ADD MPS': 'weekday',
                   'ADD PHYE': 'physio', 'ADD PMTSN':'weekday', 'ADD CNPHYR3': 'weekday', 'ADD PHYSD': 'physio', 'ROS GAH': 'weekday', 'ADD GMTSF': 'weekday',
                   'ADD KFTE': 'weekday', 'ADD MPMPP': 'weekday', 'ADD VASC ACC DAY UNIT': 'weekday', 'ADD JNAUOC': 'weekday', 'ROS EGDW': 'radiology',
                   'CUH SW RAD': 'weekday', 'ADD SMC':'weekday',  'ADD AHNRD': 'weekday', 'ADD VK': 'weekday', 'ADD DRWJT': 'weekday' ,'G5 WARD': 'general medical ward',
                   'ADD NTRECON': 'weekday', 'ADD AMBPEN3': 'weekday', 'ADD MRB': 'weekday', 'ADD NEUROREG': 'weekday', 'ADD IBDTEL': 'weekday',
                   'ADD RGTD2': 'weekday', 'ADD THR': 'weekday', 'ADD CBUR': 'weekday', 'ADD THEATRE 12 DC UNIT': 'theatre', 'ADD MKF': 'weekday',
                   'ADD DEXA': 'radiology', 'ADD CARDK2': 'weekday', 'ADD DSCP': 'weekday', 'ADD MSI': 'weekday' ,'ADD OTHOTDST': 'weekday', 'ADD ENTOTO': 'weekday',
                   'ROS CHARLES WOLFSON WD': 'paediatric ward', 'ROS ROSIE BIRTH CENTRE': 'maternity', 'ADD GYNRT': 'weekday', 'ROS EPUDW': 'maternity',
                   'ADD PSOPGN': 'weekday', 'ADD DGUGI':'weekday',  'ADD NRH': 'weekday', 'ADD ECEP': 'weekday', 'ADD DMOS': 'weekday', 'ADD LDC': 'weekday',
                   'ADD AR1F': 'weekday', 'ADD AMFU': 'weekday', 'ADD CATARACT': 'weekday', 'ROS SCHDPROC': 'maternity', 'ADD CAMHS': 'weekday',
                   'ADD OPLAKDA': 'weekday', 'CUH TKKHC': 'weekday', 'ADD MGEND': 'weekday', 'ADD GPRC': 'weekday', 'ALGYDC WARD': 'weekday',
                   'ADD ALLERGY DAY UNIT': 'weekday', 'ADD CR': 'weekday', 'ADD NEUREG': 'weekday', 'ADD TXW':'weekday', 'CUH HOME BIRTH': 'maternity',
                   'ADD FCH': 'weekday', 'ADD PHG': 'weekday', 'ADD CRJAPSUR': 'weekday', 'ADD CORNREV': 'weekday', 'ADD MKO': 'weekday', 'ADD CNPHY43': 'weekday',
                   'ADD LEAPCON': 'weekday', 'ADD CAU': 'weekday', 'ADD AHNR':'weekday',  'ADD UROLP': 'weekday', 'ADDFIBROSCAN': 'weekday',
                   'ADD VASCSURV':'weekday',  'ADD MBR': 'weekday', 'ADD DE': 'weekday', 'ROS NURSEPMB': 'weekday', 'ADD PMIC':'weekday', 'ADD JMW': 'weekday',
                   'ADD RJW': 'weekday', 'ADD ALCC': 'weekday', 'ADD UVP': 'weekday', 'ADD AJCGEN': 'weekday', 'ADD CCH': 'weekday', 'ADD DMOSVRC': 'weekday',
                   'ADD PUVATL':'weekday', 'ADD JOAMD' : 'weekday','ADD AGO': 'weekday', 'C8 WARD': 'orthopaedic ward', 'ADD GPRCB':'weekday',  'ADD PFWO': 'weekday',
                   'ADD JB':'weekday',  'ADD SMK': 'weekday', 'ADD CJB': 'weekday',  'CUH PFWON': 'weekday' ,'ADD LMSH': 'weekday', 'ADD JLU': 'weekday',
                   'ADD CONSFOOT': 'weekday', 'ADD HEPNEW': 'weekday', 'ADD KESPB': 'weekday', 'ADD OTHOTNEU': 'weekday', 'ADD SKIN': 'weekday',
                   'ADD GMTS': 'weekday', 'ADD SMCEF': 'weekday', 'ROS PPMD': 'weekday', 'ADD NFLL': 'weekday', 'ADD LTX': 'weekday', 'CUH GPRCN': 'weekday',
                   'ADD SNSK': 'weekday', 'ADD KV': 'weekday', 'ADD NS': 'weekday', 'CUH NGSHAV': 'weekday', 'ADD SKAMP': 'weekday', 'CCRC Endo':'weekday',  'ADD RDPFP': 'weekday'}


ICU_combined_min_dict = {'ADD A3 WARD': 'neurosurgery ward', 'ADD A4 WARD': 'neurosurgery ward',
                   'ADD A5 WARD': 'neurosurgery ward', 'ADD D6 WARD': 'neurosurgery ward',
                   'ADD CLINICAL DECN UNIT': 'CDU ward', 'ADD CT': 'CT',
                   'ADD ECHO1': 'echo', 'ADD EMERGENCY DEPT': 'AE',
                   'ADD GENRAD': 'XR', 'ADD IRAD': 'IR',
                   'ADD J2 WARD': 'surgical ward', 'ADD J2-C3 WARD': 'PICU',
                   'ADD MAIN THEATRE': 'theatre', 'ADD MAIN THEATRE 04':'theatre',
                   'ADD MAIN THEATRE 22': 'neuro theatre', 'ADD MRI': 'MRI',
                   'ADD NEURO ICU': 'ICU', 'ADD NEURO THEATRE': 'theatre',
                   'ADD NEURO THEATRE 1': 'theatre', 'ADD US': 'US',
                   'ADD CUH EXT FILM': 'external radiology', 'ADD POST-DISCHARGE': 'discharge',
                   'discharge': 'discharge', 'ADD C5 WARD': 'medical ward',
                   'ADD D10': 'medical ward', 'ADD D8 WARD': 'orthopaedic ward',
                   'ADD D9 WARD': 'medical ward', 'ADD DISCHARGE LOUNGE': 'discharge',
                   'ADD FLUORO': 'fluoroscopy', 'ADD GENERAL ICU': 'ICU',
                   'ADD LSFOOT': 'clinic', 'ADD MAIN THEATRE 20': 'theatre',
                   'ADD NEURO THEATRE 2': 'theatre', 'ADD NEURO THEATRE 3': 'theatre',
                   'ADD NEUROPHY': 'clinic', 'ADD PET': 'PET',
                   'ADD REHAB UNIT': 'rehab', 'ADD RT TRT': 'clinic',
                   'Endo Ward': 'clinic', 'ADD D4 IDA UNIT': 'HDU','ADD L2 WARD' : 'surgical ward',
                   'ADD MAIN THEATRE 16': 'theatre', 'ADD R2 WARD': 'rehab',
                   'ADD K3 WARD': 'medical ward', 'ADD G4 WARD': 'medical ward',
                   'ADD L4 WARD': 'surgical ward', 'ADD L5 WARD': 'surgical ward',
                   'ADD C4 WARD': 'medical ward', 'ADD ATC THEATRE': 'theatre',
                   'ADD ATC THEATRE 31': 'theatre', 'ADD ATC THEATRE 32': 'theatre',
                   'ADD ATC THEATRE 36': 'theatre', 'ADD ATC THEATRE 33': 'theatre',
                   'ADD ATC THEATRE 34': 'theatre', 'ADD M4 WARD': 'surgical ward',
                   'ROS DAPHNE WARD': 'gynae surgical ward', 'ADD PRE-ADMISSION':'AE',
                   'ADD ATC THEATRE 35': 'theatre', 'ADD C10 WARD': 'medical ward','ADD C3 WARD': 'paediatric ward',
                   'ADD D10 WARD': 'medical ward', 'ADD CATH ROOM': 'angio',
                   'ADD CORONARY CARE UNIT': 'HDU', 'ADD DIALYSIS UNIT': 'clinic',
                   'ADD K2 WARD': 'medical ward', 'ADD MAIN THEATRE 17': 'theatre',
                   'ADD D5 WARD': 'medical ward', 'ADD D6H WARD': 'medical ward','ADD C9 WARD': 'medical ward',
                   'ADD D7 WARD': 'medical ward', 'ADD C7 WARD': 'surgical ward','ADD C6 WARD': 'medical ward',
                   'ADD C8 WARD': 'orthopaedic ward',  'ADD EAU4 WARD': 'medical ward', 'ADD C2 WARD': 'paediatric ward','ADD D2 WARD': 'paediatric ward',
                   'ADD F6 WARD': 'medical ward', 'ADD G6 WARD': 'medical ward',
                   'ADD F5 WARD': 'acute medical ward', 'ADD G5 WARD': 'medical ward',
                   'ADD F4 WARD': 'medical ward', 'ADD G3 WARD': 'medical ward',
                   'ADD F3 WARD': 'paediatric ward', 'ADD K2 TOE/CARDIOVERSION': 'TOE',
                   'ADD M5 WARD': 'surgical ward', 'ADD MAIN THEATRE 08': 'theatre',
                   'ADD MED S-STAY UNIT': 'medical ward', 'ADD N2 WARD': 'medical ward',
                   'ADD N3 WARD': 'medical ward', 'ADD RT REV': 'clinic',
                   'ADD TRANSPLANT HDU': 'HDU', 'ADD ADDOPTHIMG14': 'clinic','ADD ADDOPTHIMG3': 'clinic','ADD ADDOPTHIMGVF': 'clinic',
                   'ADD BMF': 'clinic', 'ADD DAY SURGERY UNIT': 'clinic',
                   'ADD MAIN THEATRE 03': 'theatre', 'ADD MAIN THEATRE 05': 'theatre',
                   'ADD MAIN THEATRE 01': 'theatre', 'ADD MAIN THEATRE 02': 'theatre',
                   'ADD MAIN THEATRE 09': 'theatre', 'ADD MAIN THEATRE 10': 'theatre',
                   'ADD MAIN THEATRE 11': 'theatre', 'ADD MAIN THEATRE 12': 'theatre',
                   'ADD MAIN THEATRE 14': 'theatre', 'ADD MAIN THEATRE 15': 'theatre',
                   'ADD MAIN THEATRE 18': 'theatre', 'ADD MAIN THEATRE 19': 'theatre',
                   'ADD MAIN THEATRE 23': 'theatre', 'ADD MAIN THEATRE 21': 'theatre',
                   'ADD MAIN THEATRE 06': 'theatre', 'ADD MAIN THEATRE 07': 'theatre',
                   'ADD OIR RECOVERY': 'clinic', 'ADD SURG DISCH LOUNGE': 'discharge',
                   'ADD ADREHAB': 'rehab', 'ADD DENTALX': 'XR',
                   'ADD EMMF': 'clinic', 'ADD GII': 'medical ward',
                   'ADD ORTHOP': 'clinic', 'ADD OTHOTMON': 'clinic',
                   'CUH EXT FILM': 'external radiology', 'ADD PFWON': 'clinic',
                   'ROS MRI SCAN': 'MRI', 'VAU WARD': 'VA',
                   'ADD EAU5 WARD': 'medical ward', 'ADD PPMFU': 'clinic','ADD EAU3 WARD': 'medical ward',
                   'ADD CL8': 'clinic', 'ADD OBS US': 'US',
                   'ADD CNPHY': 'NP', 'ADD AAA': 'clinic',
                   'ADD FANREHA': 'rehab','ADD G2 WARD': 'medical ward',
                   'ADD OTHOTATY': 'clinic', 'ADD STOMA': 'clinic',
                   'CUHTAANKGLAU': 'clinic', 'ADD EMEYE': 'clinic',
                   'ADD EMMO': 'clinic', 'ADD EYE UNIT DAYCASES': 'clinic',
                   'ADD EYE UNIT THEATRE': 'theatre', 'CUH ELY DAY SURG UNIT': 'clinic',
                   'ADD E10 WARD': 'medical ward', 'ROS CYSTOMCS': 'clinic',
                   'ROS GONC': 'clinic', 'ADD ENTX': 'clinic',
                   'ADD DIAGVEST':'clinic','ADD JRM':'clinic','ADD HFT':'clinic','ADD LFT':'clinic',
                   'ADD NM':'clinic', 'ADD PDHU':'clinic', 'ADD RBJNEPH': 'clinic',
                   'ADD AIADAR': 'clinic', 'ADD TXM': 'clinic','ADD LVR':'clinic', 'ADD WTUOC':'clinic',
                   'ADD JODR': 'clinic','ADD AHNREF':'clinic','ADD NJAUOC':'clinic','ADD JMDW':'clinic',
                   'ADD ACF': 'clinic', 'ADD DKNAMD':'clinic', 'ADD EABC':'clinic', 'ADD MRDB':'clinic',
                   'ADD UDA':'clinic', 'ADD POADSU': 'clinic', 'ADD POAOSDSU':'clinic',
                   'ADD AJCUOCW':'clinic','ADD SJM':'clinic','ADD SMBRECON': 'clinic', 'ADD SRGAMB': 'clinic',
                   'ADD LVRF':'clinic','ADD KDABI':'clinic', 'ADD NSGYFC':'clinic', 'ADD PSUD':'clinic',
                   'ADD BU':'XR', 'POST-DISCHARGE':'discharge', 'PRE-ADMISSION':'AE',
                   'ADD J3-C3 WARD': 'surgical day ward', 'ADD PAED ICU': 'PICU', 'ADD R3': 'medical ward', 'ADD PLASTIC SURG UNIT': 'surgical ward',
                   'ADD KDA': 'clinic', 'ADDFLEXCYSOP': 'clinic', 'ROS SARA WARD': 'gynae surgical ward', 'ROS MFM': 'maternity', 'ROS DELIVERY UNIT': 'maternity',
                   'ROS ROSIE THEATRE 2': 'theatre', 'ADD GDC': 'clinic', 'ADD ONCOLOGY DAY UNIT': 'clinic', 'ADD AECLINIC': 'clinic',
                   'ROS OBS US': 'US', 'ADD OTHOTESP': 'clinic', 'ADD SNSKF': 'clinic', 'ADDOPTHIMG14':'clinic', 'ADD EMENT': 'clinic',
                   'ADD DSK': 'clinic', 'ADD PMT': 'clinic', 'ROS ROSIE THEATRE 1': 'theatre', 'ROS LADY MARY WARD': 'maternity', 'ADD PACV': 'clinic',
                   'ADD DKNVR': 'clinic',  'ADD EYE UNIT THEATRE 41': 'clinic', 'ADD SURGAMB': 'clinic', 'ADD OTHOTRMC':'clinic',
                   'ADD J3 PICU WARD': 'PICU', 'ADD NEUROONC': 'clinic', 'CUH ELY THEATRE 3': 'clinic', 'ROS UROG': 'clinic',
                   'ADD FCHEM': 'clinic', 'ADD RMAC': 'clinic', 'ADD C9 DAY UNIT': 'medical ward', 'ADD MKTMF': 'clinic','ADD EYE UNIT THEATRE 42': 'theatre', 'ADD ORALCF': 'clinic', 'ADD ALA':'clinic' , 'ADD ADCA': 'clinic', 'ADD DCHIR': 'clinic',
                   'L4 WARD': 'surgical ward', 'ADD LITHO': 'clinic','ADD MLBV': 'clinic', 'ADDKKSTPHCL1': 'clinic', 'ADD ARNO': 'clinic', 'ADD ENT': 'clinic',
                   'ADD ORALNK': 'clinic', 'ADDSALHSTONE': 'clinic', 'ADD DVT': 'clinic', 'ADD LEAP': 'clinic', 'ADD ANGED': 'clinic', 'ADD MP': 'clinic',
                   'ADD ARNOF': 'clinic', 'F3 WARD': 'paediatric ward', 'ADD KKSTF':'clinic',  'ADD SO': 'clinic', 'ADD CROPP': 'rehab', 'ADD PJM3': 'clinic',
                   'ADD TPBAC': 'clinic', 'ADD HHSC': 'clinic', 'ADD PAED DAY UNIT': 'clinic', 'ADD JOMR': 'clinic', 'ADD SM': 'clinic',
                   'ADDOPTHIMGVF': 'clinic', 'ADD AMBIPN3': 'clinic', 'ADD PAEDAUD': 'clinic' ,'ADD NASHC': 'clinic', 'ADD BPHYT': 'clinic',
                   'ADD CARDPP': 'clinic', 'ADD PDHUF': 'clinic', 'NICU WARD': 'PICU', 'M5 WARD': 'surgical ward', 'ADD CJGG': 'clinic',  'ADD TXT': 'clinic',
                   'ADD PDCCAP': 'clinic', 'ADD EIUNET': 'clinic', 'ADD POAF2F': 'clinic ', 'ADD ALC43': 'clinic', 'ADD NSGYPAED': 'clinic',
                   'ADD EMEWA': 'clinic', 'ADD LVA': 'clinic', 'ADD RMIL': 'clinic',  'ADD CAUFUTEL': 'clinic', 'ADD HMF': 'maternity', 'ADD JTKM': 'clinic',
                   'PDU WARD': 'clinic', 'ADD BMUTN': 'clinic', 'ADD EMSAC': 'clinic', 'ADD PPMBS': 'clinic', 'ADD ACPRUOC':'clinic', 'ADD OPLAOP': 'clinic',
                   'ADD GICH': 'clinic', 'ADD PENT': 'clinic', 'ADD RATRG': 'clinic',  'ADD COLSB': 'clinic', 'ADD CRG': 'clinic', 'ADD LCWVASC': 'clinic',
                   'ROS MADU': 'maternity', 'ADD HAEMOP': 'clinic', 'ADD PRIMARY': 'clinic', 'ADD TNM':'clinic' , 'ADD DXACCESS': 'clinic', 'G2 WARD' : 'medical ward',
                   'ADD PPMBSK2': 'clinic', 'ADD MAIN RECOVERY': 'recovery', 'ADD PDH': 'clinic', 'ADD AIAD': 'clinic' ,
                   'ADD ENDOSCOPY UNIT': 'endoscopy', 'ADD IMPREHAB': 'rehab', 'ADD CDMSLD': 'clinic', 'ADD PJPU': 'clinic', 'ADD YML': 'physio',
                   'ADD PJNK': 'clinic', 'ADD NEUROTR': 'clinic', 'ADD MSR': 'clinic', 'ADD KRM': 'clinic', 'ADD PJ': 'clinic', 'ADD PHYL': 'physio',
                   'ADD ORALVSAN':'clinic',  'ADD MOSOP': 'clinic', 'ADD AJCUOC': 'clinic', 'ADD TKKHL': 'clinic', 'ADD EMSMHC':'clinic',
                   'ADD NEJENT': 'clinic', 'ADD JPF': 'clinic', 'ADD EIACA': 'clinic', 'ADD UROLA': 'clinic', 'E10 WARD': 'medical ward', 'ADD GMTSEF': 'clinic',
                   'ADD APCCOMB': 'clinic', 'ADD MLEDAR': 'clinic', 'ADD NPDV': 'clinic', 'ADDOTHOTORTH': 'clinic', 'ADD AJM': 'clinic',
                   'ADD PDHUEF': 'clinic', 'ADD SNSKEF': 'clinic', 'ADD D5 DAY CASE UNIT': 'surgical ward', 'ADD MPFC': 'clinic','ADD MPS': 'clinic',
                   'ADD PHYE': 'physio', 'ADD PMTSN':'clinic', 'ADD CNPHYR3': 'clinic', 'ADD PHYSD': 'physio', 'ROS GAH': 'clinic', 'ADD GMTSF': 'clinic',
                   'ADD KFTE': 'clinic', 'ADD MPMPP': 'clinic', 'ADD VASC ACC DAY UNIT': 'clinic', 'ADD JNAUOC': 'clinic', 'ROS EGDW': 'XR',
                   'CUH SW RAD': 'clinic', 'ADD SMC':'clinic',  'ADD AHNRD': 'clinic', 'ADD VK': 'clinic', 'ADD DRWJT': 'clinic' ,'G5 WARD': 'medical ward',
                   'ADD NTRECON': 'clinic', 'ADD AMBPEN3': 'clinic', 'ADD MRB': 'clinic', 'ADD NEUROREG': 'clinic', 'ADD IBDTEL': 'clinic',
                   'ADD RGTD2': 'clinic', 'ADD THR': 'clinic', 'ADD CBUR': 'clinic', 'ADD THEATRE 12 DC UNIT': 'theatre', 'ADD MKF': 'clinic',
                   'ADD DEXA': 'XR', 'ADD CARDK2': 'clinic', 'ADD DSCP': 'clinic', 'ADD MSI': 'clinic' ,'ADD OTHOTDST': 'clinic', 'ADD ENTOTO': 'clinic',
                   'ROS CHARLES WOLFSON WD': 'paediatric ward', 'ROS ROSIE BIRTH CENTRE': 'maternity', 'ADD GYNRT': 'clinic', 'ROS EPUDW': 'maternity',
                   'ADD PSOPGN': 'clinic', 'ADD DGUGI':'clinic',  'ADD NRH': 'clinic', 'ADD ECEP': 'clinic', 'ADD DMOS': 'clinic', 'ADD LDC': 'clinic',
                   'ADD AR1F': 'clinic', 'ADD AMFU': 'clinic', 'ADD CATARACT': 'clinic', 'ROS SCHDPROC': 'maternity', 'ADD CAMHS': 'clinic',
                   'ADD OPLAKDA': 'clinic', 'CUH TKKHC': 'clinic', 'ADD MGEND': 'clinic', 'ADD GPRC': 'clinic', 'ALGYDC WARD': 'clinic',
                   'ADD ALLERGY DAY UNIT': 'clinic', 'ADD CR': 'clinic', 'ADD NEUREG': 'clinic', 'ADD TXW':'clinic', 'CUH HOME BIRTH': 'maternity',
                   'ADD FCH': 'clinic', 'ADD PHG': 'clinic', 'ADD CRJAPSUR': 'clinic', 'ADD CORNREV': 'clinic', 'ADD MKO': 'clinic', 'ADD CNPHY43': 'clinic',
                   'ADD LEAPCON': 'clinic', 'ADD CAU': 'clinic', 'ADD AHNR':'clinic',  'ADD UROLP': 'clinic', 'ADDFIBROSCAN': 'clinic',
                   'ADD VASCSURV':'clinic',  'ADD MBR': 'clinic', 'ADD DE': 'clinic', 'ROS NURSEPMB': 'clinic', 'ADD PMIC':'clinic', 'ADD JMW': 'clinic',
                   'ADD RJW': 'clinic', 'ADD ALCC': 'clinic', 'ADD UVP': 'clinic', 'ADD AJCGEN': 'clinic', 'ADD CCH': 'clinic', 'ADD DMOSVRC': 'clinic',
                   'ADD PUVATL':'clinic', 'ADD JOAMD' : 'clinic','ADD AGO': 'clinic', 'C8 WARD': 'orthopaedic ward', 'ADD GPRCB':'clinic',  'ADD PFWO': 'clinic',
                   'ADD JB':'clinic',  'ADD SMK': 'clinic', 'ADD CJB': 'clinic',  'CUH PFWON': 'clinic' ,'ADD LMSH': 'clinic', 'ADD JLU': 'clinic',
                   'ADD CONSFOOT': 'clinic', 'ADD HEPNEW': 'clinic', 'ADD KESPB': 'clinic', 'ADD OTHOTNEU': 'clinic', 'ADD SKIN': 'clinic',
                   'ADD GMTS': 'clinic', 'ADD SMCEF': 'clinic', 'ROS PPMD': 'clinic', 'ADD NFLL': 'clinic', 'ADD LTX': 'clinic', 'CUH GPRCN': 'clinic',
                   'ADD SNSK': 'clinic', 'ADD KV': 'clinic', 'ADD NS': 'clinic', 'CUH NGSHAV': 'clinic', 'ADD SKAMP': 'clinic', 'CCRC Endo':'clinic',
                   'ADD RDPFP': 'clinic','ADD IMA':'clinic', 'ADDALCGNLYR3':'clinic', 'ADD JTKMEF':'clinic', 'ADD LUCENTOP': 'clinic', 'ADD PSC': 'clinic', 'ADD SORD': 'clinic', 'THEATRE':'theatre'}



location_category_map = ICU_combined_min_dict

all_t_strain['from_category'] = all_t_strain['from_loc'].map(location_category_map)

missing_locations = all_t_strain[all_t_strain['from_category'].isnull()]['from_loc'].unique()
print(missing_locations)


all_t_strain['to_category'] = all_t_strain['to_loc'].map(location_category_map)

list_from_wards = all_t_strain.from_category.unique()
print(list_from_wards)
#all_t_strain.to_csv('transfers_strain_icu.csv', header=True, index=False)
all_t_strain.to_csv('transfers_strain_all_adult.csv', header=True, index=False)
print('transfer file with cat and strain written')

#
#
#
#
