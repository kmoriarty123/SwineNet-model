""" SwineNet Network Simulation Model.

Simple network simulation model
"""
import datetime
# from io import StringIO
from random import choices
import numpy as np
import pandas
import pandas as pd

import global_setup as gs


# def create_farm_dict(
#        start_year: int,
#        end_year: int
# ):
#    """ Initiates the farm matrix.
#
#    Only active farms between start_date and end_date.
#    """
#    # Don't need start_date: datetime, end_date: datetime parameters since we take all farms (geographic)
#    # From file, import farms from agis_data and create dict
#    farm_df = pd.read_csv('../data/agis_data_lim.csv', encoding='latin-1')
#    farm_df = farm_df[(farm_df['year'] <= end_year) & (farm_df['year'] >= start_year)]
#
#    # replace all n_pigs with zeros
#    farm_df['tot_pigs'] = farm_df['tot_pigs'].fillna(0)
#
#    farm_list = farm_df.values.tolist()
#
#    farm_dict = {}
#    for idx, farm_info in enumerate(farm_list):
#        farm_dict[farm_info[gs.TVD]] = idx
#
#    # Return Dictionary
#    return farm_dict, farm_list


def set_index_case(
        farm_list: list,
        curr_run: int,
        output_dir: str,
        disease: str,
        idx_case_factor: int) -> tuple[int, int]:
    """ Pick 1 pig on a farm to be infected.
    More weight is given to farms that are more likely to be infected.
    These weights are dependent on disease.
    :return: Index of farm index and farm tvd
    """
    farm_indices = []
    farm_weights = []

    # choose weights based on disease (preprocessed in R preprocessing files)
    if disease == 'ASF':
        if idx_case_factor == 1:
            tmp_idx_weights = gs.IDX_WGHT_ASF_1
        elif idx_case_factor == 2:
            tmp_idx_weights = gs.IDX_WGHT_ASF_2
        else:
            tmp_idx_weights = gs.IDX_WGHT_ASF_3
    elif disease == 'PRRS':
        if idx_case_factor == 1:
            tmp_idx_weights = gs.IDX_WGHT_PRRS_1
        elif idx_case_factor == 2:
            tmp_idx_weights = gs.IDX_WGHT_PRRS_2
        else:
            tmp_idx_weights = gs.IDX_WGHT_PRRS_3
    elif disease == 'APP':
        if idx_case_factor == 1:
            tmp_idx_weights = gs.IDX_WGHT_APP_1
        elif idx_case_factor == 2:
            tmp_idx_weights = gs.IDX_WGHT_APP_2
        else:
            tmp_idx_weights = gs.IDX_WGHT_APP_3

    # Exclude all holdings that have 0 total pigs (slaughterhouses, medical center, etc.)
    for idx, row in enumerate(farm_list):
        if row[gs.NPIGS] > 0:
            farm_indices.append(idx)
            farm_weights.append(row[tmp_idx_weights])

    # Pick one index from 0 to 1 less than total farms
    index_farm_idx = choices(farm_indices, k=1, weights=farm_weights)[0]  # returns a list so need the first element

    print(f"info re index case: {farm_list[index_farm_idx]}", flush=True)
    index_farm_tvd = farm_list[index_farm_idx][gs.TVD]

    # Save the info re index case to file
    farm_to_save = farm_list[index_farm_idx]
    farm_to_save.append(curr_run)  # include curr_run
    farm_to_save = ", ".join(map(str, farm_to_save))  # save as string (need to convert ints to string first)
    with open(output_dir + "index_case_" + str(curr_run) + ".csv", 'w') as f:
        f.write(farm_to_save + "\n")

    return index_farm_idx, index_farm_tvd


def update_sim_data(
        index_farm_idx: int,
        sim_data: np.array) -> np.array:
    # update index_case with 1 infected pig.
    sim_data[index_farm_idx, gs.INF] = 1

    # remove one pig from index_case susceptible
    sim_data[index_farm_idx, gs.SU] = sim_data[index_farm_idx, gs.SU] - 1

    return sim_data


# For all farms with sows, move the susceptible pigs to compartment SUS to handle them differently for PRRS
def update_sim_data_sows_PRRS(
        farm_list: list,
        sim_data: np.array) -> np.array:
    for idx, row in enumerate(farm_list):
        if row[gs.SOW_IND] > 0:
            sim_data[idx, gs.SUS] = sim_data[idx, gs.SU]
            sim_data[idx, gs.SU] = 0

    return sim_data


def create_tour_arr(
        start_date: datetime,
        end_date: datetime,
        farm_dict: dict,
        direct_transport_df: pandas.DataFrame
) -> np.array:
    """ Creates the direct transport tour data frame, the other contact tour dataframe and the tour array.

    Only tours between start_date and end_date.
    Dataframe is saved with farm indices and not farm tvds
    tour_arr is a binary 2-d array which is 1 for farm_idx that has a direct transport on that day.
    """

    direct_transport_df = direct_transport_df[(direct_transport_df['event_date'] >= start_date) &
                                              (direct_transport_df['event_date'] <= end_date)]

    # Create tour array

    # number of difference in days
    diff_days = (end_date - start_date).days

    # initialize tour array
    tour_arr = np.zeros((len(farm_dict), diff_days + 1))

    # update direct_transport_df with 1s when the farm_idx has a tour on that day
    tmp_date = start_date
    day_count = 0

    while tmp_date <= end_date:
        active_src_list = direct_transport_df.loc[direct_transport_df['event_date'] == tmp_date, 'source_idx']
        for source_idx in active_src_list:
            tour_arr[source_idx, day_count] = 1
        tmp_date += datetime.timedelta(days=1)
        day_count = day_count + 1

    # Return dataframe
    return tour_arr, direct_transport_df
