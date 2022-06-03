""" SwineNet Network Simulation Model.

Simple network simulation model
"""
import datetime
from io import StringIO
from random import choices
import pandas as pd

import transmit_disease as ts
import global_setup as gs


def pick_test_dates(test_interval_days: datetime,
                    start_date: datetime,
                    end_date: datetime):
    # List to return testing dates at the farms
    testing_dates = []

    # Select a random number for the number of days after the start of the simulation to start testing
    # Number is no longer than the surveillance interval window
    num_days_after_start = choices(range(1, test_interval_days), k=1)[0]  # returns a list so need the first element

    first_test_date = start_date + datetime.timedelta(days=num_days_after_start)

    if first_test_date > end_date:
        print("First test date found after the end_date")
    else:
        # Add the test date to the list of testing_dates
        testing_dates.append(first_test_date)

        # Keep adding testing dates until the end of the surveillance run is reached
        new_test_date = first_test_date
        while new_test_date + datetime.timedelta(days=test_interval_days) <= end_date:
            new_test_date = new_test_date + datetime.timedelta(days=test_interval_days)
            testing_dates.append(new_test_date)

    return testing_dates


# Create df of farm_idx that are to be tested based on contact network metrics
def create_test_farm_list(farm_dict,
                          test_contact_type,
                          test_top_thresh):
    # Read test_list from file
    with open('../data/top_deg_list_all_' + str(test_top_thresh) + '.csv') as f:
        # skip header line
        header = next(f).strip()
        # read in farm list
        text = "\n".join(line for line in f)
        test_farm_df = pd.read_csv(StringIO(text))

    # Add the column headings
    test_farm_df.columns = header.split(',')
    test_farm_df_lim = test_farm_df.copy()
    test_farm_df = test_farm_df[test_farm_df['contact_net_type'].isin(test_contact_type)]
    test_farm_df_lim['tvd_idx'] = test_farm_df['tvd_nr'].map(farm_dict)

    # Check for missing tvd_nrs and drop (some tvds are not active every year)
    test_farm_df_lim = test_farm_df_lim.loc[test_farm_df_lim['tvd_idx'].notnull()]

    # convert tvd_idx to integer
    test_farm_df_lim.loc[:, 'tvd_idx'] = test_farm_df_lim.loc[:, 'tvd_idx'].values.astype(int)

    # Return the farm_idx array
    test_farm_list = test_farm_df_lim.values.tolist()

    return test_farm_list


def network_surv_test_farm(test_farm_idx,
                           sim_data,
                           inspect_farm_list,
                           curr_date,
                           control):
    # Loop through tested farms list
    for idx, farm_idx in enumerate(test_farm_idx):
        # farm_idx[0]=tvd, farm_idx[1]=contact type, farm_idx[2] = idx
        farm_ind = farm_idx[gs.NET_IDX]
        tmp_inf = sim_data[farm_ind, gs.INF]

        if tmp_inf > 0:
            # print('farm pigs detected: ', farm_idx, str(tmp_inf))

            # Test pigs on the farm
            num_detected = ts.inspect_herd_farm(tmp_inf,
                                                sim_data[farm_ind, gs.SU] + sim_data[farm_ind, gs.SUS],
                                                sim_data[farm_ind, gs.EX] + sim_data[farm_ind, gs.EXS],
                                                sim_data[farm_ind, gs.ASY])

            if num_detected > 0:
                inspect_farm_list.append((farm_ind, curr_date, farm_idx[gs.NET_CNTCT], num_detected))

                # Move detected pigs from infected to detected
                sim_data[farm_ind, gs.INF] = sim_data[farm_ind, gs.INF] - num_detected
                sim_data[farm_ind, gs.ISO] = sim_data[farm_ind, gs.ISO] + num_detected

                if control == "quarantine":
                    # Move susceptible to quarantine
                    sim_data[farm_ind, gs.QUA_S] = sim_data[farm_ind, gs.SU] + sim_data[farm_ind, gs.SUS] + sim_data[farm_ind, gs.QUA_S]
                    sim_data[farm_ind, gs.SU] = 0
                    sim_data[farm_ind, gs.SUS] = 0
                    # Move exposed to quarantineE
                    sim_data[farm_ind, gs.QUA_E] = sim_data[farm_ind, gs.EX] + sim_data[farm_ind, gs.EXS] + sim_data[farm_ind, gs.QUA_S]
                    sim_data[farm_ind, gs.EX] = 0
                    sim_data[farm_ind, gs.EXS] = 0
                    # Move asymptomatic to quarantine_A
                    sim_data[farm_ind, gs.QUA_A] = sim_data[farm_ind, gs.ASY] + sim_data[farm_ind, gs.QUA_A]
                    sim_data[farm_ind, gs.ASY] = 0

    return sim_data, inspect_farm_list
