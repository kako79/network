from matplotlib import pyplot

import pandas as pd
import numpy as np
from collections import deque, namedtuple
import itertools
import functools

import matplotlib
matplotlib.use('agg')
import matplotlib.pyplot as plt
import networkx as nx
#from collections import Counter
#from itertools import chain
#from collections import defaultdict
from datetime import datetime

def parser(x):
    return datetime.strptime('190' + x, '%Y-%m')


arima_data = pd.read_csv('arima_prep.csv')

#try one of the parameters first - eg nn

series_nodes = arima_data['number nodes']
diff = series_nodes.diff()
pyplot.plot(diff)
pyplot.show()