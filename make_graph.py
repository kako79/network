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

#def get_weekend_list(alldata):
#    #weekend_admissions = alldata[alldata['admission_time'].get_weekday() == True]
#    weekend_admissions = alldata[alldata['admission_time'].weekday() == '5' or alldata['admission_time'].weekday() == '6']
#    #weekend_admissions = alldata.loc[alldata['admission_time'].get_weekday() == 'Saturday' ]
#    return weekend_admissions

def is_weekend(date):
    #print(date)
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
    #d = datetime.strptime(date, '%Y-%m-%d %H:%M:%S')
    #print(d)
    return d.isoweekday() % 7 < 2



#adm_data = alldata['dt_adm']
#adm_data.to_csv('adm_data_only.csv', header=True, index=False)


print('reading in done')


#need to make an assignment of the individual wards to a category eg surgical ward, outlier, high dependency...



#this is the main dictionary
ward_dict_cat = {'ADD A3 WARD': 'neurosurgical ward', 'ADD A4 WARD': 'neurosurgical ward',
                   'ADD A5 WARD': 'neurosurgical ward', 'ADD D6 WARD': 'neurosurgical ward',
                   'ADD CLINICAL DECN UNIT': 'CDU ward', 'ADD CT': 'CT scan',
                   'ADD ECHO1': 'echo', 'ADD EMERGENCY DEPT': 'AE',
                   'ADD GENRAD': 'radiology', 'ADD IRAD': 'interv rad',
                   'ADD J2 WARD': 'surgical day ward', 'ADD J2-C3 WARD': 'PICU',
                   'ADD MAIN THEATRE': 'theatre', 'ADD MAIN THEATRE 04':'emergency theatre',
                   'ADD MAIN THEATRE 22': 'neuro theatre', 'ADD MRI': 'mri',
                   'ADD NEURO ICU': 'NCCU', 'ADD NEURO THEATRE': 'neuro theatre',
                   'ADD NEURO THEATRE 1': 'neuro theatre', 'ADD US': 'US',
                  'ADD CUH EXT FILM': 'external radiology', 'ADD POST-DISCHARGE': 'discharge',
                   'discharge': 'discharge', 'ADD C5 WARD': 'general medical ward',
                   'ADD D10': 'general medical ward', 'ADD D8 WARD': 'orthopaedic ward',
                   'ADD D9 WARD': 'general medical ward', 'ADD DISCHARGE LOUNGE': 'disch lounge',
                   'ADD FLUORO': 'fluoroscopy', 'ADD GENERAL ICU': 'ICU',
                  'ADD LSFOOT': 'outpatient', 'ADD MAIN THEATRE 20': 'theatre',
                   'ADD NEURO THEATRE 2': 'neuro theatre', 'ADD NEURO THEATRE 3': 'neuro theatre',
                   'ADD NEUROPHY': 'neurophysiology', 'ADD PET': 'PET',
                   'ADD REHAB UNIT': 'rehab', 'ADD RT TRT': 'RT treatment',
                   'Endo Ward': 'endoscopy', 'ADD D4 IDA UNIT': 'HDU','ADD L2 WARD' : 'surgical day ward',
                   'ADD MAIN THEATRE 16': 'theatre', 'ADD R2 WARD': 'rehab',
                   'ADD K3 WARD': 'cardiology ward', 'ADD G4 WARD': 'general medical ward',
                   'ADD L4 WARD': 'ATC surgical ward', 'ADD L5 WARD': 'ATC surgical ward',
                   'ADD C4 WARD': 'acute medical ward', 'ADD ATC THEATRE': 'theatre',
                   'ADD ATC THEATRE 31': 'theatre', 'ADD ATC THEATRE 32': 'theatre',
                   'ADD ATC THEATRE 36': 'theatre', 'ADD ATC THEATRE 33': 'theatre',
                   'ADD ATC THEATRE 34': 'theatre', 'ADD M4 WARD': 'ATC surgical ward',
                   'ROS DAPHNE WARD': 'gynae surgical ward', 'ADD PRE-ADMISSION':'admission',
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
                   'ADD CL8': 'ortho appt', 'ADD OBS US': 'US',
                   'ADD CNPHY': 'neurophysiology', 'ADD AAA': 'other',
                   'ADD FANREHA': 'rehab','ADD G2 WARD': 'general medical ward',
                   'ADD OTHOTATY': 'ophth appt', 'ADD STOMA': 'medical appt',
                   'CUHTAANKGLAU': 'ophth appt', 'ADD EMEYE': 'ophth appt',
                   'ADD EMMO': 'medical appt', 'ADD EYE UNIT DAYCASES': 'theatre eye',
                   'ADD EYE UNIT THEATRE': 'theatre eye', 'CUH ELY DAY SURG UNIT': 'theatre ely',
                   'ADD E10 WARD': 'general medical ward', 'ROS CYSTOMCS': 'gynae appt',
                   'ROS GONC': 'gynae appt', 'ADD ENTX': 'ent appt',
                   'ADD DIAGVEST':'other','ADD JRM':'other','ADD HFT':'other','ADD LFT':'other',
                   'ADD NM':'other', 'ADD PDHU':'general surgical appt', 'ADD RBJNEPH': 'other',
                   'ADD AIADAR': 'medical appt', 'ADD TXM': 'transplant appt','ADD LVR':'ortho appt', 'ADD WTUOC':'other',
                   'ADD JODR': 'general surgical appt','ADD AHNREF':'medical appt','ADD NJAUOC':'other','ADD JMDW':'general surgical appt',
                   'ADD ACF': 'nephro appt', 'ADD DKNAMD':'opth appt', 'ADD EABC':'gastro appt', 'ADD MRDB':'cardiology appt',
                   'ADD UDA':'oral surgery appt', 'ADD POADSU': 'anaesthetic assess', 'ADD POAOSDSU':'anaesthetic assess',
                   'ADD AJCUOCW':'urology appt','ADD SJM':'surgery appt','ADD SMBRECON': 'urology appt', 'ADD SRGAMB': 'surgery appt',
                   'ADD LVRF':'trauma appt','ADD KDABI':'plastic surgery appt', 'ADD NSGYFC':'neurosurgery appt', 'ADD PSUD':'plastic surgery appt',
                   'ADD BU':'radiology', 'POST-DISCHARGE':'discharge', 'PRE-ADMISSION':'admission', 'ADD J3-C3 WARD': 'surgical day ward', 'ADD PAED ICU': 'PICU',
                   'ADD R3': 'general medical ward', 'ADD PLASTIC SURG UNIT': 'surgical day ward',
                   'ADD KDA': 'weekday', 'ADDFLEXCYSOP': 'urology appt', 'ROS SARA WARD': 'gynae surgical ward', 'ROS MFM': 'maternity', 'ROS DELIVERY UNIT': 'maternity',
                   'ROS ROSIE THEATRE 2': 'rosie theatre', 'ADD GDC': 'medical appt', 'ADD ONCOLOGY DAY UNIT': 'medical appt', 'ADD AECLINIC': 'paed appt',
                   'ROS OBS US': 'US', 'ADD OTHOTESP': 'ophth appt', 'ADD SNSKF': 'trauma appt', 'ADDOPTHIMG14':'ophth appt', 'ADD EMENT': 'other',
                   'ADD DSK': 'medical appt', 'ADD PMT': 'medical appt', 'ROS ROSIE THEATRE 1': 'rosie theatre', 'ROS LADY MARY WARD': 'maternity', 'ADD PACV': 'general surgical appt',
                   'ADD DKNVR': 'other',  'ADD EYE UNIT THEATRE 41': 'theatre eye', 'ADD SURGAMB': 'general surgery appt', 'ADD OTHOTRMC':'ophth appt',
                   'ADD J3 PICU WARD': 'PICU', 'ADD NEUROONC': 'medical appt', 'CUH ELY THEATRE 3': 'theatre ely', 'ROS UROG': 'gynae appt',
                   'ADD FCHEM': 'medical appt', 'ADD RMAC': 'trauma appt', 'ADD C9 DAY UNIT': 'general medical ward', 'ADD MKTMF': 'general surgical appt',
                   'ADD EYE UNIT THEATRE 42': 'theatre', 'ADD ORALCF': 'general surgical appt', 'ADD ALA':'medical appt' , 'ADD ADCA': 'ortho appt', 'ADD DCHIR': 'medical appt',
                   'L4 WARD': 'general surgical ward', 'ADD LITHO': 'urology appt','ADD MLBV': 'ENT appt', 'ADDKKSTPHCL1': 'gastro appt', 'ADD ARNO': 'ortho appt', 'ADD ENT': 'ent appt',
                   'ADD ORALNK': 'maxfax appt', 'ADDSALHSTONE': 'appt', 'ADD DVT': 'appt', 'ADD LEAP': 'ophth appt', 'ADD ANGED': 'neuro appt', 'ADD MP': 'general surgical appt',
                   'ADD ARNOF': 'ortho appt', 'F3 WARD': 'paediatric ward', 'ADD KKSTF':'general surgical appt',  'ADD SO': 'appt', 'ADD CROPP': 'rehab', 'ADD PJM3': 'appt',
                   'ADD TPBAC': 'other', 'ADD HHSC': 'other', 'ADD PAED DAY UNIT': 'paed day unit', 'ADD JOMR': 'other', 'ADD SM': 'appt',
                   'ADDOPTHIMGVF': 'ophth appt', 'ADD AMBIPN3': 'general surgical appt', 'ADD PAEDAUD': 'paed appt' ,'ADD NASHC': 'hepat appt', 'ADD BPHYT': 'medical appt',
                   'ADD CARDPP': 'medical appt', 'ADD PDHUF': 'appt', 'NICU WARD': 'PICU', 'M5 WARD': 'ATC surgical ward', 'ADD CJGG': 'appt',  'ADD TXT': 'transplant appt',
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
                   'ADD SNSK': 'ortho appt', 'ADD KV': 'general surgical appt', 'ADD NS': 'medical appt', 'CUH NGSHAV': 'medical appt', 'ADD SKAMP': 'other', 'CCRC Endo':'other',  'ADD RDPFP': 'other',
                    'ADD IMA': 'gastro appt', 'ADDALCGNLYR3': 'neurol appt', 'ADD JTKMEF': 'trauma appt', 'ADD LUCENTOP': 'ophth appt', 'ADD PSC': 'cardiology appt', 'ADD SORD': 'medical appt'}

