import pandas as pd
import datetime
import numpy as np
from collections import deque, namedtuple

alltransfers = pd.read_csv("all_transfers_file.csv")

alltransfers.rename(index=str, columns={'from': 'from_loc'}, inplace=True)
list_wards = alltransfers.from_loc.unique()

#need to make an assignment of the individual wards to a category eg surgical ward, outlier, high dependency...


print(list_wards)