""" SwineNet Network Simulation Model.

Simple network simulation model
"""
import datetime
import random
from io import StringIO
from random import choices
import numpy as np
import pandas as pd

import network_functions as fun

# Indices from simulated_data matrix
SU, EX, INF, DE, ISO = 0, 1, 2, 3, 4

# Indices for farm_list
TVD, TYPE, NPIGS = 1, 5, 6

# Indices for direct transport
SRC, DEST, DATE, T_NPIGS, INSPCT, N_DIS = 0, 1, 2, 3, 4, 5
column_names_direct = ['source_idx', 'dest_idx', 'event_date', 'n_pigs', 'inspect_ind']

# Indices for tour
CNTCT = 4
column_names_tour = ['source_idx', 'dest_idx', 'event_date', 'n_pigs', 'contact_type']

# Indices for geo
G_SRC, G_DEST, DIST = 0, 1, 2
column_names_geo = ['source_idx', 'dest_idx', 'dist']

# Tau-leap time step
TAU = 1

# Within Farm Spread
# Contact transmission rate: BET,
# Exposed to infected rate: SIG
# Disease causing death rate: DEL
BET, SIG, DEL = 2, 0.16, 0.1

# Between Farm Spread
# Other contact transmission rates
INDIRECT_TRANS_RATE = 0.01
PIG_PIG_TRANS_RATE = 0.1
FOMITE_TRANS_RATE = 0.05
GEO_TRANS_RATE = 0.01

# Evidence for surveillance design: 9 slaughterhouses chosen at random. Roughly 7,200 pigs tested. 6 pigs at least
# from the same farm. Then, roughly 134 farms from each slaughter house. Inspection occured from Jan 1 - August 31 in
# 2020
inspection_start_date = datetime.date.fromisoformat('2014-01-01')
inspection_end_date = datetime.date.fromisoformat('2014-08-30')
NUM_SH = 9
MAX_FARMS_PER_SH = 134
MAX_PIGS_PER_FARM = 6
INIT_FARM_MORT = 0.026


def create_slaughterhouse_list(
        farm_list: list,
        curr_run: int,
        output_dir: str) -> list:
    """ Pick 9 slaughterhouses at random to be surveilled

    :return: Index of slaughterhouses that were chosen for surveillance
    """

    slaughter_all_indices = []

    # Find slaughter houses by holding_cat variable
    for idx, row in enumerate(farm_list):
        if row[TYPE] == "SlaughterEnterprise":
            slaughter_all_indices.append(idx)

    # Pick one random index from 0 to 1 less than total farms
    slaughter_indices_list = choices(slaughter_all_indices, k=NUM_SH)

    # Save the info re index case to file
    print(f"slaughter_indicies_list: {slaughter_indices_list}")
    with open(output_dir + "slaughters_chosen_" + str(curr_run) + ".csv", 'w') as out_file:
        # f.write(f'{item}\n')
        # f.write(farm_to_save + "\n")
        out_file.write('\n'.join(map(str, slaughter_indices_list)))

    return slaughter_indices_list


def find_transports_to_slaughter(slaughter_indices_list: list,
                                 direct_trans_df: np.array,
                                 ) -> pd.DataFrame:
    """ Put a marker on transports to the slaughterhouses that would be tagged for inspection.

        :return: direct_trans_df with additional column for tagged for inspection
    """

    # Subset for all transports to that slaughterhouse
    slaughter_transports_df = direct_trans_df[direct_trans_df['dest_idx'].isin(slaughter_indices_list)]

    # Limit transports to only those within the inspection timeframe
    slaughter_transports_lim = slaughter_transports_df[
        (slaughter_transports_df['event_date'] >= inspection_start_date) &
        (slaughter_transports_df['event_date'] <= inspection_end_date)]

    # Create subset of transports for the slaughterhouses as destination
    for sh_idx in slaughter_indices_list:  # for each randomly selected slaughterhouse
        # Only include those with at least 6 pigs
        curr_slaughter_df = slaughter_transports_lim[(slaughter_transports_lim['dest_idx'] == sh_idx) &
                                                     (slaughter_transports_lim['n_pigs'] >= 6)]

        # Only want to include the top MAX_FARMS_PER_SH
        curr_slaughter_df = curr_slaughter_df[0:MAX_FARMS_PER_SH]

        # set inspection indicator to 1
        curr_slaughter_df['inspection_ind'] = 1

        # merge this subset with main direct transport dataframe
        direct_trans_df.update(curr_slaughter_df)

    # bug in pandas update function that converts all ints to floats
    # https://github.com/pandas-dev/pandas/issues/4094
    # Need to convert all back to ints
    direct_trans_df.iloc[:, [SRC, DEST, T_NPIGS, INSPCT]] = \
        direct_trans_df.iloc[:, [SRC, DEST, T_NPIGS, INSPCT]].values.astype(int)

    return direct_trans_df