ward_dict_nocat = {'ADD A3 WARD': 'A3 ward', 'ADD A4 WARD': 'A4 ward',
                    'ADD A5 WARD': 'A5 ward', 'ADD D6 WARD': 'D6 ward',
                   'ADD CLINICAL DECN UNIT': 'CDU ward', 'ADD CT': 'CT scan',
                   'ADD ECHO1': 'echo', 'ADD EMERGENCY DEPT': 'AE',
                   'ADD GENRAD': 'radiology', 'ADD IRAD': 'interv rad',
                   'ADD J2 WARD': 'J2 ward', 'ADD J2-C3 WARD': 'PICU',
                   'ADD MAIN THEATRE': 'theatre', 'ADD MAIN THEATRE 04':'emergency theatre',
                   'ADD MAIN THEATRE 22': 'neuro theatre', 'ADD MRI': 'mri',
                   'ADD NEURO ICU': 'NCCU', 'ADD NEURO THEATRE': 'neuro theatre',
                   'ADD NEURO THEATRE 1': 'neuro theatre', 'ADD US': 'US',
                  'ADD CUH EXT FILM': 'external radiology', 'ADD POST-DISCHARGE': 'discharge',
                   'discharge': 'discharge', 'ADD C5 WARD': 'C5 ward',
                   'ADD D10': 'D10 ward', 'ADD D8 WARD': 'D8 ward',
                   'ADD D9 WARD': 'D9 ward', 'ADD DISCHARGE LOUNGE': 'disch lounge',
                   'ADD FLUORO': 'fluoroscopy', 'ADD GENERAL ICU': 'ICU',
                  'ADD LSFOOT': 'outpatient', 'ADD MAIN THEATRE 20': 'theatre',
                   'ADD NEURO THEATRE 2': 'neuro theatre', 'ADD NEURO THEATRE 3': 'neuro theatre',
                   'ADD NEUROPHY': 'neurophysiology', 'ADD PET': 'PET',
                   'ADD REHAB UNIT': 'rehab', 'ADD RT TRT': 'RT treatment',
                   'Endo Ward': 'endoscopy', 'ADD D4 IDA UNIT': 'HDU','ADD L2 WARD' : 'surgical day ward',
                   'ADD MAIN THEATRE 16': 'theatre', 'ADD R2 WARD': 'rehab',
                   'ADD K3 WARD': 'cardiology ward', 'ADD G4 WARD': 'G4 ward',
                   'ADD L4 WARD': 'L4 ward', 'ADD L5 WARD': 'L5 ward',
                   'ADD C4 WARD': 'C4 ward', 'ADD ATC THEATRE': 'theatre',
                   'ADD ATC THEATRE 31': 'theatre', 'ADD ATC THEATRE 32': 'theatre',
                   'ADD ATC THEATRE 36': 'theatre', 'ADD ATC THEATRE 33': 'theatre',
                   'ADD ATC THEATRE 34': 'theatre', 'ADD M4 WARD': 'M4 ward',
                   'ROS DAPHNE WARD': 'gynae surgical ward', 'ADD PRE-ADMISSION':'admission',
                   'ADD ATC THEATRE 35': 'theatre', 'ADD C10 WARD': 'C10 ward','ADD C3 WARD': 'paediatric ward',
                   'ADD D10 WARD': 'D10 ward', 'ADD CATH ROOM': 'angiography',
                   'ADD CORONARY CARE UNIT': 'HDU', 'ADD DIALYSIS UNIT': 'dialysis',
                   'ADD K2 WARD': 'K2 ward', 'ADD MAIN THEATRE 17': 'theatre',
                   'ADD D5 WARD': 'D5 ward', 'ADD D6H WARD': 'D6H ward','ADD C9 WARD': 'C9 ward',
                   'ADD D7 WARD': 'D7 ward', 'ADD C7 WARD': 'C7 ward','ADD C6 WARD': 'C6 ward',
                   'ADD C8 WARD': 'C8 ward',  'ADD EAU4 WARD': 'EAU4 ward', 'ADD C2 WARD': 'C2 ward','ADD D2 WARD': 'D2 ward',
                   'ADD F6 WARD': 'F6 ward', 'ADD G6 WARD': 'G6 ward',
                   'ADD F5 WARD': 'F5 ward', 'ADD G5 WARD': 'G5 ward',
                   'ADD F4 WARD': 'F4 ward', 'ADD G3 WARD': 'G3 ward',
                   'ADD F3 WARD': 'F3 ward', 'ADD K2 TOE/CARDIOVERSION': 'toe',
                   'ADD M5 WARD': 'M5 ward', 'ADD MAIN THEATRE 08': 'theatre',
                   'ADD MED S-STAY UNIT': 'medical short stay ward', 'ADD N2 WARD': 'N2 ward',
                   'ADD N3 WARD': 'N3 ward', 'ADD RT REV': 'outpatient',
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
                   'ADD EMMF': 'medical appt', 'ADD GII': 'GII ward',
                   'ADD ORTHOP': 'ortho appt', 'ADD OTHOTMON': 'ophth appt',
                   'CUH EXT FILM': 'external radiology', 'ADD PFWON': 'medical appt',
                   'ROS MRI SCAN': 'mri', 'VAU WARD': 'vascular access ward',
                   'ADD EAU5 WARD': 'EAU5 ward', 'ADD PPMFU': 'PPM','ADD EAU3 WARD': 'EAU3 ward',
                   'ADD CL8': 'ortho appt', 'ADD OBS US': 'US',
                   'ADD CNPHY': 'neurophysiology', 'ADD AAA': 'other',
                   'ADD FANREHA': 'rehab','ADD G2 WARD': 'GII ward',
                   'ADD OTHOTATY': 'ophth appt', 'ADD STOMA': 'medical appt',
                   'CUHTAANKGLAU': 'ophth appt', 'ADD EMEYE': 'ophth appt',
                   'ADD EMMO': 'medical appt', 'ADD EYE UNIT DAYCASES': 'theatre eye',
                   'ADD EYE UNIT THEATRE': 'theatre eye', 'CUH ELY DAY SURG UNIT': 'theatre ely',
                   'ADD E10 WARD': 'E10 ward', 'ROS CYSTOMCS': 'gynae appt',
                   'ROS GONC': 'gynae appt', 'ADD ENTX': 'ent appt',
                   'ADD DIAGVEST':'other','ADD JRM':'other','ADD HFT':'other','ADD LFT':'other',
                   'ADD NM':'other', 'ADD PDHU':'general surgical appt', 'ADD RBJNEPH': 'other',
                   'ADD AIADAR': 'medical appt', 'ADD TXM': 'transplant appt','ADD LVR':'ortho appt', 'ADD WTUOC':'other',
                   'ADD JODR': 'general surgical appt','ADD AHNREF':'medical appt','ADD NJAUOC':'other','ADD JMDW':'general surgical appt',
                   'ADD ACF': 'nephro appt', 'ADD DKNAMD':'opth appt', 'ADD EABC':'gastro appt', 'ADD MRDB':'cardiology appt',
                   'ADD UDA':'oral surgery appt', 'ADD POADSU': 'anaesthetic assess', 'ADD POAOSDSU':'anaesthetic assess',
                   'ADD AJCUOCW':'urology appt','ADD SJM':'surgery appt','ADD SMBRECON': 'urology appt', 'ADD SRGAMB': 'surgery appt',
                   'ADD LVRF':'trauma appt','ADD KDABI':'plastic surgery appt', 'ADD NSGYFC':'neurosurgery appt', 'ADD PSUD':'plastic surgery appt',
                   'ADD BU':'radiology', 'POST-DISCHARGE':'discharge', 'PRE-ADMISSION':'admission', 'ADD J3-C3 WARD': 'surgical day ward', 'ADD PAED ICU': 'PICU',
                   'ADD R3': 'general medical ward', 'ADD PLASTIC SURG UNIT': 'surgical day ward',
                   'ADD KDA': 'weekday', 'ADDFLEXCYSOP': 'urology appt', 'ROS SARA WARD': 'gynae surgical ward', 'ROS MFM': 'maternity', 'ROS DELIVERY UNIT': 'maternity',
                   'ROS ROSIE THEATRE 2': 'rosie theatre', 'ADD GDC': 'medical appt', 'ADD ONCOLOGY DAY UNIT': 'medical appt', 'ADD AECLINIC': 'paed appt',
                   'ROS OBS US': 'US', 'ADD OTHOTESP': 'ophth appt', 'ADD SNSKF': 'trauma appt', 'ADDOPTHIMG14':'ophth appt', 'ADD EMENT': 'other',
                   'ADD DSK': 'medical appt', 'ADD PMT': 'medical appt', 'ROS ROSIE THEATRE 1': 'rosie theatre', 'ROS LADY MARY WARD': 'maternity', 'ADD PACV': 'general surgical appt',
                   'ADD DKNVR': 'other',  'ADD EYE UNIT THEATRE 41': 'theatre eye', 'ADD SURGAMB': 'general surgery appt', 'ADD OTHOTRMC':'ophth appt',
                   'ADD J3 PICU WARD': 'PICU', 'ADD NEUROONC': 'medical appt', 'CUH ELY THEATRE 3': 'theatre ely', 'ROS UROG': 'gynae appt',
                   'ADD FCHEM': 'medical appt', 'ADD RMAC': 'trauma appt', 'ADD C9 DAY UNIT': 'C9 ward', 'ADD MKTMF': 'general surgical appt',
                   'ADD EYE UNIT THEATRE 42': 'theatre', 'ADD ORALCF': 'general surgical appt', 'ADD ALA':'medical appt' , 'ADD ADCA': 'ortho appt', 'ADD DCHIR': 'medical appt',
                   'L4 WARD': 'general surgical ward', 'ADD LITHO': 'urology appt','ADD MLBV': 'ENT appt', 'ADDKKSTPHCL1': 'gastro appt', 'ADD ARNO': 'ortho appt', 'ADD ENT': 'ent appt',
                   'ADD ORALNK': 'maxfax appt', 'ADDSALHSTONE': 'appt', 'ADD DVT': 'appt', 'ADD LEAP': 'ophth appt', 'ADD ANGED': 'neuro appt', 'ADD MP': 'general surgical appt',
                   'ADD ARNOF': 'ortho appt', 'F3 WARD': 'paediatric ward', 'ADD KKSTF':'general surgical appt',  'ADD SO': 'appt', 'ADD CROPP': 'rehab', 'ADD PJM3': 'appt',
                   'ADD TPBAC': 'other', 'ADD HHSC': 'other', 'ADD PAED DAY UNIT': 'paed day unit', 'ADD JOMR': 'other', 'ADD SM': 'appt',
                   'ADDOPTHIMGVF': 'ophth appt', 'ADD AMBIPN3': 'general surgical appt', 'ADD PAEDAUD': 'paed appt' ,'ADD NASHC': 'hepat appt', 'ADD BPHYT': 'medical appt',
                   'ADD CARDPP': 'medical appt', 'ADD PDHUF': 'appt', 'NICU WARD': 'PICU', 'M5 WARD': 'ATC surgical ward', 'ADD CJGG': 'appt',  'ADD TXT': 'transplant appt',
                   'ADD PDCCAP': 'urology appt', 'ADD EIUNET': 'other', 'ADD POAF2F': 'anaesthetic assess ', 'ADD ALC43': 'general surgical appt', 'ADD NSGYPAED': 'paed appt',
                   'ADD EMEWA': 'ophth appt', 'ADD LVA': 'ophth appt', 'ADD RMIL': 'general surgical appt',  'ADD CAUFUTEL': 'appt', 'ADD HMF': 'maternity', 'ADD JTKM': 'other',
                   'PDU WARD': 'paediatric day ward', 'ADD BMUTN': 'other', 'ADD EMSAC': 'appt', 'ADD PPMBS': 'appt', 'ADD ACPRUOC':'appt', 'ADD OPLAOP': 'general surgical appt',
                   'ADD GICH': 'medical appt', 'ADD PENT': 'paediatric appt', 'ADD RATRG': 'neuro appt',  'ADD COLSB': ' general surgical appt', 'ADD CRG': 'urology appt', 'ADD LCWVASC': 'general surgical appt',
                   'ROS MADU': 'maternity', 'ADD HAEMOP': 'medical appt', 'ADD PRIMARY': 'other', 'ADD TNM':'urology appt' , 'ADD DXACCESS': 'transplant appt', 'G2 WARD' : 'GII ward',
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
                   'ADD PUVATL':'other', 'ADD JOAMD' : 'medical appt','ADD AGO': 'other', 'C8 WARD': 'C8 ward', 'ADD GPRCB':'other',  'ADD PFWO': 'neurol appt',
                   'ADD JB':'other',  'ADD SMK': 'general surgical appt', 'ADD CJB': 'general surgical appt',  'CUH PFWON': 'neurol appt' ,'ADD LMSH': 'medical appt', 'ADD JLU': ',edical appt',
                   'ADD CONSFOOT': 'medical appt', 'ADD HEPNEW': 'medical appt', 'ADD KESPB': 'medical appt', 'ADD OTHOTNEU': 'other', 'ADD SKIN': 'medical appt',
                   'ADD GMTS': 'ortho appt', 'ADD SMCEF': 'trauma appt', 'ROS PPMD': 'maternity', 'ADD NFLL': 'medical appt', 'ADD LTX': 'transplant appt', 'CUH GPRCN': 'medical appt',
                   'ADD SNSK': 'ortho appt', 'ADD KV': 'general surgical appt', 'ADD NS': 'medical appt', 'CUH NGSHAV': 'medical appt', 'ADD SKAMP': 'other', 'CCRC Endo':'other',  'ADD RDPFP': 'other',
                   'ADD IMA': 'gastro appt', 'ADDALCGNLYR3': 'neurol appt', 'ADD JTKMEF': 'trauma appt', 'ADD LUCENTOP': 'ophth appt', 'ADD PSC': 'cardiology appt', 'ADD SORD': 'medical appt'}


