""" SwineNet Network Simulation Model.

Simple network simulation model
"""
import datetime
from io import StringIO
from random import choices
import numpy as np
import pandas as pd

# Indices from simulated_data matrix
SU, EX, INF, DE = 0, 1, 2, 3

# Indices for farm_list
TVD, TYPE, NPIGS = 0, 2, 6

# Indices for direct transport
SRC, DEST, DATE, T_NPIGS, INSPCT = 0, 1, 2, 3, 4
column_names_direct = ['source_idx', 'dest_idx', 'event_date', 'n_pigs', 'inspect_ind']

# Indices for tour
SRC, DEST, DATE, T_NPIGS, CNTCT = 0, 1, 2, 3, 4
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


def create_slaughterhouse_list(
        farm_list: list,
        curr_run: int,
        output_dir: str) -> list:
    """ Pick 9 slaughterhouses at random to be surveilled

    :return: Index of slaughterhouses that were chosen for surveillance
    """

    slaughter_all_indices = []

    # Exclude all holdings that have 0 total pigs (slaughterhouses, medical center, etc.)
    for idx, row in enumerate(farm_list):
        if row[TYPE] == "SlaughterEnterprise":
            slaughter_all_indices.append(idx)

    # Pick one random index from 0 to 1 less than total farms
    slaughter_indices_list = choices(slaughter_all_indices, k=NUM_SH)

    # slaughter_tvd_list = map(farm_list.__getitem__, slaughter_indicies_list][0]

    # Save the info re index case to file
    # slaughters_to_save = map(slaughter_indicies_list).__getitem__, slaughter_indicies_list)
    print(f"slaughter_indicies_list: {slaughter_indices_list}")
    # print(f"slaughters_to_save: {slaughters_to_save}")
    # farm_to_save.append(curr_run)  # include curr_run
    # farm_to_save = ", ".join(map(str, farm_to_save))  # save as string (need to convert ints to string first)
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


    # curr_inspection_date = inspection_start_date
    # count_farms_slaughter = 0

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
        if (tour_arr[farm_idx, day_count] == 1):

            # Grab row where infected farm transport occurs
            inf_farm_tour = curr_tours[np.where(curr_tours[:, SRC] == farm_idx)[0]][0]

            # Check if the transport is inspected at slaughter
            if (inf_farm_tour[INSPCT] == 1):
                print("FOUND AN INSPECTED TRANSPORT with INFECTED PIGS!")
                inspect_trans_list.append(inf_farm_tour)
                # TODO - code another function for finding an infected pig

            # Get index of destination farm
            dest_tvd_id = inf_farm_tour[DEST]
            print("inf_farm_tour:", inf_farm_tour, flush=True)

            # Calculate the number of infected pigs sent on the tour
            tran_inf_pigs = min(sim_data[farm_idx, INF],
                                np.random.poisson(TAU * inf_farm_tour[T_NPIGS] * sim_data[farm_idx, INF] / N))

            print("trans inf pigs: ", tran_inf_pigs, flush=True)

            if tran_inf_pigs > 0:
                infected_pig_list.append([curr_date, 'd', tran_inf_pigs])

                # Update infected pig count for infected farm and destination farm (ensure it isn't negative)
                sim_data[farm_idx, INF] = sim_data[farm_idx, INF] - tran_inf_pigs
                sim_data[dest_tvd_id, INF] = sim_data[dest_tvd_id, INF] + tran_inf_pigs

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
                        print("ind inf pigs: ", ind_inf_pigs, flush=True)
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
                        print("p2p: ", pig_inf_pigs, flush=True)
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

                        print("formites: ", fom_inf_pigs, flush=True)
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