def update_spread_within_farms_surv(
        sim_data: np.array,
        infected_farm_list: list,
        curr_date: datetime,
        infected_pig_list: list,
        mortality_rate_inc: float,
        inspect_farm_list: list) -> np.array:
    for idx in np.arange(0, sim_data.shape[0]):

        # Store information of all entries with at least 1 infected, 1 exposed, or 1 deceased pig
        if sim_data[idx, INF] > 0 or sim_data[idx, EX] > 0 or sim_data[idx, DE] > 0:
            infected_farm_list.append([curr_date, idx, sim_data[idx, SU], sim_data[idx, EX], sim_data[idx, INF],
                                       sim_data[idx, DE], sim_data[idx, ISO]])

            # Select all entries with at least 1 infected or exposed pig
            if sim_data[idx, INF] > 0 or sim_data[idx, EX] > 0:
                new_sus, new_exp, new_inf, new_dec, e_to_i = fun.run_farm_spread(sim_data[idx, SU], sim_data[idx, EX],
                                                                                 sim_data[idx, INF], sim_data[idx, DE])
                sim_data[idx, SU] = new_sus
                sim_data[idx, EX] = new_exp
                sim_data[idx, INF] = new_inf
                sim_data[idx, DE] = new_dec
                infected_pig_list.append([curr_date, 'f', e_to_i])

                # Check if mortality rate increase is more than surveillance threshold
                if sim_data[idx, DE] > 0:
                    num_tot_pigs = sim_data[idx, SU] + sim_data[idx, EX] + sim_data[idx, INF] + sim_data[idx, DE]
                    num_sus_exp = sim_data[idx, SU] + sim_data[idx, EX]

                    prop_dec = sim_data[idx, DE] / num_tot_pigs  # proportion of deceased since start of simulation

                    # if proportion is greater than surveillance threshold, then start surveillance
                    if prop_dec > (mortality_rate_inc + INIT_FARM_MORT):
                        num_discovered = inspect_herd_farm(sim_data[idx, INF], num_sus_exp)

                        if num_discovered > 0:
                            inspect_farm_list.append((idx, curr_date, num_discovered))

                            # Move the detected pigs to "isolated" category
                            sim_data[idx, INF] = sim_data[idx, INF] - num_discovered
                            sim_data[idx, ISO] = sim_data[idx, ISO] + num_discovered

    return sim_data, infected_farm_list, infected_pig_list, inspect_farm_list