#dictionary for removing weekday influence on node numbers
collated_cat_ward_dict = {'ADD A3 WARD': 'neurosurgery HDU', 'ADD A4 WARD': 'neurosurgery ward',
                   'ADD A5 WARD': 'neurosurgery ward', 'ADD D6 WARD': 'neurosurgery ward',
                   'ADD CLINICAL DECN UNIT': 'CDU ward', 'ADD CT': 'CT scan',
                   'ADD ECHO1': 'echo', 'ADD EMERGENCY DEPT': 'AE',
                   'ADD GENRAD': 'radiology', 'ADD IRAD': 'interv rad',
                   'ADD J2 WARD': 'surgical day ward', 'ADD J2-C3 WARD': 'PICU',
                   'ADD MAIN THEATRE': 'theatre', 'ADD MAIN THEATRE 04':'emergency theatre',
                   'ADD MAIN THEATRE 22': 'neuro theatre', 'ADD MRI': 'MRI',
                   'ADD NEURO ICU': 'NCCU', 'ADD NEURO THEATRE': 'neuro theatre',
                   'ADD NEURO THEATRE 1': 'neuro theatre', 'ADD US': 'US',
                   'ADD CUH EXT FILM': 'external radiology', 'ADD POST-DISCHARGE': 'discharge',
                   'discharge': 'discharge', 'ADD C5 WARD': 'general medical ward',
                   'ADD D10': 'general medical ward', 'ADD D8 WARD': 'orthopaedic ward',
                   'ADD D9 WARD': 'general medical ward', 'ADD DISCHARGE LOUNGE': 'discharge lounge',
                   'ADD FLUORO': 'fluoroscopy', 'ADD GENERAL ICU': 'ICU',
                   'ADD LSFOOT': 'weekday', 'ADD MAIN THEATRE 20': 'theatre',
                   'ADD NEURO THEATRE 2': 'neuro theatre', 'ADD NEURO THEATRE 3': 'neuro theatre',
                   'ADD NEUROPHY': 'weekday', 'ADD PET': 'PET',
                   'ADD REHAB UNIT': 'rehab', 'ADD RT TRT': 'weekday',
                   'Endo Ward': 'weekday', 'ADD D4 IDA UNIT': 'HDU','ADD L2 WARD' : 'surgical day ward',
                   'ADD MAIN THEATRE 16': 'theatre', 'ADD R2 WARD': 'rehab',
                   'ADD K3 WARD': 'cardiology ward', 'ADD G4 WARD': 'general medical ward',
                   'ADD L4 WARD': 'ATC surgical ward', 'ADD L5 WARD': 'ATC surgical ward',
                   'ADD C4 WARD': 'acute medical ward', 'ADD ATC THEATRE': 'theatre',
                   'ADD ATC THEATRE 31': 'theatre', 'ADD ATC THEATRE 32': 'theatre',
                   'ADD ATC THEATRE 36': 'theatre', 'ADD ATC THEATRE 33': 'theatre',
                   'ADD ATC THEATRE 34': 'theatre', 'ADD M4 WARD': 'ATC surgical ward',
                   'ROS DAPHNE WARD': 'gynae surgical ward', 'ADD PRE-ADMISSION':'admission',
                   'ADD ATC THEATRE 35': 'theatre', 'ADD C10 WARD': 'general medical ward','ADD C3 WARD': 'paediatric ward',
                   'ADD D10 WARD': 'general medical ward', 'ADD CATH ROOM': 'angiography',
                   'ADD CORONARY CARE UNIT': 'HDU', 'ADD DIALYSIS UNIT': 'weekday',
                   'ADD K2 WARD': 'cardiology ward', 'ADD MAIN THEATRE 17': 'theatre',
                   'ADD D5 WARD': 'general medical ward', 'ADD D6H WARD': 'general medical ward','ADD C9 WARD': 'general medical ward',
                   'ADD D7 WARD': 'general medical ward', 'ADD C7 WARD': 'general surgical ward','ADD C6 WARD': 'general medical ward',
                   'ADD C8 WARD': 'orthopaedic ward',  'ADD EAU4 WARD': 'acute medical ward', 'ADD C2 WARD': 'paediatric ward','ADD D2 WARD': 'paediatric ward',
                   'ADD F6 WARD': 'general medical ward', 'ADD G6 WARD': 'general medical ward',
                   'ADD F5 WARD': 'acute medical ward', 'ADD G5 WARD': 'general medical ward',
                   'ADD F4 WARD': 'general medical ward', 'ADD G3 WARD': 'general medical ward',
                   'ADD F3 WARD': 'paediatric ward', 'ADD K2 TOE/CARDIOVERSION': 'TOE',
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
                   'ADD OIR RECOVERY': 'weekday', 'ADD SURG DISCH LOUNGE': 'discharge lounge',
                   'ADD ADREHAB': 'rehab', 'ADD DENTALX': 'radiology',
                   'ADD EMMF': 'weekday', 'ADD GII': 'general medical ward',
                   'ADD ORTHOP': 'weekday', 'ADD OTHOTMON': 'weekday',
                   'CUH EXT FILM': 'external radiology', 'ADD PFWON': 'weekday',
                   'ROS MRI SCAN': 'MRI', 'VAU WARD': 'vascular access ward',
                   'ADD EAU5 WARD': 'acute medical ward', 'ADD PPMFU': 'weekday','ADD EAU3 WARD': 'acute medical ward',
                   'ADD CL8': 'weekday', 'ADD OBS US': 'US',
                   'ADD CNPHY': 'weekday', 'ADD AAA': 'weekday',
                   'ADD FANREHA': 'rehab','ADD G2 WARD': 'general medical ward',
                   'ADD OTHOTATY': 'weekday', 'ADD STOMA': 'weekday',
                   'CUHTAANKGLAU': 'weekday', 'ADD EMEYE': 'weekday',
                   'ADD EMMO': 'weekday', 'ADD EYE UNIT DAYCASES': 'weekday',
                   'ADD EYE UNIT THEATRE': 'theatre', 'CUH ELY DAY SURG UNIT': 'weekday',
                   'ADD E10 WARD': 'general medical ward', 'ROS CYSTOMCS': 'weekday',
                   'ROS GONC': 'weekday', 'ADD ENTX': 'weekday',
                   'ADD DIAGVEST':'weekday','ADD JRM':'weekday','ADD HFT':'weekday','ADD LFT':'weekday',
                   'ADD NM':'weekday', 'ADD PDHU':'weekday', 'ADD RBJNEPH': 'weekday',
                   'ADD AIADAR': 'weekday', 'ADD TXM': 'weekday','ADD LVR':'weekday', 'ADD WTUOC':'weekday',
                   'ADD JODR': 'weekday','ADD AHNREF':'weekday','ADD NJAUOC':'weekday','ADD JMDW':'weekday',
                   'ADD ACF': 'weekday', 'ADD DKNAMD':'weekday', 'ADD EABC':'weekday', 'ADD MRDB':'weekday',
                   'ADD UDA':'weekday', 'ADD POADSU': 'weekday', 'ADD POAOSDSU':'weekday',
                   'ADD AJCUOCW':'weekday','ADD SJM':'weekday','ADD SMBRECON': 'weekday', 'ADD SRGAMB': 'weekday',
                   'ADD LVRF':'weekday','ADD KDABI':'weekday', 'ADD NSGYFC':'weekday', 'ADD PSUD':'weekday',
                   'ADD BU':'radiology', 'POST-DISCHARGE':'discharge', 'PRE-ADMISSION':'admission',
                   'ADD J3-C3 WARD': 'surgical day ward', 'ADD PAED ICU': 'PICU', 'ADD R3': 'general medical ward', 'ADD PLASTIC SURG UNIT': 'surgical day ward',
                   'ADD KDA': 'weekday', 'ADDFLEXCYSOP': 'weekday', 'ROS SARA WARD': 'gynae surgical ward', 'ROS MFM': 'maternity', 'ROS DELIVERY UNIT': 'maternity',
                   'ROS ROSIE THEATRE 2': 'rosie theatre', 'ADD GDC': 'weekday', 'ADD ONCOLOGY DAY UNIT': 'weekday', 'ADD AECLINIC': 'weekday',
                   'ROS OBS US': 'US', 'ADD OTHOTESP': 'weekday', 'ADD SNSKF': 'weekday', 'ADDOPTHIMG14':'weekday', 'ADD EMENT': 'weekday',
                   'ADD DSK': 'weekday', 'ADD PMT': 'weekday', 'ROS ROSIE THEATRE 1': 'rosie theatre', 'ROS LADY MARY WARD': 'maternity', 'ADD PACV': 'weekday',
                   'ADD DKNVR': 'weekday',  'ADD EYE UNIT THEATRE 41': 'weekday', 'ADD SURGAMB': 'weekday', 'ADD OTHOTRMC':'weekday',
                   'ADD J3 PICU WARD': 'PICU', 'ADD NEUROONC': 'weekday', 'CUH ELY THEATRE 3': 'weekday', 'ROS UROG': 'weekday',
                   'ADD FCHEM': 'weekday', 'ADD RMAC': 'weekday', 'ADD C9 DAY UNIT': 'general medical ward', 'ADD MKTMF': 'weekday','ADD EYE UNIT THEATRE 42': 'theatre', 'ADD ORALCF': 'weekday', 'ADD ALA':'weekday' , 'ADD ADCA': 'weekday', 'ADD DCHIR': 'weekday',
                   'L4 WARD': 'general surgical ward', 'ADD LITHO': 'weekday','ADD MLBV': 'weekday', 'ADDKKSTPHCL1': 'weekday', 'ADD ARNO': 'weekday', 'ADD ENT': 'weekday',
                   'ADD ORALNK': 'weekday', 'ADDSALHSTONE': 'weekday', 'ADD DVT': 'weekday', 'ADD LEAP': 'weekday', 'ADD ANGED': 'weekday', 'ADD MP': 'weekday',
                   'ADD ARNOF': 'weekday', 'F3 WARD': 'paediatric ward', 'ADD KKSTF':'weekday',  'ADD SO': 'weekday', 'ADD CROPP': 'rehab', 'ADD PJM3': 'weekday',
                   'ADD TPBAC': 'weekday', 'ADD HHSC': 'weekday', 'ADD PAED DAY UNIT': 'weekday', 'ADD JOMR': 'weekday', 'ADD SM': 'weekday',
                   'ADDOPTHIMGVF': 'weekday', 'ADD AMBIPN3': 'weekday', 'ADD PAEDAUD': 'weekday' ,'ADD NASHC': 'weekday', 'ADD BPHYT': 'weekday',
                   'ADD CARDPP': 'weekday', 'ADD PDHUF': 'weekday', 'NICU WARD': 'PICU', 'M5 WARD': 'ATC surgical ward', 'ADD CJGG': 'weekday',  'ADD TXT': 'weekday',
                   'ADD PDCCAP': 'weekday', 'ADD EIUNET': 'weekday', 'ADD POAF2F': 'weekday ', 'ADD ALC43': 'weekday', 'ADD NSGYPAED': 'weekday',
                   'ADD EMEWA': 'weekday', 'ADD LVA': 'weekday', 'ADD RMIL': 'weekday',  'ADD CAUFUTEL': 'weekday', 'ADD HMF': 'maternity', 'ADD JTKM': 'weekday',
                   'PDU WARD': 'weekday', 'ADD BMUTN': 'weekday', 'ADD EMSAC': 'weekday', 'ADD PPMBS': 'weekday', 'ADD ACPRUOC':'weekday', 'ADD OPLAOP': 'weekday',
                   'ADD GICH': 'weekday', 'ADD PENT': 'weekday', 'ADD RATRG': 'weekday',  'ADD COLSB': 'weekday', 'ADD CRG': 'weekday', 'ADD LCWVASC': 'weekday',
                   'ROS MADU': 'maternity', 'ADD HAEMOP': 'weekday', 'ADD PRIMARY': 'weekday', 'ADD TNM':'weekday' , 'ADD DXACCESS': 'weekday', 'G2 WARD' : 'general medical ward',
                   'ADD PPMBSK2': 'weekday', 'ADD MAIN RECOVERY': 'recovery', 'ADD PDH': 'weekday', 'ADD AIAD': 'weekday' ,
                   'ADD ENDOSCOPY UNIT': 'endoscopy', 'ADD IMPREHAB': 'rehab', 'ADD CDMSLD': 'weekday', 'ADD PJPU': 'weekday', 'ADD YML': 'physio',
                   'ADD PJNK': 'weekday', 'ADD NEUROTR': 'weekday', 'ADD MSR': 'weekday', 'ADD KRM': 'weekday', 'ADD PJ': 'weekday', 'ADD PHYL': 'physio',
                   'ADD ORALVSAN':'weekday',  'ADD MOSOP': 'weekday', 'ADD AJCUOC': 'weekday', 'ADD TKKHL': 'weekday', 'ADD EMSMHC':'weekday',
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
                   'ADD SNSK': 'weekday', 'ADD KV': 'weekday', 'ADD NS': 'weekday', 'CUH NGSHAV': 'weekday', 'ADD SKAMP': 'weekday', 'CCRC Endo':'weekday',
                   'ADD RDPFP': 'weekday','ADD IMA':'weekday', 'ADDALCGNLYR3':'weekday', 'ADD JTKMEF':'weekday', 'ADD LUCENTOP': 'weekday', 'ADD PSC': 'weekday', 'ADD SORD': 'weekday'}

