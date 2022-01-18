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

# Contact transmission rate: BET,
# Exposed to infected rate: SIG
# Disease causing death rate: DEL
BET, SIG, DEL = 5, 0.2, 0.1

# Other cantact transmission rates
INDIRECT_TRANS_RATE = 0.01
PIG_PIG_TRANS_RATE = 0.1
FOMITE_TRANS_RATE = 0.05
GEO_TRANS_RATE = 0.01


# Evidence for Choice of above rates
# BET: Assumption: all pigs interact with all other pigs in at least once in 1 day. Contact rate would be 1.
# Transmission
# rate would
# be ? (Need to get details from Antoine)
# SIG: Incubation period is 5 - 15 days: https://www.daera-ni.gov.uk/articles/african-swine-fever
# DEL: death rate is 4-9 days after exposure? I set to 10. https://www.nature.com/articles/s41598-020-62736-y

def create_farm_dict(
        start_year: int,
        end_year: int
):
    """ Initiates the farm matrix.

    Only active farms between start_date and end_date.
    """
    # Don't need start_date: datetime, end_date: datetime parameters since we take all farms (geographic)

    # From file, import farms from agis_data and create dict
    # with open('../data/agis_data_lim.csv') as f:
    # print("s{}s".format(start_year))

    # skip header line
    # next(f)

    # read in farms that are only active during the start year and end year
    # text = "\n".join([line for line in f if
    #                  int(line.split(',')[1]) == start_year or
    #                  int(line.split(',')[1]) == end_year])
    # farm_df = pd.read_csv(StringIO(text))

    # Concat the header and text and reset the Index.
    # farm_dict = pd.concat([header, farm_dict]).reset_index(drop=True)

    # farm_df['index'] = farm_df.reset_index().index

    # Convert df to dict with row index as key and other variables as list
    # farm_dict = farm_df.T.to_dict('list')

    # Create farm_key dictionary
    # farm_key_df = farm_df.iloc[:,0:1].to_dict()

    # Invert the values so now tvd_nr are the keys and index is the value
    # farm_key = {int(val): key for key, val in farm_key_df.items()}
    print("Inside create_farm_dict")
    farm_df = pd.read_csv('data/agis_data_lim.csv', encoding='latin-1')
    farm_df = farm_df[(farm_df['year'] <= end_year) & (farm_df['year'] >= start_year)]
    farm_list = farm_df.values.tolist()

    farm_dict = {}
    for idx, farm_id in enumerate(farm_list):
        farm_dict[farm_id[0]] = idx

    print("Inside create_farm_dict, after farm_dict creation")

    # Return Dictionary
    return farm_dict, farm_list


def create_tour_df(
        start_date: datetime,
        end_date: datetime
) -> pd.DataFrame:
    """ Creates the tour data frame.

    Only tours between start_date and end_date.
    """

    # From file, import farms from agis_data and create dict
    with open('data/tour_network.csv') as f:
        # skip header line
        header = next(f).strip()

        # read in farms that are only active during the start year and end year
        text = "\n".join([line for line in f if
                          start_date <= datetime.date.fromisoformat(line.split(',')[2]) <= end_date])
        tour_df = pd.read_csv(StringIO(text))

        # Add the column headings
        tour_df.columns = header.split(',')

        # Convert event_date to datetime object
        tour_df['event_date'] = pd.to_datetime(tour_df['event_date']).dt.date
        print("after", tour_df)
        # Convert tvds to ints
        tour_df.iloc[:, 0:1] = tour_df.iloc[:, 0:1].values.astype(int)
        print("before", tour_df)

    # Return dataframe
    return tour_df


def create_geo_arr():
    """Create geo network array for only farms <2km and without contact_type "g"
    :return: np.array
    """
    # Read data from file
    geo_net_all = pd.read_csv('data/geo_network.csv')

    # Limit geo net for <2km
    geo_net = geo_net_all[geo_net_all['dist'] <= 2]

    # Remove contact_type_colum and convert to numpy array
    geo_net = geo_net.drop(columns='contact_type').to_numpy()

    return geo_net


def set_index_case(
        farm_list: list) -> tuple[int, int]:
    """ Pick 1 pig on random farm to be infected

    :return: Index of farm index
    """
    # TODO: calculate different probabilities for different farms based on "fencing" and "closeness" to wild boar
    # can add to function choices the parameter weights (i.e., weights = [10, 1, 1]) to achieve this

    farm_indices = []

    # Exclude all holdings that have 0 total pigs (slaughterhouses, medical center, etc.)
    for idx, row in enumerate(farm_list):
        if row[6] > 0:
            farm_indices.append(idx)

    # Pick one random index from 0 to 1 less than total farms
    index_farm = choices(farm_indices, k=1)[0]  # returns a list so need the first element

    print(f"info re index case: {farm_list[index_farm]}")
    inf_tvd = farm_list[index_farm][0]

    return index_farm, inf_tvd


