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

originaldata = pd.read_csv("offset_data.csv")
grouped_data = originaldata.groupby('ptid')

#counting the number of times each ptid appears to know how many locations we have
grouped_data_loccounts = originaldata.groupby(['ptid']).size().reset_index(name='counts')
max_locations = max(grouped_data_loccounts['counts']) + 1



for ptid, pt_data in grouped_data:
    # now I am in each group of a ptid, now need to go to each row and select the from location


    for location in pt_data:
        for i in range(1, max_locations):
            location_name = 'loc' + str(i)
            new_df['location_name'] =



new_df['ptid'] = ptid
new_df['age'] =