nocat_ward_weekday = {'ADD A3 WARD': 'A3', 'ADD A4 WARD': 'A4',
                   'ADD A5 WARD': 'A5', 'ADD D6 WARD': 'D6',
                   'ADD CLINICAL DECN UNIT': 'CDU ward', 'ADD CT': 'CT scan',
                   'ADD ECHO1': 'echo', 'ADD EMERGENCY DEPT': 'AE',
                   'ADD GENRAD': 'radiology', 'ADD IRAD': 'interv rad',
                   'ADD J2 WARD': 'J2', 'ADD J2-C3 WARD': 'PICU',
                   'ADD MAIN THEATRE': 'theatre', 'ADD MAIN THEATRE 04':'emergency theatre',
                   'ADD MAIN THEATRE 22': 'neuro theatre', 'ADD MRI': 'MRI',
                   'ADD NEURO ICU': 'NCCU', 'ADD NEURO THEATRE': 'neuro theatre',
                   'ADD NEURO THEATRE 1': 'neuro theatre', 'ADD US': 'US',
                   'ADD CUH EXT FILM': 'external radiology', 'ADD POST-DISCHARGE': 'discharge',
                   'discharge': 'discharge', 'ADD C5 WARD': 'C5',
                   'ADD D10': 'D10', 'ADD D8 WARD': 'D8',
                   'ADD D9 WARD': 'D9', 'ADD DISCHARGE LOUNGE': 'discharge lounge',
                   'ADD FLUORO': 'fluoroscopy', 'ADD GENERAL ICU': 'ICU',
                   'ADD LSFOOT': 'weekday', 'ADD MAIN THEATRE 20': 'theatre',
                   'ADD NEURO THEATRE 2': 'neuro theatre', 'ADD NEURO THEATRE 3': 'neuro theatre',
                   'ADD NEUROPHY': 'weekday', 'ADD PET': 'PET',
                   'ADD REHAB UNIT': 'rehab', 'ADD RT TRT': 'weekday',
                   'Endo Ward': 'weekday', 'ADD D4 IDA UNIT': 'IDA','ADD L2 WARD' : 'L2',
                   'ADD MAIN THEATRE 16': 'theatre', 'ADD R2 WARD': 'rehab',
                   'ADD K3 WARD': 'K3', 'ADD G4 WARD': 'G4',
                   'ADD L4 WARD': 'L4', 'ADD L5 WARD': 'L5',
                   'ADD C4 WARD': 'C4', 'ADD ATC THEATRE': 'theatre',
                   'ADD ATC THEATRE 31': 'theatre', 'ADD ATC THEATRE 32': 'theatre',
                   'ADD ATC THEATRE 36': 'theatre', 'ADD ATC THEATRE 33': 'theatre',
                   'ADD ATC THEATRE 34': 'theatre', 'ADD M4 WARD': 'M4',
                   'ROS DAPHNE WARD': 'Daphne', 'ADD PRE-ADMISSION':'admission',
                   'ADD ATC THEATRE 35': 'theatre', 'ADD C10 WARD': 'C10','ADD C3 WARD': 'C3',
                   'ADD D10 WARD': 'D10', 'ADD CATH ROOM': 'angiography',
                   'ADD CORONARY CARE UNIT': 'coronary HDU', 'ADD DIALYSIS UNIT': 'weekday',
                   'ADD K2 WARD': 'K2', 'ADD MAIN THEATRE 17': 'theatre',
                   'ADD D5 WARD': 'D5', 'ADD D6H WARD': 'D6H','ADD C9 WARD': 'C9',
                   'ADD D7 WARD': 'D7', 'ADD C7 WARD': 'C7','ADD C6 WARD': 'C6',
                   'ADD C8 WARD': 'C8',  'ADD EAU4 WARD': 'EAU4', 'ADD C2 WARD': 'C2','ADD D2 WARD': 'D2',
                   'ADD F6 WARD': 'F6', 'ADD G6 WARD': 'G6',
                   'ADD F5 WARD': 'F5', 'ADD G5 WARD': 'G5',
                   'ADD F4 WARD': 'F4', 'ADD G3 WARD': 'G3',
                   'ADD F3 WARD': 'F3', 'ADD K2 TOE/CARDIOVERSION': 'TOE',
                   'ADD M5 WARD': 'M5', 'ADD MAIN THEATRE 08': 'theatre',
                   'ADD MED S-STAY UNIT': 'MSSU', 'ADD N2 WARD': 'N2',
                   'ADD N3 WARD': 'N3', 'ADD RT REV': 'weekday',
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
                   'ADD OIR RECOVERY': 'weekday', 'ADD SURG DISCH LOUNGE': 'discharge lounge',
                   'ADD ADREHAB': 'rehab', 'ADD DENTALX': 'radiology',
                   'ADD EMMF': 'weekday', 'ADD GII': 'G2',
                   'ADD ORTHOP': 'weekday', 'ADD OTHOTMON': 'weekday',
                   'CUH EXT FILM': 'external radiology', 'ADD PFWON': 'weekday',
                   'ROS MRI SCAN': 'MRI', 'VAU WARD': 'vascular access',
                   'ADD EAU5 WARD': 'EAU5', 'ADD PPMFU': 'weekday','ADD EAU3 WARD': 'EAU3',
                   'ADD CL8': 'weekday', 'ADD OBS US': 'US',
                   'ADD CNPHY': 'weekday', 'ADD AAA': 'weekday',
                   'ADD FANREHA': 'rehab','ADD G2 WARD': 'G2',
                   'ADD OTHOTATY': 'weekday', 'ADD STOMA': 'weekday',
                   'CUHTAANKGLAU': 'weekday', 'ADD EMEYE': 'weekday',
                   'ADD EMMO': 'weekday', 'ADD EYE UNIT DAYCASES': 'weekday',
                   'ADD EYE UNIT THEATRE': 'theatre', 'CUH ELY DAY SURG UNIT': 'weekday',
                   'ADD E10 WARD': 'E10', 'ROS CYSTOMCS': 'weekday',
                   'ROS GONC': 'weekday', 'ADD ENTX': 'weekday',
                   'ADD DIAGVEST':'weekday','ADD JRM':'weekday','ADD HFT':'weekday','ADD LFT':'weekday',
                   'ADD NM':'weekday', 'ADD PDHU':'weekday', 'ADD RBJNEPH': 'weekday',
                   'ADD AIADAR': 'weekday', 'ADD TXM': 'weekday','ADD LVR':'weekday', 'ADD WTUOC':'weekday',
                   'ADD JODR': 'weekday','ADD AHNREF':'weekday','ADD NJAUOC':'weekday','ADD JMDW':'weekday',
                   'ADD ACF': 'weekday', 'ADD DKNAMD':'weekday', 'ADD EABC':'weekday', 'ADD MRDB':'weekday',
                   'ADD UDA':'weekday', 'ADD POADSU': 'weekday', 'ADD POAOSDSU':'weekday',
                   'ADD AJCUOCW':'weekday','ADD SJM':'weekday','ADD SMBRECON': 'weekday', 'ADD SRGAMB': 'weekday',
                   'ADD LVRF':'weekday','ADD KDABI':'weekday', 'ADD NSGYFC':'weekday', 'ADD PSUD':'weekday',
                   'ADD BU':'radiology', 'POST-DISCHARGE':'discharge', 'PRE-ADMISSION':'admission',
                   'ADD J3-C3 WARD': 'J3 day', 'ADD PAED ICU': 'PICU', 'ADD R3': 'R3', 'ADD PLASTIC SURG UNIT': 'surgical day ward',
                   'ADD KDA': 'weekday', 'ADDFLEXCYSOP': 'weekday', 'ROS SARA WARD': 'sara', 'ROS MFM': 'maternity', 'ROS DELIVERY UNIT': 'maternity',
                   'ROS ROSIE THEATRE 2': 'rosie theatre', 'ADD GDC': 'weekday', 'ADD ONCOLOGY DAY UNIT': 'weekday', 'ADD AECLINIC': 'weekday',
                   'ROS OBS US': 'US', 'ADD OTHOTESP': 'weekday', 'ADD SNSKF': 'weekday', 'ADDOPTHIMG14':'weekday', 'ADD EMENT': 'weekday',
                   'ADD DSK': 'weekday', 'ADD PMT': 'weekday', 'ROS ROSIE THEATRE 1': 'rosie theatre', 'ROS LADY MARY WARD': 'maternity', 'ADD PACV': 'weekday',
                   'ADD DKNVR': 'weekday',  'ADD EYE UNIT THEATRE 41': 'weekday', 'ADD SURGAMB': 'weekday', 'ADD OTHOTRMC':'weekday',
                   'ADD J3 PICU WARD': 'PICU', 'ADD NEUROONC': 'weekday', 'CUH ELY THEATRE 3': 'weekday', 'ROS UROG': 'weekday',
                   'ADD FCHEM': 'weekday', 'ADD RMAC': 'weekday', 'ADD C9 DAY UNIT': 'C9', 'ADD MKTMF': 'weekday','ADD EYE UNIT THEATRE 42': 'theatre', 'ADD ORALCF': 'weekday', 'ADD ALA':'weekday' , 'ADD ADCA': 'weekday', 'ADD DCHIR': 'weekday',
                   'L4 WARD': 'general surgical ward', 'ADD LITHO': 'weekday','ADD MLBV': 'weekday', 'ADDKKSTPHCL1': 'weekday', 'ADD ARNO': 'weekday', 'ADD ENT': 'weekday',
                   'ADD ORALNK': 'weekday', 'ADDSALHSTONE': 'weekday', 'ADD DVT': 'weekday', 'ADD LEAP': 'weekday', 'ADD ANGED': 'weekday', 'ADD MP': 'weekday',
                   'ADD ARNOF': 'weekday', 'F3 WARD': 'F3', 'ADD KKSTF':'weekday',  'ADD SO': 'weekday', 'ADD CROPP': 'rehab', 'ADD PJM3': 'weekday',
                   'ADD TPBAC': 'weekday', 'ADD HHSC': 'weekday', 'ADD PAED DAY UNIT': 'weekday', 'ADD JOMR': 'weekday', 'ADD SM': 'weekday',
                   'ADDOPTHIMGVF': 'weekday', 'ADD AMBIPN3': 'weekday', 'ADD PAEDAUD': 'weekday' ,'ADD NASHC': 'weekday', 'ADD BPHYT': 'weekday',
                   'ADD CARDPP': 'weekday', 'ADD PDHUF': 'weekday', 'NICU WARD': 'NICU', 'M5 WARD': 'M5', 'ADD CJGG': 'weekday',  'ADD TXT': 'weekday',
                   'ADD PDCCAP': 'weekday', 'ADD EIUNET': 'weekday', 'ADD POAF2F': 'weekday ', 'ADD ALC43': 'weekday', 'ADD NSGYPAED': 'weekday',
                   'ADD EMEWA': 'weekday', 'ADD LVA': 'weekday', 'ADD RMIL': 'weekday',  'ADD CAUFUTEL': 'weekday', 'ADD HMF': 'maternity', 'ADD JTKM': 'weekday',
                   'PDU WARD': 'weekday', 'ADD BMUTN': 'weekday', 'ADD EMSAC': 'weekday', 'ADD PPMBS': 'weekday', 'ADD ACPRUOC':'weekday', 'ADD OPLAOP': 'weekday',
                   'ADD GICH': 'weekday', 'ADD PENT': 'weekday', 'ADD RATRG': 'weekday',  'ADD COLSB': 'weekday', 'ADD CRG': 'weekday', 'ADD LCWVASC': 'weekday',
                   'ROS MADU': 'maternity', 'ADD HAEMOP': 'weekday', 'ADD PRIMARY': 'weekday', 'ADD TNM':'weekday' , 'ADD DXACCESS': 'weekday', 'G2 WARD' : 'G2',
                   'ADD PPMBSK2': 'weekday', 'ADD MAIN RECOVERY': 'recovery', 'ADD PDH': 'weekday', 'ADD AIAD': 'weekday' ,
                   'ADD ENDOSCOPY UNIT': 'endoscopy', 'ADD IMPREHAB': 'rehab', 'ADD CDMSLD': 'weekday', 'ADD PJPU': 'weekday', 'ADD YML': 'physio',
                   'ADD PJNK': 'weekday', 'ADD NEUROTR': 'weekday', 'ADD MSR': 'weekday', 'ADD KRM': 'weekday', 'ADD PJ': 'weekday', 'ADD PHYL': 'physio',
                   'ADD ORALVSAN':'weekday',  'ADD MOSOP': 'weekday', 'ADD AJCUOC': 'weekday', 'ADD TKKHL': 'weekday', 'ADD EMSMHC':'weekday',
                   'ADD NEJENT': 'weekday', 'ADD JPF': 'weekday', 'ADD EIACA': 'weekday', 'ADD UROLA': 'weekday', 'E10 WARD': 'E10', 'ADD GMTSEF': 'weekday',
                   'ADD APCCOMB': 'weekday', 'ADD MLEDAR': 'weekday', 'ADD NPDV': 'weekday', 'ADDOTHOTORTH': 'weekday', 'ADD AJM': 'weekday',
                   'ADD PDHUEF': 'weekday', 'ADD SNSKEF': 'weekday', 'ADD D5 DAY CASE UNIT': 'D5', 'ADD MPFC': 'weekday','ADD MPS': 'weekday',
                   'ADD PHYE': 'physio', 'ADD PMTSN':'weekday', 'ADD CNPHYR3': 'weekday', 'ADD PHYSD': 'physio', 'ROS GAH': 'weekday', 'ADD GMTSF': 'weekday',
                   'ADD KFTE': 'weekday', 'ADD MPMPP': 'weekday', 'ADD VASC ACC DAY UNIT': 'weekday', 'ADD JNAUOC': 'weekday', 'ROS EGDW': 'radiology',
                   'CUH SW RAD': 'weekday', 'ADD SMC':'weekday',  'ADD AHNRD': 'weekday', 'ADD VK': 'weekday', 'ADD DRWJT': 'weekday' ,'G5 WARD': 'G5',
                   'ADD NTRECON': 'weekday', 'ADD AMBPEN3': 'weekday', 'ADD MRB': 'weekday', 'ADD NEUROREG': 'weekday', 'ADD IBDTEL': 'weekday',
                   'ADD RGTD2': 'weekday', 'ADD THR': 'weekday', 'ADD CBUR': 'weekday', 'ADD THEATRE 12 DC UNIT': 'theatre', 'ADD MKF': 'weekday',
                   'ADD DEXA': 'radiology', 'ADD CARDK2': 'weekday', 'ADD DSCP': 'weekday', 'ADD MSI': 'weekday' ,'ADD OTHOTDST': 'weekday', 'ADD ENTOTO': 'weekday',
                   'ROS CHARLES WOLFSON WD': 'Wolfson', 'ROS ROSIE BIRTH CENTRE': 'maternity', 'ADD GYNRT': 'weekday', 'ROS EPUDW': 'maternity',
                   'ADD PSOPGN': 'weekday', 'ADD DGUGI':'weekday',  'ADD NRH': 'weekday', 'ADD ECEP': 'weekday', 'ADD DMOS': 'weekday', 'ADD LDC': 'weekday',
                   'ADD AR1F': 'weekday', 'ADD AMFU': 'weekday', 'ADD CATARACT': 'weekday', 'ROS SCHDPROC': 'maternity', 'ADD CAMHS': 'weekday',
                   'ADD OPLAKDA': 'weekday', 'CUH TKKHC': 'weekday', 'ADD MGEND': 'weekday', 'ADD GPRC': 'weekday', 'ALGYDC WARD': 'weekday',
                   'ADD ALLERGY DAY UNIT': 'weekday', 'ADD CR': 'weekday', 'ADD NEUREG': 'weekday', 'ADD TXW':'weekday', 'CUH HOME BIRTH': 'maternity',
                   'ADD FCH': 'weekday', 'ADD PHG': 'weekday', 'ADD CRJAPSUR': 'weekday', 'ADD CORNREV': 'weekday', 'ADD MKO': 'weekday', 'ADD CNPHY43': 'weekday',
                   'ADD LEAPCON': 'weekday', 'ADD CAU': 'weekday', 'ADD AHNR':'weekday',  'ADD UROLP': 'weekday', 'ADDFIBROSCAN': 'weekday',
                   'ADD VASCSURV':'weekday',  'ADD MBR': 'weekday', 'ADD DE': 'weekday', 'ROS NURSEPMB': 'weekday', 'ADD PMIC':'weekday', 'ADD JMW': 'weekday',
                   'ADD RJW': 'weekday', 'ADD ALCC': 'weekday', 'ADD UVP': 'weekday', 'ADD AJCGEN': 'weekday', 'ADD CCH': 'weekday', 'ADD DMOSVRC': 'weekday',
                   'ADD PUVATL':'weekday', 'ADD JOAMD' : 'weekday','ADD AGO': 'weekday', 'C8 WARD': 'C8', 'ADD GPRCB':'weekday',  'ADD PFWO': 'weekday',
                   'ADD JB':'weekday',  'ADD SMK': 'weekday', 'ADD CJB': 'weekday',  'CUH PFWON': 'weekday' ,'ADD LMSH': 'weekday', 'ADD JLU': 'weekday',
                   'ADD CONSFOOT': 'weekday', 'ADD HEPNEW': 'weekday', 'ADD KESPB': 'weekday', 'ADD OTHOTNEU': 'weekday', 'ADD SKIN': 'weekday',
                   'ADD GMTS': 'weekday', 'ADD SMCEF': 'weekday', 'ROS PPMD': 'weekday', 'ADD NFLL': 'weekday', 'ADD LTX': 'weekday', 'CUH GPRCN': 'weekday',
                   'ADD SNSK': 'weekday', 'ADD KV': 'weekday', 'ADD NS': 'weekday', 'CUH NGSHAV': 'weekday', 'ADD SKAMP': 'weekday', 'CCRC Endo':'weekday',
                   'ADD RDPFP': 'weekday','ADD IMA':'weekday', 'ADDALCGNLYR3':'weekday', 'ADD JTKMEF':'weekday', 'ADD LUCENTOP': 'weekday', 'ADD PSC': 'weekday', 'ADD SORD': 'weekday'}