def update_spread_between_farms_surv(tour_arr: np.array,
                                     direct_trans_df: pd.DataFrame,
                                     other_trans_df: pd.DataFrame,
                                     sim_data: np.array,
                                     curr_date: datetime,
                                     day_count: int,
                                     geo_data: np.array,
                                     infected_pig_list: list,
                                     inspect_trans_list: list) -> np.array:
    # grab the infected farm indices
    infected_farm_idx = np.where(sim_data[:, INF] > 0)[0]

    # Grab direct transports that are on current_date
    curr_tours = direct_trans_df[(direct_trans_df['event_date'] == curr_date)].to_numpy()

    # Loop through infected farms
    for farm_idx in infected_farm_idx:

        # Total number of pigs in the infected farm
        N = sim_data[farm_idx, SU] + sim_data[farm_idx, EX] + sim_data[farm_idx, INF]

        # Transport Network Spread

        # Check to see if the infected farm has a tour
        if tour_arr[farm_idx, day_count] == 1:

            # Grab row where infected farm transport occurs
            inf_farm_tour = curr_tours[np.where(curr_tours[:, SRC] == farm_idx)[0]][0]

            # Get index of destination farm
            dest_tvd_id = inf_farm_tour[DEST]
            # print("inf_farm_tour:", inf_farm_tour, flush=True)

            # Calculate the number of infected pigs sent on the tour
            tran_inf_pigs = min(sim_data[farm_idx, INF],
                                np.random.poisson(TAU * inf_farm_tour[T_NPIGS] * sim_data[farm_idx, INF] / N))

            # print("trans inf pigs: ", tran_inf_pigs, flush=True)

            if tran_inf_pigs > 0:
                infected_pig_list.append([curr_date, 'd', tran_inf_pigs])

                # Update infected pig count for infected farm and destination farm (ensure it isn't negative)
                sim_data[farm_idx, INF] = sim_data[farm_idx, INF] - tran_inf_pigs
                sim_data[dest_tvd_id, INF] = sim_data[dest_tvd_id, INF] + tran_inf_pigs

                # Check if the transport is inspected at slaughter
                if (inf_farm_tour[INSPCT] == 1):
                    num_discovered = inspect_herd_slaughter(inf_farm_tour[T_NPIGS], tran_inf_pigs)
                    inspect_trans_list.append(np.append(inf_farm_tour, num_discovered))

                    # if pigs are detected at slaughterhouse, then isolate the infected pigs on the origin farm
                    if num_discovered > 0:
                        num_sus_exp = sim_data[farm_idx, SU] + sim_data[farm_idx, EX]
                        num_discovered_farm = inspect_herd_farm(sim_data[farm_idx, INF], num_sus_exp)

                        # Move the detected pigs to "isolated" category
                        sim_data[farm_idx, INF] = sim_data[farm_idx, INF] - num_discovered_farm
                        sim_data[farm_idx, ISO] = sim_data[farm_idx, ISO] + num_discovered_farm

            # Check for indirect contact types
            indirect_contacts = other_trans_df[(other_trans_df['event_date'] == curr_date) &
                                               (other_trans_df['source_idx'] == farm_idx)].to_numpy()

            if len(indirect_contacts) > 0:

                for curr_tour in indirect_contacts:

                    # Get index of destination farm
                    dest_idx = curr_tour[DEST]

                    if curr_tour[CNTCT] == 'i':

                        # Number of pigs on the destination farm
                        dest_num_pigs = sim_data[dest_idx, SU]

                        # Calculate the number of pigs indirectly infected
                        ind_inf_pigs = min(sim_data[dest_idx, SU], np.random.poisson(
                            TAU * tran_inf_pigs / inf_farm_tour[T_NPIGS] * INDIRECT_TRANS_RATE * dest_num_pigs))
                        # print("ind inf pigs: ", ind_inf_pigs, flush=True)
                        infected_pig_list.append([curr_date, 'i', ind_inf_pigs])

                        if ind_inf_pigs > 0:
                            # Update infected pig count for the indirect destination farm
                            sim_data[dest_idx, INF] = sim_data[dest_idx, INF] + ind_inf_pigs
                            sim_data[dest_idx, SU] = sim_data[dest_idx, SU] - ind_inf_pigs

                    elif curr_tour[CNTCT] == 'p':

                        # number of pigs heading to destination farm that mix with infected herd
                        pigs_2_dest = curr_tour[T_NPIGS]

                        # Calculate the number of pigs infected
                        pig_inf_pigs = np.random.poisson(
                            TAU * (tran_inf_pigs / inf_farm_tour[T_NPIGS]) * PIG_PIG_TRANS_RATE *
                            pigs_2_dest)
                        # print("p2p: ", pig_inf_pigs, flush=True)
                        infected_pig_list.append([curr_date, 'p', pig_inf_pigs])

                        if pig_inf_pigs > 0:
                            # Update infected pig count for the indirect destination farm
                            sim_data[dest_idx, INF] = sim_data[dest_idx, INF] + pig_inf_pigs

                    elif curr_tour[CNTCT] == 't':

                        # number of pigs heading to destination farm that mix with infected herd
                        pigs_2_dest = curr_tour[T_NPIGS]

                        # Calculate the number of pigs infected by fomites (uncleaned truck)
                        fom_inf_pigs = np.random.poisson(
                            TAU * tran_inf_pigs / inf_farm_tour[T_NPIGS] * FOMITE_TRANS_RATE * pigs_2_dest)

                        # print("formites: ", fom_inf_pigs, flush=True)
                        infected_pig_list.append([curr_date, 't', fom_inf_pigs])

                        if fom_inf_pigs > 0:
                            # Update infected pig count for the indirect destination farm
                            sim_data[dest_idx, INF] = sim_data[dest_idx, INF] + fom_inf_pigs

        # Geographic Network Spread

        # Find any entries for infected farm in the geographic network
        geo_inf_arr = geo_data[np.where(geo_data[:, G_SRC] == farm_idx)[0]]

        for curr_geo in geo_inf_arr:

            # get the index of the destination farm (returns 0 if the farm is not active during the applicable year(s))
            dest_geo_idx = curr_geo[G_DEST]

            # calculate number of pigs infected thru aerial spread
            geo_inf_pigs = min(sim_data[dest_geo_idx, SU],
                               np.random.poisson(TAU * sim_data[dest_geo_idx, SU] * sim_data[farm_idx, INF] / N *
                                                 GEO_TRANS_RATE))

            if geo_inf_pigs > 0:
                infected_pig_list.append([curr_date, 'g', geo_inf_pigs])
                # Update infected pig count for the indirect destination farm
                sim_data[dest_geo_idx, INF] = sim_data[dest_geo_idx, INF] + geo_inf_pigs
                sim_data[dest_geo_idx, SU] = sim_data[dest_geo_idx, SU] - geo_inf_pigs

    return sim_data, infected_pig_list, inspect_trans_list


