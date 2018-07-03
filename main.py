import numpy as np
import itertools
import functools
#import matplotlib.pyplot as plt
import pandas as pd
#from mpl_toolkits import mplot3d
#from matplotlib import cm
#from matplotlib import colors
import networkx as nx
#from collections import Counter
#from itertools import chain
#from collections import defaultdict
import datetime



def get_data_for_patient (patientid, alldata):
    patient_data = alldata[alldata['ptid'] == patientid]
    patient_data['to'] = patient_data['to'].shift(-1)  # shifting the to column up one so that the value from below is in that slot.
    print(patient_data.iloc[0].name)
    # Make a column that has True if the location changed.
    patient_data['transfer'] = patient_data['from'] != patient_data['to']
    print(patientid)


    patient_data.fillna('discharge', inplace = True)
    #drop the columns where the to and from is the same
    patient_data.drop(patient_data[patient_data['to'] == patient_data['from']].index, axis=0, inplace=True)
    return patient_data

def get_separate_date_time(datetimeentry):
    #this returns the date in a format where the hours and days can be accessed eg d.year or d.minute

    separate_date_time = datetime.datetime.strptime(datetimeentry,"%Y-%m-%d %H:%M:%S")
    return separate_date_time

#admpoint contains the transfers of all the patients
admpoint = pd.read_csv("ADM_POINT.csv")
#subADMPOINT = ADMPOINT[['depname','evttime', '']]

# Rename the 'STUDY_SUBJECT_DIGEST' column to 'ptid'.
admpoint.rename(index=str, columns={'STUDY_SUBJECT_DIGEST': 'ptid'}, inplace=True)

#adminfo contains demographic data for the patients
adminfo = pd.read_csv("ADM_INFO.csv")


#surgeriesinfo contains details about the surgery
surgeriesinfo = pd.read_csv("SURGERIES_INFO_red.csv")

print('reading in done')

#add on the information from the other files that is needed in addition to the transfer data in admpoint
#pick the columns in the secondary files that are actually needed.
adminfo = adminfo[['adm_hosp', 'dis_hosp', 'specialty', 'admAge', 'STUDY_SUBJECT_DIGEST']]

# Set the index of the adminfo dataframe to the value we want to join to.
adminfo.set_index('STUDY_SUBJECT_DIGEST', drop=True, inplace=True)

# Join the columns in adminfo onto the admpoint dataframe based on patient ID.
admpoint = admpoint.join(adminfo, on='ptid', how='left')
print('joining')

#add on the information from the surgeries dataframe
surgeriesinfo = surgeriesinfo[['asa_rating_c', 'STUDY_SUBJECT_DIGEST']]
surgeriesinfo.set_index('STUDY_SUBJECT_DIGEST', drop=True, inplace=True)
admpoint = admpoint.join(surgeriesinfo, on='ptid', how='left')


# Remove event types we don't care about.
# Event types are: Admission, Transfer Out, Transfer In, Census, Patient Update, Discharge, Hospital Outpatient
admpoint = admpoint[admpoint.evttype != 'Census'] # removes all census lines
admpoint = admpoint[admpoint.evttype != 'Patient Update'] # removes all patient update lines

print('deleting columns')
# Create the actual transfers - currently just a list of start positions.
# Making the two columns from and two.
admpoint['from'] = admpoint['depname'] #duplicating the column but to make it the origin of the patient
admpoint['to'] = admpoint['depname'] # duplicating it into the to column
print('duplicated the columns')

##loops through all the patient ids to get the data for each one
#list_of_patient_data = [get_data_for_patient(patientid, admpoint) for patientid in admpoint['ptid'].unique()]
#print('lopiing through patient id')

## Combine together all the dataframes.
#def append_dataframes(d1, d2):
#    return d1.append(d2)
#combined_patient_data = functools.reduce(append_dataframes, list_of_patient_data)