minimal_cat_ward_dict = {'ADD A3 WARD': 'neurosurgery ward', 'ADD A4 WARD': 'neurosurgery ward',
                   'ADD A5 WARD': 'neurosurgery ward', 'ADD D6 WARD': 'neurosurgery ward',
                   'ADD CLINICAL DECN UNIT': 'CDU ward', 'ADD CT': 'CT scan',
                   'ADD ECHO1': 'echo', 'ADD EMERGENCY DEPT': 'AE',
                   'ADD GENRAD': 'radiology', 'ADD IRAD': 'interv radiol',
                   'ADD J2 WARD': 'general surgical ward', 'ADD J2-C3 WARD': 'PICU',
                   'ADD MAIN THEATRE': 'theatre', 'ADD MAIN THEATRE 04':'theatre',
                   'ADD MAIN THEATRE 22': 'neuro theatre', 'ADD MRI': 'MRI',
                   'ADD NEURO ICU': 'NCCU', 'ADD NEURO THEATRE': 'neuro theatre',
                   'ADD NEURO THEATRE 1': 'neuro theatre', 'ADD US': 'US',
                   'ADD CUH EXT FILM': 'external radiology', 'ADD POST-DISCHARGE': 'discharge',
                   'discharge': 'discharge', 'ADD C5 WARD': 'general medical ward',
                   'ADD D10': 'general medical ward', 'ADD D8 WARD': 'orthopaedic ward',
                   'ADD D9 WARD': 'general medical ward', 'ADD DISCHARGE LOUNGE': 'discharge',
                   'ADD FLUORO': 'fluoroscopy', 'ADD GENERAL ICU': 'ICU',
                   'ADD LSFOOT': 'weekday', 'ADD MAIN THEATRE 20': 'theatre',
                   'ADD NEURO THEATRE 2': 'neuro theatre', 'ADD NEURO THEATRE 3': 'neuro theatre',
                   'ADD NEUROPHY': 'weekday', 'ADD PET': 'PET',
                   'ADD REHAB UNIT': 'rehab', 'ADD RT TRT': 'weekday',
                   'Endo Ward': 'weekday', 'ADD D4 IDA UNIT': 'HDU','ADD L2 WARD' : 'general surgical ward',
                   'ADD MAIN THEATRE 16': 'theatre', 'ADD R2 WARD': 'rehab',
                   'ADD K3 WARD': 'cardiology ward', 'ADD G4 WARD': 'general medical ward',
                   'ADD L4 WARD': 'ATC surgical ward', 'ADD L5 WARD': 'ATC surgical ward',
                   'ADD C4 WARD': 'acute medical ward', 'ADD ATC THEATRE': 'theatre',
                   'ADD ATC THEATRE 31': 'theatre', 'ADD ATC THEATRE 32': 'theatre',
                   'ADD ATC THEATRE 36': 'theatre', 'ADD ATC THEATRE 33': 'theatre',
                   'ADD ATC THEATRE 34': 'theatre', 'ADD M4 WARD': 'ATC surgical ward',
                   'ROS DAPHNE WARD': 'gynae surgical ward', 'ADD PRE-ADMISSION':'admission',
                   'ADD ATC THEATRE 35': 'theatre', 'ADD C10 WARD': 'general medical ward','ADD C3 WARD': 'paediatric ward',
                   'ADD D10 WARD': 'general medical ward', 'ADD CATH ROOM': 'angiography',
                   'ADD CORONARY CARE UNIT': 'HDU', 'ADD DIALYSIS UNIT': 'weekday',
                   'ADD K2 WARD': 'acute medical ward', 'ADD MAIN THEATRE 17': 'theatre',
                   'ADD D5 WARD': 'general medical ward', 'ADD D6H WARD': 'general medical ward','ADD C9 WARD': 'general medical ward',
                   'ADD D7 WARD': 'general medical ward', 'ADD C7 WARD': 'general surgical ward','ADD C6 WARD': 'general medical ward',
                   'ADD C8 WARD': 'orthopaedic ward',  'ADD EAU4 WARD': 'acute medical ward', 'ADD C2 WARD': 'paediatric ward','ADD D2 WARD': 'paediatric ward',
                   'ADD F6 WARD': 'general medical ward', 'ADD G6 WARD': 'general medical ward',
                   'ADD F5 WARD': 'acute medical ward', 'ADD G5 WARD': 'general medical ward',
                   'ADD F4 WARD': 'general medical ward', 'ADD G3 WARD': 'general medical ward',
                   'ADD F3 WARD': 'paediatric ward', 'ADD K2 TOE/CARDIOVERSION': 'TOE',
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
                   'ADD OIR RECOVERY': 'weekday', 'ADD SURG DISCH LOUNGE': 'discharge',
                   'ADD ADREHAB': 'rehab', 'ADD DENTALX': 'radiology',
                   'ADD EMMF': 'weekday', 'ADD GII': 'general medical ward',
                   'ADD ORTHOP': 'weekday', 'ADD OTHOTMON': 'weekday',
                   'CUH EXT FILM': 'external radiology', 'ADD PFWON': 'weekday',
                   'ROS MRI SCAN': 'MRI', 'VAU WARD': 'vascular access ward',
                   'ADD EAU5 WARD': 'acute medical ward', 'ADD PPMFU': 'weekday','ADD EAU3 WARD': 'acute medical ward',
                   'ADD CL8': 'weekday', 'ADD OBS US': 'US',
                   'ADD CNPHY': 'neurophysiology', 'ADD AAA': 'weekday',
                   'ADD FANREHA': 'rehab','ADD G2 WARD': 'general medical ward',
                   'ADD OTHOTATY': 'weekday', 'ADD STOMA': 'weekday',
                   'CUHTAANKGLAU': 'weekday', 'ADD EMEYE': 'weekday',
                   'ADD EMMO': 'weekday', 'ADD EYE UNIT DAYCASES': 'weekday',
                   'ADD EYE UNIT THEATRE': 'theatre', 'CUH ELY DAY SURG UNIT': 'weekday',
                   'ADD E10 WARD': 'general medical ward', 'ROS CYSTOMCS': 'weekday',
                   'ROS GONC': 'weekday', 'ADD ENTX': 'weekday',
                   'ADD DIAGVEST':'weekday','ADD JRM':'weekday','ADD HFT':'weekday','ADD LFT':'weekday',
                   'ADD NM':'weekday', 'ADD PDHU':'weekday', 'ADD RBJNEPH': 'weekday',
                   'ADD AIADAR': 'weekday', 'ADD TXM': 'weekday','ADD LVR':'weekday', 'ADD WTUOC':'weekday',
                   'ADD JODR': 'weekday','ADD AHNREF':'weekday','ADD NJAUOC':'weekday','ADD JMDW':'weekday',
                   'ADD ACF': 'weekday', 'ADD DKNAMD':'weekday', 'ADD EABC':'weekday', 'ADD MRDB':'weekday',
                   'ADD UDA':'weekday', 'ADD POADSU': 'weekday', 'ADD POAOSDSU':'weekday',
                   'ADD AJCUOCW':'weekday','ADD SJM':'weekday','ADD SMBRECON': 'weekday', 'ADD SRGAMB': 'weekday',
                   'ADD LVRF':'weekday','ADD KDABI':'weekday', 'ADD NSGYFC':'weekday', 'ADD PSUD':'weekday',
                   'ADD BU':'radiology', 'POST-DISCHARGE':'discharge', 'PRE-ADMISSION':'admission',
                   'ADD J3-C3 WARD': 'surgical day ward', 'ADD PAED ICU': 'PICU', 'ADD R3': 'general medical ward', 'ADD PLASTIC SURG UNIT': 'general surgical ward',
                   'ADD KDA': 'weekday', 'ADDFLEXCYSOP': 'weekday', 'ROS SARA WARD': 'gynae surgical ward', 'ROS MFM': 'maternity', 'ROS DELIVERY UNIT': 'maternity',
                   'ROS ROSIE THEATRE 2': 'theatre', 'ADD GDC': 'weekday', 'ADD ONCOLOGY DAY UNIT': 'weekday', 'ADD AECLINIC': 'weekday',
                   'ROS OBS US': 'US', 'ADD OTHOTESP': 'weekday', 'ADD SNSKF': 'weekday', 'ADDOPTHIMG14':'weekday', 'ADD EMENT': 'weekday',
                   'ADD DSK': 'weekday', 'ADD PMT': 'weekday', 'ROS ROSIE THEATRE 1': 'theatre', 'ROS LADY MARY WARD': 'maternity', 'ADD PACV': 'weekday',
                   'ADD DKNVR': 'weekday',  'ADD EYE UNIT THEATRE 41': 'weekday', 'ADD SURGAMB': 'weekday', 'ADD OTHOTRMC':'weekday',
                   'ADD J3 PICU WARD': 'PICU', 'ADD NEUROONC': 'weekday', 'CUH ELY THEATRE 3': 'weekday', 'ROS UROG': 'weekday',
                   'ADD FCHEM': 'weekday', 'ADD RMAC': 'weekday', 'ADD C9 DAY UNIT': 'general medical ward', 'ADD MKTMF': 'weekday','ADD EYE UNIT THEATRE 42': 'theatre', 'ADD ORALCF': 'weekday', 'ADD ALA':'weekday' , 'ADD ADCA': 'weekday', 'ADD DCHIR': 'weekday',
                   'L4 WARD': 'general surgical ward', 'ADD LITHO': 'weekday','ADD MLBV': 'weekday', 'ADDKKSTPHCL1': 'weekday', 'ADD ARNO': 'weekday', 'ADD ENT': 'weekday',
                   'ADD ORALNK': 'weekday', 'ADDSALHSTONE': 'weekday', 'ADD DVT': 'weekday', 'ADD LEAP': 'weekday', 'ADD ANGED': 'weekday', 'ADD MP': 'weekday',
                   'ADD ARNOF': 'weekday', 'F3 WARD': 'paediatric ward', 'ADD KKSTF':'weekday',  'ADD SO': 'weekday', 'ADD CROPP': 'rehab', 'ADD PJM3': 'weekday',
                   'ADD TPBAC': 'weekday', 'ADD HHSC': 'weekday', 'ADD PAED DAY UNIT': 'weekday', 'ADD JOMR': 'weekday', 'ADD SM': 'weekday',
                   'ADDOPTHIMGVF': 'weekday', 'ADD AMBIPN3': 'weekday', 'ADD PAEDAUD': 'weekday' ,'ADD NASHC': 'weekday', 'ADD BPHYT': 'weekday',
                   'ADD CARDPP': 'weekday', 'ADD PDHUF': 'weekday', 'NICU WARD': 'PICU', 'M5 WARD': 'ATC surgical ward', 'ADD CJGG': 'weekday',  'ADD TXT': 'weekday',
                   'ADD PDCCAP': 'weekday', 'ADD EIUNET': 'weekday', 'ADD POAF2F': 'weekday ', 'ADD ALC43': 'weekday', 'ADD NSGYPAED': 'weekday',
                   'ADD EMEWA': 'weekday', 'ADD LVA': 'weekday', 'ADD RMIL': 'weekday',  'ADD CAUFUTEL': 'weekday', 'ADD HMF': 'maternity', 'ADD JTKM': 'weekday',
                   'PDU WARD': 'weekday', 'ADD BMUTN': 'weekday', 'ADD EMSAC': 'weekday', 'ADD PPMBS': 'weekday', 'ADD ACPRUOC':'weekday', 'ADD OPLAOP': 'weekday',
                   'ADD GICH': 'weekday', 'ADD PENT': 'weekday', 'ADD RATRG': 'weekday',  'ADD COLSB': 'weekday', 'ADD CRG': 'weekday', 'ADD LCWVASC': 'weekday',
                   'ROS MADU': 'maternity', 'ADD HAEMOP': 'weekday', 'ADD PRIMARY': 'weekday', 'ADD TNM':'weekday' , 'ADD DXACCESS': 'weekday', 'G2 WARD' : 'general medical ward',
                   'ADD PPMBSK2': 'weekday', 'ADD MAIN RECOVERY': 'recovery', 'ADD PDH': 'weekday', 'ADD AIAD': 'weekday' ,
                   'ADD ENDOSCOPY UNIT': 'endoscopy', 'ADD IMPREHAB': 'rehab', 'ADD CDMSLD': 'weekday', 'ADD PJPU': 'weekday', 'ADD YML': 'physio',
                   'ADD PJNK': 'weekday', 'ADD NEUROTR': 'weekday', 'ADD MSR': 'weekday', 'ADD KRM': 'weekday', 'ADD PJ': 'weekday', 'ADD PHYL': 'physio',
                   'ADD ORALVSAN':'weekday',  'ADD MOSOP': 'weekday', 'ADD AJCUOC': 'weekday', 'ADD TKKHL': 'weekday', 'ADD EMSMHC':'weekday',
                   'ADD NEJENT': 'weekday', 'ADD JPF': 'weekday', 'ADD EIACA': 'weekday', 'ADD UROLA': 'weekday', 'E10 WARD': 'general medical ward', 'ADD GMTSEF': 'weekday',
                   'ADD APCCOMB': 'weekday', 'ADD MLEDAR': 'weekday', 'ADD NPDV': 'weekday', 'ADDOTHOTORTH': 'weekday', 'ADD AJM': 'weekday',
                   'ADD PDHUEF': 'weekday', 'ADD SNSKEF': 'weekday', 'ADD D5 DAY CASE UNIT': 'general surgical ward', 'ADD MPFC': 'weekday','ADD MPS': 'weekday',
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
                   'ADD SNSK': 'weekday', 'ADD KV': 'weekday', 'ADD NS': 'weekday', 'CUH NGSHAV': 'weekday', 'ADD SKAMP': 'weekday', 'CCRC Endo':'weekday',
                   'ADD RDPFP': 'weekday','ADD IMA':'weekday', 'ADDALCGNLYR3':'weekday', 'ADD JTKMEF':'weekday', 'ADD LUCENTOP': 'weekday', 'ADD PSC': 'weekday', 'ADD SORD': 'weekday'}


