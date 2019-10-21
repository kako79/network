
# The columns we need to include in the generated data are:
# 'ptid', 'transfer_dt', 'dt_adm', 'dt_dis', 'spec', 'age','asa', 'breach_percentage', 'strain', 'bedsfree', 'from', 'to'

import pandas as pd
import numpy as np
from random import randint, random
from datetime import datetime, timedelta


def generate_location_data(patient_count: int, location_count: int) -> pd.DataFrame:
    row_count = patient_count * 10

    patient_ids_column = np.random.randint(1, patient_count + 1, size=row_count)

    locations_column = np.array([str(chr(randint(65, 65 + location_count - 1))) for i in range(row_count)])

    base_date = datetime.utcnow()
    transfer_dt_column = np.array([base_date + timedelta(days=randint(0, 100), seconds=randint(0, 86400)) for i in range(row_count)])

    df = pd.DataFrame()
    df['ptid'] = pd.Series(patient_ids_column)
    df['loc'] = pd.Series(locations_column)
    df['transfer_dt'] = pd.Series(transfer_dt_column)

    first_transfer_dt = df.groupby('ptid').min()['transfer_dt']
    last_transfer_dt = df.groupby('ptid').max()['transfer_dt']

    df['dt_adm'] = df['ptid'].map(first_transfer_dt)
    df['dt_dis'] = df['ptid'].map(last_transfer_dt)

    dates = df['transfer_dt'].unique()

    breach_pct_lookup = {date: randint(0, 100) for date in dates}
    df['breach_percentage'] = df['transfer_dt'].map(breach_pct_lookup)

    strain_lookup = {date: random() for date in dates}
    df['strain'] = df['transfer_dt'].map(strain_lookup)

    bedsfree_lookup = {date: randint(0, 800) for date in dates}
    df['bedsfree'] = df['transfer_dt'].map(bedsfree_lookup)

    patient_ids = pd.Series(patient_ids_column).unique()

    ages_lookup = {ptid: randint(5, 100) for ptid in patient_ids}
    df['age'] = df['ptid'].map(ages_lookup)
    df['spec'] = df['age']
    df['asa'] = df['age']

    return df.sort_values(by=['ptid', 'transfer_dt']).reset_index(drop=True)


def get_transfers(data: pd.DataFrame) -> pd.DataFrame:
    df = data.copy()
    df['from'] = df['loc']
    df['to_ptid'] = pd.Series(np.roll(df['ptid'].values, -1))
    df['to'] = pd.Series(np.roll(df['loc'].values, -1))
    df = df[df['ptid'] == df['to_ptid']]
    return df.drop(columns=['loc', 'to_ptid'])


location_data = generate_location_data(1000, 10)
transfer_data = get_transfers(location_data)

transfer_data.to_csv('generated_transfer_data.csv', header=True, index=False)