def create_sim_data(
        index_case: int,
        farm_dict: dict,
        farm_list: list) -> np.array:
    # initialize num_farms x 3 integer array (columns: susceptible, exposed, infected, deceased)
    sim_data = np.zeros((len(farm_list), 4))

    # update susceptible values with num of pigs for each farm
    for idx, row in enumerate(farm_list):
        sim_data[idx, 0] = row[6]

    # update index_case with 1 infected pig
    sim_data[index_case, INF] = 1

    # remove one pig from index_case susceptible
    sim_data[index_case, SU] = sim_data[index_case, SU] - 1

    # Replace all nans with 0.0
    sim_data = np.nan_to_num(sim_data)

    print(f"index case: {index_case} and num pigs: {sim_data[index_case, SU]} from w/in create")
    return sim_data


def update_spread_within_farms(
        sim_data: np.array,
        infected_farm_list: list,
        curr_date: datetime) -> np.array:

    # Select all entries with at least 1 infected pig
    for idx in np.arange(0, sim_data.shape[0]):
        if sim_data[idx, INF] > 0:

            infected_farm_list.append([curr_date, idx, sim_data[idx, SU], sim_data[idx, EX], sim_data[idx, INF],
                                       sim_data[idx, DE]])
            new_sus, new_exp, new_inf, new_dec = \
                run_farm_spread(sim_data[idx, SU], sim_data[idx, EX], sim_data[idx, INF], sim_data[idx, DE])
            sim_data[idx, SU] = new_sus
            sim_data[idx, EX] = new_exp
            sim_data[idx, INF] = new_inf
            sim_data[idx, DE] = new_dec

    return sim_data, infected_farm_list


# Define the simulation function
def run_farm_spread(sus, exp, inf, dec):
    # Initial number of infected and recovered individuals, I0 and R0.
    S0, E0, I0, D0 = sus, exp, inf, dec
    # print(S0, E0, I0)

    # Total pig population on the farm, N.
    N = S0 + E0 + I0

    # handle the case of 0 susceptible pigs
    if S0 >= 1:
        S = S0 - BET * S0 * I0 / N
        E = E0 + BET * S0 * I0 / N - SIG * E0

        # make sure S is never negative
        if S < 0:
            S = 0

    else:
        S = S0
        E = E0 - SIG * E0

    # TODO handle the case of 0 exposed pigs

    I = I0 + SIG * E0 - DEL * I0
    D = D0 + DEL * I0

    return S, E, I, D