#read in the data from a combined csv file
alldata = pd.read_csv("transfers_old_tando.csv")
#alldata= pd.read_csv("transfers_old_t_o.csv")
location_category_map = minimal_cat_ward_dict
#location_category_map = nocat_ward_weekday

alldata['from_category'] = alldata['from'].map(location_category_map)
alldata['to_category'] = alldata['to'].map(location_category_map)

missing_locations = alldata[alldata['from_category'].isnull()]['from'].unique()
print(missing_locations)
#drop the old from and to columns and then rename the new ones into from and to
alldata = alldata.drop(['from','to'], axis=1)
alldata.rename(index=str, columns={'from_category': 'from'}, inplace = True)
alldata.rename(index=str, columns={'to_category': 'to'}, inplace = True)



# now develop the network based on the transfer data
print('now doing the network calculations')
#find all the admission dates on a weekend
alldata['dt_adm'] = pd.to_datetime(alldata['dt_adm'], format="%Y-%m-%d %H:%M")
alldata['is_weekend'] = alldata['dt_adm'].map(is_weekend)
weekend_admissions = alldata[alldata['is_weekend']]
weekday_admissions = alldata[~alldata['is_weekend']]
#list_of_weekend_admissions =[get_weekend_list(data) for data in data['admission_time']]


