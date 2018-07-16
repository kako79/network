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

import datetime

alldata= pd.read_csv("combined_data.csv")

#et = alldata['effective_time'] + datetime.timedelta(days=5)
#dt = alldata['discharge_time'] + datetime.timedelta(days = 5)
#at = alldata['admission_time']+ datetime.timedelta(days = 5)
#tt = alldata['transfer_time']+ datetime.timedelta(days = 5)

df['effective_time'] = df['effective_time'].map(lambda d: d + datetime.timedelta(days=5))


alldata.to_csv('offset_data.csv', header=True, index=False)

