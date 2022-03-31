""" SwineNet Network Simulation Model.

Simple network simulation model
"""
import datetime
from io import StringIO
from random import choices
import numpy as np
import pandas
import pandas as pd

# Indices from simulated_data matrix
SU, EX, INF, DE, ISO = 0, 1, 2, 3, 4

# Indices for farm_list
TVD, NPIGS, IDX_WGHT = 0, 6, 9

# Indices for tour
SRC, DEST, DATE, T_NPIGS, CNTCT = 0, 1, 2, 3, 4
column_names_direct = ['source_idx', 'dest_idx', 'event_date', 'n_pigs']
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


def create_farm_dict(
        start_year: int,
        end_year: int
):
    """ Initiates the farm matrix.

    Only active farms between start_date and end_date.
    """
    # Don't need start_date: datetime, end_date: datetime parameters since we take all farms (geographic)
    # From file, import farms from agis_data and create dict
    farm_df = pd.read_csv('../data/agis_data_lim.csv', encoding='latin-1')
    farm_df = farm_df[(farm_df['year'] <= end_year) & (farm_df['year'] >= start_year)]

    # replace all n_pigs with zeros
    farm_df['tot_pigs'] = farm_df['tot_pigs'].fillna(0)

    farm_list = farm_df.values.tolist()

    farm_dict = {}
    for idx, farm_info in enumerate(farm_list):
        farm_dict[farm_info[TVD]] = idx

    # Return Dictionary
    return farm_dict, farm_list


def set_index_case(
        farm_list: list,
        curr_run: int,
        output_dir: str) -> tuple[int, int]:
    """ Pick 1 pig on random farm to be infected

    :return: Index of farm index and farm tvd
    """

    farm_indices = []
    farm_weights = []

    # Exclude all holdings that have 0 total pigs (slaughterhouses, medical center, etc.)
    for idx, row in enumerate(farm_list):
        if row[NPIGS] > 0:
            farm_indices.append(idx)
            farm_weights.append(row[IDX_WGHT])

    # Pick one random index from 0 to 1 less than total farms
    index_farm_idx = choices(farm_indices, k=1, weights=farm_weights)[0]  # returns a list so need the first element

    print(f"info re index case: {farm_list[index_farm_idx]}", flush=True)
    index_farm_tvd = farm_list[index_farm_idx][0]

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
    # update index_case with 1 infected pig
    sim_data[index_farm_idx, INF] = 1

    # remove one pig from index_case susceptible
    sim_data[index_farm_idx, SU] = sim_data[index_farm_idx, SU] - 1

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


def create_geo_arr(
        farm_dict: dict
) -> np.array:
    """Create geo network array for only farms <2km and without contact_type "g" and replace tvd_ids for farm_idx
    :return: np.array
    """
    # Read data from file
    geo_net_all = pd.read_csv('../data/geo_network.csv', header=0)

    # Strip column headings
    geo_net_all.columns = geo_net_all.columns.str.strip()

    # Convert tvds to ints and distances to floats
    geo_net_all.iloc[:, 0:1] = geo_net_all.iloc[:, 0:1].values.astype(int)
    geo_net_all.iloc[:, 2] = geo_net_all.iloc[:, 2].values.astype(float)

    # Limit geo net for <2km
    geo_net = geo_net_all.loc[geo_net_all['dist'] <= 2]

    # Make a copy of as to avoid SettingWithCopyWarning: A value is trying to be set on a copy of a slice from DF...
    geo_net = geo_net.copy()

    # Map the tvd_id with the farm_idx
    geo_net.loc[:, 'source_idx'] = geo_net.loc[:, 'tvd_source'].map(farm_dict)
    geo_net.loc[:, 'dest_idx'] = geo_net.loc[:, 'tvd_dest'].map(farm_dict)

    # Drop any values that weren't matched as not in active agis database
    geo_net.dropna(subset=['source_idx', 'dest_idx'], inplace=True, axis=0)

    # Remove contact_type_column, tvd_source, and tvd_dest
    geo_net = geo_net.drop(['tvd_source', 'tvd_dest', 'contact_type'], axis=1)

    # Reindex columns
    geo_net = geo_net.reindex(columns=column_names_geo)

    # Convert idx to int (not sure why they are floats)
    geo_net['source_idx'] = geo_net['source_idx'].astype(int)
    geo_net['dest_idx'] = geo_net['dest_idx'].astype(int)

    # Convert to numpy array
    geo_arr = geo_net.to_numpy().astype(int)

    return geo_arr


def update_spread_within_farms(
        sim_data: np.array,
        infected_farm_list: list,
        curr_date: datetime,
        infected_pig_list: list) -> np.array:
    for idx in np.arange(0, sim_data.shape[0]):

        # Store information of all entries with at least 1 infected, 1 exposed, or 1 deceased pig
        if sim_data[idx, INF] > 0 or sim_data[idx, EX] > 0 or sim_data[idx, DE] > 0:
            infected_farm_list.append([curr_date, idx, sim_data[idx, SU], sim_data[idx, EX], sim_data[idx, INF],
                                       sim_data[idx, DE], sim_data[idx, ISO]])

        # Select all entries with at least 1 infected or exposed pig
        if sim_data[idx, INF] > 0 or sim_data[idx, EX] > 0:
            new_sus, new_exp, new_inf, new_dec, e_to_i = run_farm_spread(sim_data[idx, SU], sim_data[idx, EX],
                                                                         sim_data[idx, INF], sim_data[idx, DE])
            sim_data[idx, SU] = new_sus
            sim_data[idx, EX] = new_exp
            sim_data[idx, INF] = new_inf
            sim_data[idx, DE] = new_dec
            infected_pig_list.append([curr_date, 'f', e_to_i])

    return sim_data, infected_farm_list, infected_pig_list


# Define the simulation function
def run_farm_spread(sus, exp, inf, dec):
    # Initial number of infected and recovered individuals, I0 and R0.
    S0, E0, I0, D0 = sus, exp, inf, dec

    # Total pig population on the farm, N.
    N = S0 + E0 + I0

    # Calculate expected values and probabilities
    exp_S_to_E = TAU * BET * S0 * I0 / N
    prob_E_to_I = 1 - np.exp(-SIG * TAU)
    prob_I_to_D = 1 - np.exp(-DEL * TAU)

    # Calculate the random draws
    S_to_E = np.random.poisson(exp_S_to_E)
    E_to_I = np.random.binomial(E0, prob_E_to_I)
    I_to_D = np.random.binomial(I0, prob_I_to_D)

    S = S0 - min(S_to_E, S0)  # ensure S is never negative
    E = E0 + min(S_to_E, S0) - E_to_I
    I = I0 + E_to_I - I_to_D
    D = D0 + I_to_D

    return S, E, I, D, E_to_I


def update_spread_between_farms(tour_arr: np.array,
                                direct_trans_df: pd.DataFrame,
                                other_trans_df: pd.DataFrame,
                                sim_data: np.array,
                                curr_date: datetime,
                                day_count: int,
                                geo_data: np.array,
                                infected_pig_list: list) -> np.array:
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

    return sim_data, infected_pig_list
