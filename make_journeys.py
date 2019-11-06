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

groups = transfers.groupby('ptid')
for ptid, group in groups:
    for row_index, row in group.iterrows():


