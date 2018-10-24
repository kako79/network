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
from datetime import datetime

#this programme takes a list of transfers and analyses them by month and whether they were on a weekend or weekday
# it makes an edge file for each month and also creates a data analysis csv file that contains some network charactersistics for each month
# it replaces the individual theatres with a a general theatre category to capture the degree of the theatre node overall.

def is_weekend(date):
    #print(date)
    strdate = str(date)
    fmt = "%Y-%m-%d %H:%M"
    try:
        d = datetime.strptime(strdate, fmt)
    except ValueError as v:
            ulr = len(v.args[0].partition('unconverted data remains: ')[2])
            if ulr:
                d = datetime.strptime(strdate[:-ulr], fmt)
            else:
                raise v
    #d = datetime.strptime(date, '%Y-%m-%d %H:%M:%S')
    #print(d)
    if (d.isoweekday() == 6 or d.isoweekday() == 7):
        return True
    else:
        return False

def is_ED_strained(breach_perc):
    if breach_perc < 0.75:
        return True
    else:
        return False


def get_month(date):
    strdate = str(date)
    fmt = "%Y-%m-%d %H:%M"
    try:
        d = datetime.strptime(strdate, fmt)
    except ValueError as v:
        ulr = len(v.args[0].partition('unconverted data remains: ')[2])
        if ulr:
            d = datetime.strptime(strdate[:-ulr], fmt)
        else:
            raise v
    return d.month

def get_network_analytics(month_data_reduced):
    # weighted edges first
    # count the number of times a specific transfer appears to get edge weight
    transfer_counts = month_data_reduced.groupby(['from', 'to']).count()

    # add the old index as a column - int he above the count became the index.
    transfer_counts = transfer_counts.reset_index()
    transfer_counts = transfer_counts[transfer_counts['ptid'] > 1]
    # Get a list of tuples that contain the values from the rows.
    edge_weight_data = transfer_counts[['from', 'to', 'ptid']]
    sum_of_all_transfers = edge_weight_data['ptid'].sum()
    edge_weight_data['ptid'] = edge_weight_data['ptid'] / sum_of_all_transfers
    if it_is_weekend == False:
        edge_weight_data.to_csv('edge_wdadult%s.csv' % str(i), header=True, index=False)
    else:
        edge_weight_data.to_csv('edge_weadult%s.csv' % str(i), header=True, index=False)

    weighted_edges = list(
        itertools.starmap(lambda f, t, w: (f, t, int(w)), edge_weight_data.itertuples(index=False, name=None)))

    G = nx.DiGraph()
    # print(weighted_edges)
    G.add_weighted_edges_from(weighted_edges)
    en = G.number_of_edges()
    nn = G.number_of_nodes()
    #print(en)
    #print(nn)
    en_list.append(en)
    nn_list.append(nn)

    # calculate the degree
    degrees = nx.classes.function.degree(G)
    degrees_list = [[n, d] for n, d in degrees]
    degrees_data = pd.DataFrame(degrees_list, columns=['node', 'degree'])
    degrees_data.to_csv('degrees_weadult%s.csv'%str(i), header =True, index=False)
    #look at degrees of the emergency department, need to change it to a dictionary to be able to look up the degree value for this node
    degrees_data.set_index('node', inplace=True)
    degrees_dict = degrees_data.to_dict()['degree']
    #check if there is data in this specific subset eg there may not be data in a weekend stress set in summer...
    if 'ADD EMERGENCY DEPT' in degrees_dict:
        emergency_degrees = degrees_dict['ADD EMERGENCY DEPT']
        print('in dict')
        no_data = False
    else:
        print('not in dict')
        no_data = True
        emergency_degrees = 0


    #degrees_list.append(list(degrees.values))
    #degrees_list.to_csv('degrees%s.csv' % str(i), header=True, index=False)
    #print('degrees')
    #print(degrees)

    # histdegrees = nx.classes.function.degree_histogram(G)
    # print('histdegrees')
    # print(histdegrees)

    # calculate the centrality of each node - fraction of nodes the incoming/outgoing edges are connected to
    incentrality = nx.algorithms.centrality.in_degree_centrality(G)
    # check if the theatre node exists in this data subset
    if 'theatre' in incentrality:
        in_theatre_centrality = incentrality['theatre']
    else:
        in_theatre_centrality = 0

    outcentrality = nx.algorithms.centrality.out_degree_centrality(G)
    if 'theatre' in outcentrality:
        out_theatre_centrality = outcentrality['theatre']
    else:
        out_theatre_centrality = 0



    #print (incentrality)
    #print(in_theatre_centrality)

    # flow hiearchy - finds strongly connected components
    if no_data == True:
        flow_hierarchy = 0
    else:
        flow_hierarchy = nx.algorithms.hierarchy.flow_hierarchy(G)
    #print('flow hierarchy')
    #print(flow_hierarchy)
    flow_h_list.append(flow_hierarchy)

    data_list.append({'month':i,'number of transfers': len(month_data_reduced['transfer_month']),'number nodes': nn,'number edges': en,'flow hierarchy': flow_hierarchy, 'emergency degrees': emergency_degrees, 'incentrality theatres': in_theatre_centrality, 'outcentrality theatres': out_theatre_centrality})
    return data_list




