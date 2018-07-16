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

alldata['effective_time'] = pd.to_datetime(alldata['effective_time'], format = "%Y-%m-%d %H:%M:%S")
alldata['discharge_time'] = pd.to_datetime(alldata['discharge_time'], format = "%Y-%m-%d %H:%M:%S")
alldata['admission_time'] = pd.to_datetime(alldata['admission_time'], format = "%Y-%m-%d %H:%M:%S")
alldata['transfer_time'] = pd.to_datetime(alldata['transfer_time'], format = "%Y-%m-%d %H:%M:%S")

#et = alldata['effective_time'] + datetime.timedelta(days=5)
#dt = alldata['discharge_time'] + datetime.timedelta(days = 5)
#at = alldata['admission_time']+ datetime.timedelta(days = 5)
#tt = alldata['transfer_time']+ datetime.timedelta(days = 5)

alldata['effective_time'] = alldata['effective_time'].map(lambda d: d + datetime.timedelta(days=5))
alldata['discharge_time'] = alldata['discharge_time'].map(lambda d: d + datetime.timedelta(days=5))
alldata['admission_time'] = alldata['admission_time'].map(lambda d: d + datetime.timedelta(days=5))
alldata['transfer_time'] = alldata['transfer_time'].map(lambda d: d + datetime.timedelta(days=5))
alldata = alldata.drop(['specialty'], axis=1)

alldata.to_csv('offset_data.csv', header=True, index=False)