def update_spread_between_farms(farm_dict: dict,
                                tour_net: pd.DataFrame,
                                sim_data: np.array,
                                curr_date: datetime,
                                geo_data: np.array,
                                infected_pig_list: list) -> np.array:
    infected_farm_idx = np.where(sim_data[:, 2] > 0)[0]

    # Grab tours that are on current_date only direct contact_type
    curr_tours = tour_net[(tour_net['event_date'] == curr_date) & (tour_net['contact_type'] == "d")].to_numpy()

    # Loop through infected farms
    for farm_idx in infected_farm_idx:

        infected_tvd_id = list(farm_dict.values()).index(farm_idx)
        infected_tvd = list(farm_dict.keys())[infected_tvd_id]

        # Total number of pigs in the infected farm
        N = sim_data[farm_idx, SU] + sim_data[farm_idx, EX] + sim_data[farm_idx, INF]

        # Transport Network Spread

        # Check to see if the infected farm has a tour
        if sum(np.isin(curr_tours[:, 0], infected_tvd)):  # sum counts how many booleans

            # Grab row where infected farm transport occurs
            # inf_farm_tour = curr_tours[np.isin(infected_tvd, curr_tours[:, 0])]
            inf_farm_tour = curr_tours[np.where(curr_tours[:, 0] == infected_tvd)[0]][0]
            print(f"Found a tour of an infected farm! {inf_farm_tour}")

            # Get index of destination farm
            dest_tvd_id = farm_dict[inf_farm_tour[1]]

            # Calculate the number of infected pigs infected sent on the tour
            tran_inf_pigs = round(inf_farm_tour[3] * sim_data[farm_idx, INF] / N, 0)
            print("trans inf pigs", tran_inf_pigs)
            infected_pig_list.append([curr_date, 'd', tran_inf_pigs])

            # Update infected pig count for infected farm and destination farm
            sim_data[farm_idx, INF] = sim_data[farm_idx, INF] - tran_inf_pigs
            sim_data[dest_tvd_id, INF] = sim_data[dest_tvd_id, INF] + tran_inf_pigs

            # Check for indirect contact types
            indirect_contacts = tour_net[(tour_net['event_date'] == curr_date) &
                                         ((tour_net['contact_type'] == 'i') | (tour_net['contact_type'] == 'p') |
                                          (tour_net['contact_type'] == 't')) &
                                         (tour_net['tvd_source'] == inf_farm_tour[0])].to_numpy()

            if len(indirect_contacts) > 0:

                for row in indirect_contacts:

                    # Get index of destination farm
                    dest_contact_tvd = row[1]
                    dest_contact_tvd_id = farm_dict[dest_contact_tvd]

                    if row[4] == 'i':

                        # Number of pigs on the destination farm
                        sum_sus_pigs_i = sim_data[dest_contact_tvd_id, SU]

                        # Calculate the number of pigs indirectly infected
                        ind_inf_pigs = round(tran_inf_pigs / inf_farm_tour[3] * INDIRECT_TRANS_RATE * sum_sus_pigs_i, 0)
                        print("ind inf pigs: ", ind_inf_pigs)
                        infected_pig_list.append([curr_date, 'i', ind_inf_pigs])

                        # Update infected pig count for the indirect destination farm
                        sim_data[dest_contact_tvd_id, INF] = sim_data[dest_contact_tvd_id, INF] + ind_inf_pigs

                    elif row[4] == 'p':

                        # Search for the farms that drop off pigs at the same destination to get total # of
                        # susceptible pigs
                        pig_to_pig = tour_net[(tour_net['event_date'] == curr_date) &
                                              (tour_net['contact_type'] == 'd') &
                                              (tour_net['tvd_dest'] == dest_contact_tvd) &
                                              (tour_net['tvd_source'] != infected_tvd)]

                        print(pig_to_pig)
                        # sum all the susceptible pigs
                        sum_sus_pigs_p = pig_to_pig['n_pigs'].sum()

                        # Calculate the number of pigs infected
                        pig_inf_pigs = round((tran_inf_pigs / inf_farm_tour[3]) * PIG_PIG_TRANS_RATE *
                                             sum_sus_pigs_p, 0)
                        print("p2p: ", pig_inf_pigs)
                        infected_pig_list.append([curr_date, 'p', pig_inf_pigs])

                        # Update infected pig count for the indirect destination farm
                        sim_data[dest_contact_tvd_id, INF] = sim_data[dest_contact_tvd_id, INF] + pig_inf_pigs

                    elif row[4] == 't':

                        # Search for the farms that drop off pigs at the same destination to get total # of
                        # susceptible pigs
                        truck_share = tour_net[(tour_net['event_date'] == curr_date) &
                                               (tour_net['contact_type'] == 'd') &
                                               (tour_net['tvd_dest'] == dest_contact_tvd) &
                                               (tour_net['tvd_source'] != infected_tvd)]

                        # sum all the susceptible pigs
                        sum_sus_pigs_t = truck_share['n_pigs'].sum()

                        # Calculate the number of pigs infected by fomites (uncleaned truck)
                        fom_inf_pigs = round(tran_inf_pigs / inf_farm_tour[3] * FOMITE_TRANS_RATE * sum_sus_pigs_t, 0)
                        print("formites: ", fom_inf_pigs)
                        infected_pig_list.append([curr_date, 't', fom_inf_pigs])
                        # Update infected pig count for the indirect destination farm
                        sim_data[dest_contact_tvd_id, INF] = sim_data[dest_contact_tvd_id, INF] + fom_inf_pigs

        # Geographic Network Spread

        # Find any entries for infected farm in the geographic network
        geo_inf_arr = [row for row in geo_data if row[0] == infected_tvd]

        for row in geo_inf_arr:

            # get the index of the destination farm (returns 0 if the farm is not active during the applicable year(s))
            dest_geo_idx = farm_dict.get(row[1], 0)

            if dest_geo_idx != 0:
                # calculate number of pigs infected thru aerial spread
                geo_inf_pigs = round(sim_data[dest_geo_idx, SU] * sim_data[infected_tvd_id, INF] / N * GEO_TRANS_RATE)

                if geo_inf_pigs > 0:
                    infected_pig_list.append([curr_date, 'g', geo_inf_pigs])
                    # Update infected pig count for the indirect destination farm
                    sim_data[dest_geo_idx, INF] = sim_data[dest_geo_idx, INF] + geo_inf_pigs

    return sim_data, infected_pig_list