#read in the data from a combined csv file
alldata= pd.read_csv("all_transfers_with_ed_perf.csv")
#adm_data = alldata['dt_adm']
#adm_data.to_csv('adm_data_only.csv', header=True, index=False)
print('reading in done')

# now develop the network based on the transfer data

#find all the transfer dates on a weekend! not the admission dates
alldata['transfer_dt'] = pd.to_datetime(alldata['transfer_dt'], format="%Y-%m-%d %H:%M")
# add on columns for the true and false for weekend, true/false for ED stress and the month as a number
alldata['is_weekend'] = alldata['transfer_dt'].map(is_weekend)
alldata['ed_stress'] = alldata['breach_percentage'].map(is_ED_strained)
alldata['transfer_month'] = alldata['transfer_dt'].map(get_month)



alldata['to'].replace(to_replace=['ADD MAIN THEATRE', 'ADD MAIN THEATRE 01','ADD MAIN THEATRE 02', 'ADD MAIN THEATRE 03', 'ADD MAIN THEATRE 04' , 'ADD MAIN THEATRE 05', 'ADD MAIN THEATRE 06', 'ADD MAIN THEATRE 07','ADD MAIN THEATRE 08', 'ADD MAIN THEATRE 09', 'ADD MAIN THEATRE 10' ,'ADD MAIN THEATRE 11', 'ADD MAIN THEATRE 12', 'ADD MAIN THEATRE 14','ADD MAIN THEATRE 15', 'ADD MAIN THEATRE 16','ADD MAIN THEATRE 17', 'ADD MAIN THEATRE 18','ADD MAIN THEATRE 19', 'ADD MAIN THEATRE 20','ADD MAIN THEATRE 21', 'ADD MAIN THEATRE 22','ADD ATC THEATRE 31', 'ADD ATC THEATRE 32','ADD ATC THEATRE 33', 'ADD ATC THEATRE 34','ADD ATC THEATRE 35', 'ADD ATC THEATRE 36'],value='theatre',inplace=True)
alldata['from'].replace(to_replace=['ADD MAIN THEATRE', 'ADD MAIN THEATRE 01','ADD MAIN THEATRE 02', 'ADD MAIN THEATRE 03', 'ADD MAIN THEATRE 04' , 'ADD MAIN THEATRE 05', 'ADD MAIN THEATRE 06', 'ADD MAIN THEATRE 07','ADD MAIN THEATRE 08', 'ADD MAIN THEATRE 09', 'ADD MAIN THEATRE 10' ,'ADD MAIN THEATRE 11', 'ADD MAIN THEATRE 12', 'ADD MAIN THEATRE 14','ADD MAIN THEATRE 15', 'ADD MAIN THEATRE 16','ADD MAIN THEATRE 17', 'ADD MAIN THEATRE 18','ADD MAIN THEATRE 19', 'ADD MAIN THEATRE 20','ADD MAIN THEATRE 21', 'ADD MAIN THEATRE 22','ADD ATC THEATRE 31', 'ADD ATC THEATRE 32','ADD ATC THEATRE 33', 'ADD ATC THEATRE 34','ADD ATC THEATRE 35', 'ADD ATC THEATRE 36'],value='theatre',inplace=True)