#now make the graph
specific_data = alldata
#specific_data = weekend_admissions
#specific_data = weekday_admissions
#specific_data = pd.read_csv("combined_data.csv")
#specific_data.loc[admpoint[specific_data['admission_time'] == specific_data['extraid']].index, 'to'] = 'discharge'

#weighted edges first
#drop the columns that are not needed for the graph, also only adults
data_only_transfers = specific_data.drop(['transfer_dt', 'dt_adm', 'dt_dis', 'spec', 'age', 'asa'], axis=1)
#data_only_transfers = specific_data.loc[specific_data['age'] > 16].drop(['transfer_dt', 'dt_adm', 'dt_dis', 'spec', 'age', 'asa'], axis=1)

# count the number of times a specific transfer appears to get edge weight
transfer_counts = data_only_transfers.groupby(['from', 'to']).count()
#add the old index as a column - int he above the count became the index.
transfer_counts = transfer_counts.reset_index()
transfer_counts = transfer_counts[transfer_counts['ptid'] > 1]
# Get a list of tuples that contain the values from the rows.
edge_weight_data = transfer_counts[['from', 'to', 'ptid']]
unweighted_edge_data = transfer_counts[['from', 'to']]
sum_of_all_transfers = edge_weight_data['ptid'].sum()
edge_weight_data['ptid'] = edge_weight_data['ptid']#/sum_of_all_transfers


weighted_edges = list(itertools.starmap(lambda f, t, w: (f, t, int(w)), edge_weight_data.itertuples(index=False, name=None)))
unweighted_edges = list(itertools.starmap(lambda f, t: (f,t), unweighted_edge_data.itertuples(index=False, name = None)))

G = nx.DiGraph()
#print(weighted_edges)
G.add_weighted_edges_from(weighted_edges)

unweightednondirG = nx.Graph()
unweightednondirG.add_edges_from(unweighted_edges)

en=G.number_of_edges()
nn=G.number_of_nodes()
print(en)
print(nn)





#undirected graph of the same data
nondiG = nx.Graph()
nondiG.add_weighted_edges_from(weighted_edges)


#calculate the degree
degrees = nx.classes.function.degree(G)
in_degrees = G.in_degree
out_degrees = G.out_degree

#print(in_degrees)

weighted_degrees = nx.degree(G,weight = 'weight')
#weighted_in_degrees = nx.DiGraph.in_degree(G,weight = 'weights')
weighted_in_degrees = G.in_degree(weight = 'weight')
#print(weighted_in_degrees)
weighted_out_degrees = G.out_degree(weight = 'weight')
#print('degrees')
#print(degrees)
histdegrees = nx.classes.function.degree_histogram(G)
#print('histdegrees')
#print(histdegrees)
# calculate the degree
degrees_list = [[n, d] for n, d in degrees]
degrees_data = pd.DataFrame(degrees_list, columns=['node', 'degree'])

indegreeslist = [[n, d] for n, d in in_degrees]
indegrees_data = pd.DataFrame(indegreeslist, columns=['node', 'degree'])

outdegreeslist = [[n, d] for n, d in out_degrees]
outdegrees_data = pd.DataFrame(outdegreeslist, columns=['node', 'degree'])

weighted_degrees_list = [[n, d] for n, d in weighted_degrees]
weighted_degrees_data = pd.DataFrame(weighted_degrees_list, columns=['node', 'degree'])

weighted_indegrees_list = [[n, d] for n, d in weighted_in_degrees]
weighted_indegrees_data = pd.DataFrame(weighted_indegrees_list, columns=['node', 'degree'])

weighted_outdegrees_list = [[n, d] for n, d in weighted_out_degrees]
weighted_outdegrees_data = pd.DataFrame(weighted_outdegrees_list, columns=['node', 'degree'])



print(nx.get_edge_attributes(G, 'weight'))

#degrees_data_degree = degrees_data['degree']


# calculate the centrality of each node - fraction of nodes the incoming/outgoing edges are connected to
incentrality = nx.algorithms.centrality.in_degree_centrality(G)
outcentrality = nx.algorithms.centrality.out_degree_centrality(G)


df_with_node_index = degrees_data.set_index('node')
emergency_degrees = df_with_node_index.loc['AE','degree']
#print(emergency_degrees)
    #degrees_list.append(list(degrees.values))
    #degrees_list.to_csv('degrees%s.csv' % str(i), header=True, index=False)

#number of transfers from medical wards to theatre
acute_to_theatre = G.get_edge_data('acute medical ward', 'theatre', default={}).get('weight', 1)
gen_to_theatre = G.get_edge_data('general medical ward', 'theatre', default={}).get('weight', 1)
card_to_theatre = G.get_edge_data('cardiology ward', 'theatre', default={}).get('weight', 1)
rehab_to_theatre = G.get_edge_data('rehab', 'theatre', default={}).get('weight', 1)
total_medical_to_theatre = acute_to_theatre + gen_to_theatre + card_to_theatre + rehab_to_theatre

