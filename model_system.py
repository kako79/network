import pandas as pd
import datetime
import numpy as np
from collections import deque, namedtuple

alltransfers = pd.read_csv("all_transfers_file.csv")

alltransfers.rename(index=str, columns={'from': 'from_loc'}, inplace=True)
alltransfers.rename(index=str, columns={'from': 'from_loc'}, inplace=True)
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
                   'discharge': 'discharge', 'ADD C5 WARD': 'medical ward',
                   'ADD D10': 'medical ward', 'ADD D8 WARD': 'surgical ward',
                   'ADD D9 WARD': 'medical ward', 'ADD DISCHARGE LOUNGE': 'disch lounge',
                   'ADD FLUORO': 'radiology', 'ADD GENERAL ICU': 'icu',
                   'ADD LSFOOT': 'other', 'ADD MAIN THEATRE 20': 'theatre',
                   'ADD NEURO THEATRE 2': 'neuro theatre', 'ADD NEURO THEATRE 3': 'neuro theatre',
                   'ADD NEUROPHY': 'neurophys', 'ADD PET': 'radiology',
                   'ADD REHAB UNIT': 'rehab', 'ADD RT TRT': 'treatment',
                   'Endo Ward': 'endoscopy', 'ADD D4 IDA UNIT': 'HDU',
                   'ADD MAIN THEATRE 16': 'theatre', 'ADD R2 WARD': 'medical ward',
                   'ADD K3 WARD': 'medical ward', 'ADD G4 WARD': 'medical ward',
                   'ADD L4 WARD': 'surgical ward', 'ADD L5 WARD': 'surgical ward',
                   'ADD C4 WARD': 'medical ward', 'ADD ATC THEATRE': 'theatre',
                   'ADD ATC THEATRE 31': 'theatre', 'ADD ATC THEATRE 32': 'theatre',
                   'ADD ATC THEATRE 36': 'theatre', 'ADD ATC THEATRE 33': 'theatre',
                   'ADD ATC THEATRE 34': 'theatre', 'ADD M4 WARD': 'surgical ward',
                   'ROS DAPHNE WARD': 'surgical ward', 'ADD PRE-ADMISSION':'pread',
                   'ADD ATC THEATRE 35': 'theatre', 'ADD C10 WARD': 'medical ward',
                   'ADD D10 WARD': 'medical ward', 'ADD CATH ROOM': 'angiography',
                   'ADD CORONARY CARE UNIT': 'hdu', 'ADD DIALYSIS UNIT': 'dialysis',
                   'ADD K2 WARD': 'medical ward', 'ADD MAIN THEATRE 17': 'theatre',
                   'ADD D5 WARD': 'medical ward', 'ADD D6H WARD': 'medical ward',
                   'ADD D7 WARD': 'surgical ward', 'ADD C7 WARD': 'surgical ward',
                   'ADD C8 WARD': 'surgical ward',  'ADD EAU4 WARD': 'medical ward',
                   'ADD F6 WARD': 'medical ward', 'ADD G6 WARD': 'medical ward',
                   'ADD F5 WARD': 'hdu', 'ADD G5 WARD': 'medical ward',
                   'ADD F4 WARD': 'medical ward', 'ADD G3 WARD': 'medical ward',
                   'ADD F3 WARD': 'paediatric ward', 'ADD K2 TOE/CARDIOVERSION': 'toe',
                   'ADD M5 WARD': 'surgical ward', 'ADD MAIN THEATRE 08': 'theatre',
                   'ADD MED S-STAY UNIT': 'medical ward', 'ADD N2 WARD': 'medical ward',
                   'ADD N3 WARD': 'medical ward', 'ADD RT REV': 'treatment',
                   'ADD TRANSPLANT HDU': 'hdu', 'ADD ADDOPTHIMG14': 'outpatient',
                   'ADD BMF': 'other', 'ADD DAY SURGERY UNIT': 'theatre',
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
                   'ADD EMMF': 'other', 'ADD GII': 'medical ward',
                   'ADD ORTHOP': 'outpatient', 'ADD OTHOTMON': 'ot',
                   'CUH EXT FILM': 'radiology', 'ADD PFWON': 'investigation',
                   'ROS MRI SCAN': 'mri', 'VAU WARD': 'research ward',
                   'ADD EAU5 WARD': 'medical ward', 'ADD PPMFU': 'investigation',
                   'ADD CL8': 'surgical ward', 'ADD OBS US': 'us',
                   'ADD CNPHY': 'physiology', 'ADD AAA': 'other',
                   'ADD FANREHA': 'rehab', }
PPMFU
VAU WARD
ADD HFT
ADD AAA
print(list_wards)

