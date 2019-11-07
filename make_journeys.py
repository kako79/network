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


COLUMN_NAMES = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12', '13', '14', '15', '16', '17', '18', '19',
                '20', '21','22','23','24','25','26','27','28','29','30','31','32','33','34','35','36','37','38','39','40']
maxLen = len(COLUMN_NAMES)
groups = transfers.groupby('ptid')

df_journeys = pd.DataFrame(columns=COLUMN_NAMES)

locations_not_needed = ['XR', 'clinic', 'PET', 'IR', 'CT']

for ptid, group in groups:
    journey = []
    numbers = []
    for row_index, row in group.iterrows():
        row_location = row['from_cat']
        if row_location in locations_not_needed:
            continue
        if row_location in journey:
            # print('here')
            number_loc = journey.count(row_location) + 1
            # print(number_loc)
        else:
            # print('second here')
            number_loc = 1
        numbers.append(number_loc)
        journey.append(row['from_cat'])
        if len(journey) > maxLen:
            print('long journey', len(journey))

    journey = journey + [0] * (maxLen - len(journey))
    numbers = numbers + [0] * (maxLen - len(numbers))
    full = [str(i) + str(j) for i, j in zip(journey, numbers)]
    print(full)



