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

list_from_wards.to_csv('list of wards.csv')


#ward_dictionary = {'ADD '}


print(list_wards)