def inspect_herd_slaughter(num_trans: int,
                           num_inf_pigs: int):
    # Draw 6 random sample of pigs from the transported herd
    pigs_sampled = random.sample(range(num_trans), MAX_PIGS_PER_FARM)

    # Determine if any of the pigs that were sampled were also infected
    # Let first num_inf_pigs to be the infected pigs (0 is included in the pig sampling above so < num_inf_pigs)
    count = len([i for i in pigs_sampled if i < num_inf_pigs])

    return count


def inspect_herd_farm(num_inf_pigs: int,
                      num_non_inf_pigs: int):
    # Test all pigs on farm
    # TODO: include delay in testing
    # TODO: include likelihood of farmer choosing to test pigs
    # TODO: include specificity and sensitivity of testing
    pigs_detected = num_inf_pigs  # initial assumption: all pigs on the farm are detected

    return pigs_detected


def pick_test_dates(test_interval_days: datetime,
                    start_date: datetime,
                    end_date: datetime):
    # List to return testing dates at the farms
    testing_dates = []

    # Select a random number for the number of days after the start of the simulation to start testing
    # Number is no longer than the surveillance interval window
    num_days_after_start = choices(range(1, test_interval_days), k=1)[0]  # returns a list so need the first element

    first_test_date = start_date + datetime.timedelta(days=num_days_after_start)

    if (first_test_date > end_date):
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
                           curr_date):
    # Loop through tested farms list
    for idx, farm_idx in enumerate(test_farm_idx):
        tmp_inf = sim_data[farm_idx[2], INF]
        tmp_su = sim_data[farm_idx[2], SU]
        if tmp_inf > 0:
            print('farm pigs detected: ', farm_idx, str(tmp_inf))

            # Test pigs on the farm
            num_detected = inspect_herd_farm(tmp_inf, tmp_su)

            if num_detected > 0:
                inspect_farm_list.append((farm_idx[2], curr_date, farm_idx[1], num_detected))

                # Move detected pigs from infected to detected
                sim_data[farm_idx[2], INF] = sim_data[farm_idx[2], INF] - num_detected
                sim_data[farm_idx[2], ISO] = sim_data[farm_idx[2], ISO] + num_detected

    return sim_data, inspect_farm_list