#do the above for all the data together to save time
admpoint['extraid'] = admpoint['ptid']
admpoint['extraid'] = admpoint['extraid'].shift(-1)
admpoint['to'] = admpoint['to'].shift(-1)  # shifting the to column up one so that the value from below is in that slot.
#print(patient_data.iloc[0].name)

#the rows where the patient id changes are discharge rows
admpoint[admpoint['ptid']!=admpoint['extraid']] = 'discharge'

# Make a column that has True if the location changed
admpoint['transfer'] = admpoint['from'] != admpoint['to']
#drop the rows where the to and from is the same as they are not real transfers
admpoint.drop(admpoint[admpoint['to'] == admpoint['from']].index, axis=0, inplace=True)

#renaming the dataframe
combined_patient_data = admpoint

#separate out the date and time in the transfer data for both effective time (which is the transfer date) and admission date and discharge date.
list_of_separate_transfer_date_time = [get_separate_date_time(combined_date_time) for combined_date_time in combined_patient_data['effective_time']]
combined_patient_data['transfer_time'] = list_of_separate_transfer_date_time
print('dates separated')

list_of_separate_admission_date_time = [get_separate_date_time(combined_date_time) for combined_date_time in combined_patient_data['adm_hosp']]
combined_patient_data['admission_time'] = list_of_separate_admission_date_time

#list_of_separate_discharge_date_time = [get_separate_date_time(combined_date_time) for combined_date_time in combined_patient_data['dis_hosp']]
#combined_patient_data['discharge_time'] = list_of_separate_discharge_date_time
print(combined_patient_data)

#output the data developed.
combined_patient_data = combined_patient_data.drop(['adm_hosp', 'dis_hosp', 'extraid'], axis=1)
combined_patient_data.pd.to_csv('combined_data.csv', header = True, index=False)

# now develop the network based on the transfer data

#weighted edges first
data_only_transfers = combined_patient_data.loc[combined_patient_data['admAge'] > 20].drop(['depname','evttype','effective_time', 'specialty', 'admAge', 'asa_rating_c', 'transfer', 'transfer_time', 'admission time'], axis=1)
transfer_counts = data_only_transfers.groupby(['from', 'to']).count().reset_index()
#transfer_counts = transfer_counts[transfer_counts['ptid'] > 1]
# Get a list of tuples that contain the values from the rows.
weighted_edges = list(itertools.starmap(lambda f, t, w: (f, t, int(w)), transfer_counts.itertuples(index=False, name=None)))

G = nx.DiGraph()
print(weighted_edges)
G.add_weighted_edges_from(weighted_edges)
en=G.number_of_edges()
nn=G.number_of_nodes()
print(en)
print(nn)

#undirected graph of the same data
nondiG = nx.Graph()
nondiG.add_weighted_edges_from(weighted_edges)


#calculate the degree
degrees = nx.classes.function.degree(G)
print(degrees)
histdegrees = nx.classes.function.degree_histogram(G)
print(histdegrees)

# calculate the centrality of each node - fraction of nodes the incoming/outgoing edges are connected to
incentrality = nx.algorithms.centrality.in_degree_centrality(G)
outcentrality = nx.algorithms.centrality.out_degree_centrality(G)
print(incentrality)
print(outcentrality)


#centrality_overall = defaultdict(list)
#for k,v in chain(incentrality.items(), outcentrality.items()):
#    centrality_overall[k].append(v)

#print(centrality_overall)
#dfcentrality = pd.DataFrame.from_dict(centrality_overall,orient='index')
#print(dfcentrality)

#clustering - doesnt work for directed graphs
clustering_average = nx.algorithms.cluster.clustering(nondiG)
print('clustering in non directed graph')
print(clustering_average)

#shortest path in the directed graph, from a starting point source to a point target
#shortest_path = nx.algorithms.shortest_paths.generic.shortest_path(G, source = 'ICU', target = 'ER')
#print('shortest path is')
#print(shortest_path)

#flow hiearchy - finds strongly connected components
#flow_hierarchy = nx.algorithms.hierarchy.flow_hierarchy(G)
#print(flow_hierarchy)