#number of circular or unnecessary ward transfers
med_to_med_acute = G.get_edge_data('acute medical ward', 'acute medical ward', default = {}).get('weight', 1)
med_to_med_acgen = G.get_edge_data('acute medical ward', 'general medical ward', default={}).get('weight', 1)
med_to_med_genac = G.get_edge_data('general medical ward', 'acute medical ward', default={}).get('weight', 1)
med_to_med_general = G.get_edge_data('general medical ward', 'general medical ward', default={}).get('weight', 1)


med_to_surg = G.get_edge_data('general medical ward', 'general surgical ward', default ={}).get('weight', 1)
med_to_ortho = G.get_edge_data('general medical ward', ' orthopaedic ward', default ={}).get('weight', 1)
med_to_surg_acute = G.get_edge_data('acute medical ward', 'general surgical ward', default={}).get('weight', 1)
med_to_orth_acute = G.get_edge_data('acute medical ward', ' orthopaedic ward', default={}).get('weight', 1)
acmed_to_ns = G.get_edge_data('acute medical ward', 'neurossurgical ward', default={}).get('weight', 1)
genmed_to_ns = G.get_edge_data('general medical ward', 'neurosurgical ward', default={}).get('weight', 1)
acmed_to_atc = G.get_edge_data('acute medical ward', 'ATC surgical ward', default={}).get('weight', 1)
genmed_to_atc = G.get_edge_data('general medical ward', 'ATC surgical ward', default={}).get('weight', 1)
total_medical_ward_transfers = med_to_med_acute + med_to_med_general+med_to_med_acgen+med_to_med_genac+ med_to_ortho+ med_to_surg+ med_to_surg_acute+ med_to_orth_acute+acmed_to_ns+genmed_to_ns+acmed_to_atc+genmed_to_atc
#print (total_medical_ward_transfers)

ae_surg = G.get_edge_data('AE', 'general surgical ward', default={}).get('weight', 0)+ G.get_edge_data('AE', 'orthopaedic ward', default={}).get('weight', 0) +G.get_edge_data('AE', 'ATC surgical ward', default={}).get('weight', 0) + G.get_edge_data('AE', 'gynae ward', default={}).get('weight', 0)+  G.get_edge_data('AE', 'neurosurgical ward', default={}).get('weight', 0)
#print(ae_surg)
ae_med = G.get_edge_data('AE', 'acute medical ward', default={}).get('weight', 0) + G.get_edge_data('AE', 'general medical ward', default={}).get('weight', 0) + G.get_edge_data('AE', 'cardiology ward', default={}).get('weight', 0) + G.get_edge_data('AE', 'rehab', default={}).get('weight', 0) +  G.get_edge_data('AE', 'cdu', default={}).get('weight', 0)
if ae_surg == 0:
    ratio_wards_surg_med = 0
else:
    ratio_wards_surg_med = ae_med/ae_surg


# calculate the centrality of each node - fraction of nodes the incoming/outgoing edges are connected to
incentrality = nx.algorithms.centrality.in_degree_centrality(G)
in_centr_df = pd.DataFrame.from_dict(incentrality, orient = 'index')
# check if the theatre node exists in this data subset
if 'theatre' in incentrality:
    in_theatre_centrality = incentrality['theatre']
else:
    in_theatre_centrality = 0

outcentrality = nx.algorithms.centrality.out_degree_centrality(G)
out_centr_df = pd.DataFrame.from_dict(outcentrality, orient = 'index')
if 'theatre' in outcentrality:
    out_theatre_centrality = outcentrality['theatre']
else:
    out_theatre_centrality = 0

if 'AE' in outcentrality:
    out_ed_centrality = outcentrality['AE']
else:
    out_ed_centrality = 0


bet_centr = nx.algorithms.centrality.betweenness_centrality(G)
bet_centr_df = pd.DataFrame.from_dict(bet_centr, orient = 'index')
#print(bet_centr)
#print(bet_centr_df)

if 'theatre' in bet_centr:
    theatres_bet_centrality = bet_centr['theatre']
else:
    theatres_bet_centrality = 0

#specialised centralities and the assortativity and nearest neightbor fucntions

if en == 0:
    theatres_eigen_centr = 0
    ed_eigen_centr = 0
    assortativity_net_inout = 0
    k_nearest_n = 0
else:
    eigen_centr = nx.eigenvector_centrality_numpy(G)
    eigen_centr_df = pd.DataFrame.from_dict(eigen_centr, orient = 'index')
    #print(eigen_centr_df)


    assortativity_net_inout = nx.degree_assortativity_coefficient(G, x='out', y='in', weight='weights')
    print('assortativity=')
    print(assortativity_net_inout)
    k_nearest_n = nx.k_nearest_neighbors(G,source='out',target='in', weight='weights')
    print('knn')
    print(k_nearest_n)
    print('knn data frame')

    #knn_list = [[n, k] for n, k in k_nearest_n]
    #knn_data = pd.DataFrame(knn_list, columns=['node', 'knn'])
    knn_df = pd.DataFrame.from_dict(k_nearest_n, orient='index')
    #knn_df = pd.DataFrame(k_nearest_n, index=['ward', 'knn'])
    print(knn_df)
    if 'theatre' in eigen_centr:
        theatres_eigen_centr = eigen_centr['theatre']
    else:
        theatres_eigen_centr = 0

    if 'AE' in eigen_centr:
        ed_eigen_centr = eigen_centr['AE']
    else:
        ed_eigen_centr = 0


# flow hiearchy - finds strongly connected components
if nn == 0:
    flow_hierarchy = 0
    print('flowhierarchy is zero as nn zero')
else:
    flow_hierarchy = nx.flow_hierarchy(G, weight = 'weights')
print('flow hierarchy')
print(flow_hierarchy)


#other network measures that apply to the whole network
density_net = nx.density(G)
transitivity_net = nx.transitivity(G)
#clustering - doesnt work for directed graphs
clustering_average = nx.average_clustering(nondiG,weight = 'weights')
weighted_clustering_distribution = nx.clustering(nondiG, weight = 'weight')
non_weighted_clustering_distribution = nx.clustering(unweightednondirG)
#print(clustering_distribution)
weighted_clustering_list = [[n, d] for n, d in weighted_clustering_distribution.items()]
weighted_clustering_data = pd.DataFrame(weighted_clustering_list, columns=['node', 'clustering_coeff'])

non_weighted_clustering_list = [[n, d] for n, d in non_weighted_clustering_distribution.items()]
non_weighted_clustering_data = pd.DataFrame(non_weighted_clustering_list, columns=['node', 'clustering_coeff'])

print('clustering in non directed graph')
print(clustering_average)

#shortest path in the directed graph, from a starting point source to a point target
average_shortest_path = nx.average_shortest_path_length(G,weight = 'weights')
#average_shortest_path = 0
print(average_shortest_path)


#flow hiearchy - finds strongly connected components
#flow_hierarchy = nx.algorithms.hierarchy.flow_hierarchy(G)
#print('flow hierarchy')
#print(flow_hierarchy)

data_list = []
data_list.append({'sum of transfers': sum_of_all_transfers,'number nodes': nn,'number edges': en,'flow hierarchy': flow_hierarchy,
                      'emergency degrees': emergency_degrees,'outcentrality ed': out_ed_centrality,'eigen_centr_ed': ed_eigen_centr, 'incentrality theatres': in_theatre_centrality,
                      'outcentrality theatres': out_theatre_centrality, 'bet centrality theatres': theatres_bet_centrality,'eigen_centr_theatre': theatres_eigen_centr,
                  'medical to theatre': total_medical_to_theatre,
                      'medical ward transfers': total_medical_ward_transfers, 'med surg ratio': ratio_wards_surg_med,
                       'density': density_net, 'transitivity':transitivity_net, 'clustering average': clustering_average, 'average shortest path':average_shortest_path})

all_network_info_df = pd.DataFrame(columns=['sum of transfers','number nodes', 'number edges', 'flow hierarchy', 'emergency degrees', 'outcentrality ed', 'eigen_centr_ed',
                                         'incentrality theatres', 'outcentrality theatres', 'bet centrality theatres','eigen_centr_theatre','medical to theatre','medical ward transfers',
                                         'med surg ratio', 'density', 'transitivity', 'clustering average', 'average shortest path'], data = data_list)

filename = '_mincat_1102_oldto'


all_network_info_df.to_csv('info' + filename + '.csv', header=True, index=False)
edge_weight_data.to_csv('edge' + filename + '.csv', header=True, index=False)
#nx.write_pajek(G, 'pajek_old.net')
degrees_data.to_csv('degrees' + filename + '.csv', header =True, index=False)
indegrees_data.to_csv('indegrees' + filename + '.csv', header =True, index=False)
outdegrees_data.to_csv('outdegrees' + filename + '.csv', header =True, index=False)
weighted_degrees_data.to_csv('weighteddegrees' + filename + '.csv', header =True, index=False)
weighted_indegrees_data.to_csv('weightedindegrees' + filename + '.csv', header =True, index=False)
weighted_outdegrees_data.to_csv('weightedoutdegrees' + filename + '.csv', header =True, index=False)

weighted_clustering_data.to_csv('weightedclustering' + filename + '.csv', header = True, index = False)
non_weighted_clustering_data.to_csv('nonweightedclustering' + filename + '.csv', header = True, index = False)
knn_df.to_csv('knndata'+ filename+'.csv', header = True, index = True)
eigen_centr_df.to_csv('eigencentrdata'+ filename+'.csv', header = True, index = True)
in_centr_df.to_csv('incentrdata'+ filename+'.csv', header = True, index = True)
out_centr_df.to_csv('outcentrdata'+ filename+'.csv', header = True, index = True)
bet_centr_df.to_csv('betweencentrdata'+ filename+'.csv', header = True, index = True)
nx.write_graphml(G,'graphml'+ filename + '.graphml')
nx.write_gexf(G,'gexf' + filename +'.gexf')



print('all network information file created')



#fig = plt.figure(figsize=(7, 5))
#nx.set_node_attributes(G,'length_of_stay',los)
#pos = nx.circular_layout(G)
#widthedge = [d['weight'] *0.1 for _,_,d in G.edges(data=True)]
#nx.draw_networkx(G, pos=pos, with_labels=True, font_weight='bold', arrows = False, width= widthedge,  node_size=1300)
#nx.draw_circular(G)
#width = [d['weight'] for _,_,d in G.edges(data=True)]

#edge_labels=dict([((u,v,), d['weight'])
#             for u,v,d in G.edges(data=True)])
#nx.draw_networkx(G, with_labels=True, font_weight='bold' )
#nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels)
#plt.show()
#fig.savefig("adultrennetworkgraph.png")
#plt.gcf().clear()
