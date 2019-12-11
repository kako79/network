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

t_into_pivot = transfers[['ptid','from']]


pivotdf = t_into_pivot.pivot_table(index='ptid', columns='from', aggfunc=len)

pivotdf.to_csv('pivotdf', header = True, index = True)