#theatre_dictionary = {'ADD MAIN THEATRE': 'theatre', 'ADD MAIN THEATRE 01': 'theatre',
#                       'ADD MAIN THEATRE 02': 'theatre', 'ADD MAIN THEATRE 03': 'theatre',
#                       'ADD MAIN THEATRE 04': 'theatre', 'ADD MAIN THEATRE 05': 'theatre',
#                       'ADD MAIN THEATRE 06': 'theatre', 'ADD MAIN THEATRE 07': 'theatre',
#                       'ADD MAIN THEATRE 08': 'theatre', 'ADD MAIN THEATRE 09': 'theatre',
#                          'ADD MAIN THEATRE 10': 'theatre','ADD MAIN THEATRE 11': 'theatre',
#                          'ADD MAIN THEATRE 12': 'theatre', 'ADD MAIN THEATRE 14': 'theatre',
#                          'ADD MAIN THEATRE 15': 'theatre', 'ADD MAIN THEATRE 16': 'theatre',
#                          'ADD MAIN THEATRE 17': 'theatre', 'ADD MAIN THEATRE 18': 'theatre',
#                          'ADD MAIN THEATRE 19': 'theatre', 'ADD MAIN THEATRE 20': 'theatre',
#                          'ADD MAIN THEATRE 21': 'theatre', 'ADD MAIN THEATRE 22': 'theatre',
#                          'ADD ATC THEATRE 31': 'theatre', 'ADD ATC THEATRE 32': 'theatre',
#                          'ADD ATC THEATRE 33': 'theatre', 'ADD ATC THEATRE 34': 'theatre',
#                          'ADD ATC THEATRE 35': 'theatre', 'ADD ATC THEATRE 36': 'theatre'}


#weekend and weekday transfers
weekend_transfers = alldata[alldata['is_weekend']]
weekday_transfers = alldata[~alldata['is_weekend']]

stress_transfers = alldata[alldata['ed_stress']]
calm_transfers = alldata[~alldata['ed_stress']]
weekend_transfers_ed_stress = weekend_transfers[weekend_transfers['ed_stress']]
weekend_transfers_ed_calm = weekend_transfers[~weekend_transfers['ed_stress']]
weekday_transfers_ed_stress = weekday_transfers[weekday_transfers['ed_stress']]
weekday_transfers_ed_calm = weekday_transfers[~weekday_transfers['ed_stress']]


#list_of_weekend_admissions =[get_weekend_list(data) for data in data['admission_time']]
monthlist=[1,2,3,4,5,6,7,8,9,10,11,12]
en_list = []
nn_list = []
degrees_list = []
flow_h_list = []
data_list = []
data_list_stress = []
data_list_calm = []
it_is_weekend = False

#data seprated by weekend weekday
for i in monthlist:
    if it_is_weekend == True:
        month_data = weekend_transfers[weekend_transfers['transfer_month'] == i]
    else:
        month_data = weekday_transfers[weekday_transfers['transfer_month'] == i]

    number_of_transfers = len(month_data['transfer_month'])
    # drop the columns that are not needed for the graph, also select adults or children
    month_data_reduced = month_data.loc[month_data['age'] > 16].drop(['transfer_dt', 'dt_adm', 'dt_dis', 'spec', 'age', 'asa'], axis=1)
    get_network_analytics(month_data_reduced)
    print(i, number_of_transfers)

print(data_list)

analysis_data_week = pd.DataFrame(columns=['month', 'number of transfers', 'number nodes', 'number edges', 'flow hierarchy', 'emergency degrees', 'incentrality theatres', 'outcentrality theatres'], data = data_list)
#data into csv
if it_is_weekend == True:
    analysis_data_week.to_csv('analysis_data_weekend.csv', header =True, index=False)
