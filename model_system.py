import pandas as pd
import datetime
import numpy as np
from collections import deque, namedtuple

alltransfers = pd.read_csv("all_transfers_file.csv")

alltransfers.rename(index=str, columns={'from': 'from_loc'}, inplace=True)
alltransfers.rename(index=str, columns={'to': 'to_loc'}, inplace=True)
list_from_wards = alltransfers.from_loc.unique()
list_to_wards = alltransfers.to_loc.unique()
#need to make an assignment of the individual wards to a category eg surgical ward, outlier, high dependency...


ward_dictionary = {'ADD A3 WARD': 'ns ward', 'ADD A4 WARD': 'ns ward',
                   'ADD A5 WARD': 'ns ward', 'ADD D6 WARD': 'ns ward',
                   'ADD CLINICAL DECN UNIT': 'assess ward', 'ADD CT': 'CT scan',
                   'ADD ECHO1': 'echo', 'ADD EMERGENCY DEPT': 'AE',
                   'ADD GENRAD': 'radiology', 'ADD IRAD': 'interv rad',
                   'ADD J2 WARD': 'day ward', 'ADD J2-C3 WARD': 'day ward',
                   'ADD MAIN THEATRE': 'theatre', 'ADD MAIN THEATRE 04':'theatre',
                   'ADD MAIN THEATRE 22': 'theatre', 'ADD MRI': 'mri',
                   'ADD NEURO ICU': 'nncu', 'ADD NEURO THEATRE': 'neuro theatre',
                   'ADD NEURO THEATRE 1': 'neuro theatre', 'ADD US': 'us',
                   'ADD CUH EXT FILM': 'external rad', 'ADD POST-DISCHARGE': 'post-discharge',
                   'discharge': 'discharge', 'ADD C5 WARD': 'acute medical ward',
                   'ADD D10': 'general medical ward', 'ADD D8 WARD': 'orthopaedic ward',
                   'ADD D9 WARD': 'general medical ward', 'ADD DISCHARGE LOUNGE': 'disch lounge',
                   'ADD FLUORO': 'fluoroscopy', 'ADD GENERAL ICU': 'icu',
                   'ADD LSFOOT': 'other', 'ADD MAIN THEATRE 20': 'theatre',
                   'ADD NEURO THEATRE 2': 'neuro theatre', 'ADD NEURO THEATRE 3': 'neuro theatre',
                   'ADD NEUROPHY': 'neurophys', 'ADD PET': 'PET scan',
                   'ADD REHAB UNIT': 'rehab', 'ADD RT TRT': 'RT treatment',
                   'Endo Ward': 'endoscopy', 'ADD D4 IDA UNIT': 'HDU',
                   'ADD MAIN THEATRE 16': 'theatre', 'ADD R2 WARD': 'general medical',
                   'ADD K3 WARD': 'cardiology ward', 'ADD G4 WARD': 'general medical ward',
                   'ADD L4 WARD': 'general surgical ward', 'ADD L5 WARD': 'general surgical ward',
                   'ADD C4 WARD': 'acute medical ward', 'ADD ATC THEATRE': 'theatre',
                   'ADD ATC THEATRE 31': 'theatre', 'ADD ATC THEATRE 32': 'theatre',
                   'ADD ATC THEATRE 36': 'theatre', 'ADD ATC THEATRE 33': 'theatre',
                   'ADD ATC THEATRE 34': 'theatre', 'ADD M4 WARD': 'general surgical ward',
                   'ROS DAPHNE WARD': 'gynae surgical ward', 'ADD PRE-ADMISSION':'pread',
                   'ADD ATC THEATRE 35': 'theatre', 'ADD C10 WARD': 'general medical ward',
                   'ADD D10 WARD': 'general medical ward', 'ADD CATH ROOM': 'angiography',
                   'ADD CORONARY CARE UNIT': 'coronary hdu', 'ADD DIALYSIS UNIT': 'dialysis',
                   'ADD K2 WARD': 'cardiology ward', 'ADD MAIN THEATRE 17': 'theatre',
                   'ADD D5 WARD': 'acute medical ward', 'ADD D6H WARD': 'general medical ward',
                   'ADD D7 WARD': 'general surgical ward', 'ADD C7 WARD': 'general surgical ward',
                   'ADD C8 WARD': 'orthopaedic ward',  'ADD EAU4 WARD': 'acute medical ward',
                   'ADD F6 WARD': 'general medical ward', 'ADD G6 WARD': 'general medical ward',
                   'ADD F5 WARD': 'transplant hdu', 'ADD G5 WARD': 'general medical ward',
                   'ADD F4 WARD': 'general medical ward', 'ADD G3 WARD': 'general medical ward',
                   'ADD F3 WARD': 'paediatric ward', 'ADD K2 TOE/CARDIOVERSION': 'toe',
                   'ADD M5 WARD': 'general surgical ward', 'ADD MAIN THEATRE 08': 'theatre',
                   'ADD MED S-STAY UNIT': 'acute medical ward', 'ADD N2 WARD': 'general medical ward',
                   'ADD N3 WARD': 'acute medical ward', 'ADD RT REV': 'outpatient',
                   'ADD TRANSPLANT HDU': 'transplant hdu', 'ADD ADDOPTHIMG14': 'outpatient',
                   'ADD BMF': 'other', 'ADD DAY SURGERY UNIT': 'day surgery unit',
                   'ADD MAIN THEATRE 03': 'theatre', 'ADD MAIN THEATRE 05': 'theatre',
                   'ADD MAIN THEATRE 01': 'theatre', 'ADD MAIN THEATRE 02': 'theatre',
                   'ADD MAIN THEATRE 09': 'theatre', 'ADD MAIN THEATRE 10': 'theatre',
                   'ADD MAIN THEATRE 11': 'theatre', 'ADD MAIN THEATRE 12': 'theatre',
                   'ADD MAIN THEATRE 14': 'theatre', 'ADD MAIN THEATRE 15': 'theatre',
                   'ADD MAIN THEATRE 18': 'theatre', 'ADD MAIN THEATRE 19': 'theatre',
                   'ADD MAIN THEATRE 23': 'theatre', 'ADD MAIN THEATRE 21': 'theatre',
                   'ADD MAIN THEATRE 06': 'theatre', 'ADD MAIN THEATRE 07': 'theatre',
                   'ADD OIR RECOVERY': 'oir', 'ADD SURG DISCH LOUNGE': 'disch lounge',
                   'ADD ADREHAB': 'rehab', 'ADD DENTALX': 'dental',
                   'ADD EMMF': 'other', 'ADD GII': 'general medical ward',
                   'ADD ORTHOP': 'outpatient', 'ADD OTHOTMON': 'ot',
                   'CUH EXT FILM': 'radiology', 'ADD PFWON': 'investigation',
                   'ROS MRI SCAN': 'mri', 'VAU WARD': 'surgical assessment ward',
                   'ADD EAU5 WARD': 'acute medical ward', 'ADD PPMFU': 'investigation',
                   'ADD CL8': 'outpatient', 'ADD OBS US': 'us',
                   'ADD CNPHY': 'physiology', 'ADD AAA': 'other',
                   'ADD FANREHA': 'rehab','ADD G2 WARD': 'general medical ward',
                   'ADD OTHOTATY': 'ot', 'ADD STOMA': 'outpatient',
                   'CUHTAANKGLAU': 'research ward', 'ADD EMEYE': 'outpatient',
                   'ADD EMMO': 'other', 'ADD EYE UNIT DAYCASES': 'theatre',
                   'ADD EYE UNIT THEATRE': 'theatre', 'CUH ELY DAY SURG UNIT': 'theatre ely',
                   'ADD E10 WARD': 'medical ward', 'ROS CYSTOMCS': 'investigation',
                   'ROS GONC': 'investigation', 'ADD ENTX': 'investigation',
                   'ADD DIAGVEST':'other','ADD JRM':'other','ADD HFT':'other','ADD LFT':'other',
                   'ADD NM':'other', 'ADD PDHU':'investigation', 'ADD RBJNEPH': 'other',
                   'ADD AIADAR': 'other', 'ADD TXM': 'other','ADD LVR':'other', 'ADD WTUOC':'other',
                   'ADD JODR': 'other','ADD AHNREF':'other','ADD NJAUOC':'other','ADD JMDW':'other',
                   'ADD ACF': 'other', 'ADD DKNAMD':'other', 'ADD EABC':'other', 'ADD MRDB':'other',
                   'ADD UDA':'other', 'ADD POADSU': 'surgical admission ward', 'ADD POAOSDSU':'surgical admission ward',
                   'ADD AJCUOCW':'other','ADD SJM':'other','ADD SMBRECON': 'other', 'ADD SRGAMB': 'other',
                   'ADD LVRF':'other','ADD KDABI':'other', 'ADD NSGYFC':'surgical admission ward', 'ADD PSUD':'other',
                   'ADD BU':'other', 'POST-DISCHARGE':'post-discharge', 'PRE-ADMISSION':'pread'}

location_category_map = ward_dictionary
alltransfers['from_category'] = alltransfers['from_loc'].map(location_category_map)
alltransfers['to_category'] = alltransfers['to_loc'].map(location_category_map)

alltransfers.to_csv('transfers_categories.csv', header=True, index=False)
print('transfer file with categories written')