else:
    analysis_data_week.to_csv('analysis_data_weekday.csv', header = True, index = False)

#data separated  by stress and calm overall - no weekend distinction
for i in monthlist:
    monthly_stress_data = stress_transfers[stress_transfers['transfer_month'] == i]
    monthly_calm_data = calm_transfers[calm_transfers['transfer_month'] == i]
    number_of_stress_transfers = len(monthly_stress_data['transfer month'])
    number_of_calm_transfers = len(monthly_calm_data['transfer_month'])
    # drop the columns that are not needed for the graph, also select adults or children
    monthly_stress_data_reduced = monthly_stress_data.loc[monthly_stress_data['age'] > 16].drop(['transfer_dt', 'dt_adm', 'dt_dis', 'spec', 'age', 'asa'], axis=1)
    get_network_analytics(month_data_reduced)
    print(i, number_of_transfers)

print(data_list)

analysis_data_week = pd.DataFrame(columns=['month', 'number of transfers', 'number nodes', 'number edges', 'flow hierarchy', 'emergency degrees', 'incentrality theatres', 'outcentrality theatres'], data = data_list)
if it_is_weekend == True:
    analysis_data_week.to_csv('analysis_data_weekend.csv', header =True, index=False)
else:
    analysis_data_week.to_csv('analysis_data_weekday.csv', header = True, index = False)




data_list = []
# now look at ED stress also separated by weekend and weekday
for i in monthlist:
    if it_is_weekend == True:
        ED_stress_data = weekend_transfers_ed_stress[weekend_transfers_ed_stress['transfer_month'] == i]
    else:
        ED_stress_data = weekday_transfers_ed_stress[weekday_transfers_ed_stress['transfer_month'] == i]

    number_of_transfers_stress = len(ED_stress_data['transfer_month'])
    # drop the columns that are not needed for the graph, also select adults or children
    ED_stress_data_reduced = ED_stress_data.loc[ED_stress_data['age'] > 16].drop(['transfer_dt', 'dt_adm', 'dt_dis', 'spec', 'age', 'asa'], axis=1)

    data_list_stress = get_network_analytics(ED_stress_data_reduced)


    print(i, number_of_transfers_stress)

data_list = []
for i in monthlist:
    if it_is_weekend == True:
        ED_calm_data = weekend_transfers_ed_calm[weekend_transfers_ed_calm['transfer_month'] == i]
    else:
        ED_calm_data = weekday_transfers_ed_calm[weekday_transfers_ed_calm['transfer_month'] == i]

    number_of_transfers_calm = len(ED_calm_data['transfer_month'])

    # drop the columns that are not needed for the graph, also select adults or children
    ED_calm_data_reduced =  ED_calm_data.loc[ED_calm_data['age'] > 16].drop(['transfer_dt', 'dt_adm', 'dt_dis', 'spec', 'age', 'asa'], axis=1)

    data_list_calm = get_network_analytics(ED_calm_data_reduced)

    print(i, number_of_transfers_calm)


analysis_data_week_stress = pd.DataFrame(columns=['month', 'number of transfers', 'number nodes', 'number edges', 'flow hierarchy', 'emergency degrees', 'incentrality theatres', 'outcentrality theatres'], data = data_list_stress)
analysis_data_week_calm = pd.DataFrame(columns=['month', 'number of transfers', 'number nodes', 'number edges', 'flow hierarchy', 'emergency degrees', 'incentrality theatres', 'outcentrality theatres'], data = data_list_calm)

if it_is_weekend == True:
    analysis_data_week_stress.to_csv('analysis_data_weekend_stress.csv', header =True, index=False)
    analysis_data_week_calm.to_csv('analysis_data_weekend_calm.csv', header=True, index=False)
else:
    analysis_data_week_stress.to_csv('analysis_data_weekday_stress.csv', header =True, index=False)
    analysis_data_week_calm.to_csv('analysis_data_weekday_calm.csv', header=True, index=False)
