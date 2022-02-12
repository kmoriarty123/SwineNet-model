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


# Evidence for Choice of above rates
# BET = contact_rate x transmission_rate
# contact_rate: all pigs interact with all other pigs once a day
# here it is between 0.95 and 1 https://www.frontiersin.org/articles/10.3389/fvets.2019.00248/full
# transmission_rate would be 0.45 to 3.63 per day: https://pubmed.ncbi.nlm.nih.gov/23664069/#:~:text=Different%20criteria%20were%20used%20for,0.45%20to%203.63%20per%20day.
# here it is between 0.6 and 1.5 https://www.frontiersin.org/articles/10.3389/fvets.2019.00248/full
# here it is between https://bvajournals.onlinelibrary.wiley.com/doi/pdf/10.1136/vr.103593
# SIG: time from exposed to acute disease is 4-9 days after exposure. I set to 6.25 days. https://www.nature.com/articles/s41598-020-62736-y
# DEL: After disease, death usually in 10 days.  https://www.efsa.europa.eu/en/topics/topic/african-swine-fever#:~:text=Sudden%20death%20may%20occur.,not%20show%20typical%20clinical%20signs.
# Francesco's article: https://www.authorea.com/doi/full/10.22541/au.164271398.86217172/v1 (table 3)
# danish model: (supplemental tables show parameter values) https://www.frontiersin.org/articles/10.3389/fvets.2018.00049/full#supplementary-material

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
    farm_list = farm_df.values.tolist()

    farm_dict = {}
    for idx, farm_id in enumerate(farm_list):
        farm_dict[farm_id[0]] = idx


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
    with open('../data/tour_network.csv') as f:
        # skip header line
        header = next(f).strip()

        # read in farms that are only active during the start year and end year
        text = "\n".join([line for line in f if
                          start_date <= datetime.date.fromisoformat(line.split(',')[2]) <= end_date])
        tour_df = pd.read_csv(StringIO(text))

        # TODO create numpy array of columns as days and rows farm_idx and true/false for that farm on that day is tour
        # Add the column headings
        tour_df.columns = header.split(',')

        # Convert event_date to datetime object
        tour_df['event_date'] = pd.to_datetime(tour_df['event_date']).dt.date

        # Convert tvds to ints
        tour_df.iloc[:, 0:1] = tour_df.iloc[:, 0:1].values.astype(int)

    # TODO update tour network data with farm index matched on farm_id

    # Return dataframe
    return tour_df


def create_geo_arr():
    """Create geo network array for only farms <2km and without contact_type "g"
    :return: np.array
    """
    # Read data from file
    geo_net_all = pd.read_csv('../data/geo_network.csv')

    # Limit geo net for <2km
    geo_net = geo_net_all[geo_net_all['dist'] <= 2]

    # Remove contact_type_colum and convert to numpy array
    geo_net = geo_net.drop(columns='contact_type').to_numpy()

    # TODO update tour geo data with farm index matched on farm_id

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

    print(f"info re index case: {farm_list[index_farm]}", flush=True)
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
        sim_data[idx, SU] = row[6]

    # update index_case with 1 infected pig
    sim_data[index_case, INF] = 1

    # remove one pig from index_case susceptible
    sim_data[index_case, SU] = sim_data[index_case, SU] - 1

    # Replace all nans with 0.0
    sim_data = np.nan_to_num(sim_data)

    return sim_data


def update_spread_within_farms(
        sim_data: np.array,
        infected_farm_list: list,
        curr_date: datetime,
        infected_pig_list: list) -> np.array:
    for idx in np.arange(0, sim_data.shape[0]):

        # Store information of all entries with at least 1 infected, 1 exposed, or 1 deceased pig
        if sim_data[idx, INF] > 0 or sim_data[idx, EX] > 0 or sim_data[idx, DE] > 0:
            infected_farm_list.append([curr_date, idx, sim_data[idx, SU], sim_data[idx, EX], sim_data[idx, INF],
                                       sim_data[idx, DE]])

            # Select all entries with at least 1 infected or exposed pig
        if sim_data[idx, INF] > 0 or sim_data[idx, EX] > 0:
            new_sus, new_exp, new_inf, new_dec, e_to_i = run_farm_spread(sim_data[idx, SU], sim_data[idx, EX],
                                                                         sim_data[idx, INF], sim_data[idx, DE])
            sim_data[idx, SU] = new_sus
            sim_data[idx, EX] = new_exp
            sim_data[idx, INF] = new_inf
            sim_data[idx, DE] = new_dec
            infected_pig_list.append([curr_date, 'f', e_to_i])

    return sim_data, infected_farm_list


# Define the simulation function
def run_farm_spread(sus, exp, inf, dec):
    # Initial number of infected and recovered individuals, I0 and R0.
    S0, E0, I0, D0 = sus, exp, inf, dec
    # print(S0, E0, I0)

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


def update_spread_between_farms(farm_dict: dict,
                                tour_net: pd.DataFrame,
                                sim_data: np.array,
                                curr_date: datetime,
                                geo_data: np.array,
                                infected_pig_list: list) -> np.array:
    # TODO create parallel list, nupy array, or dict to store infected farms
    # use infected_farm_idx and update along the way rather than search
    infected_farm_idx = np.where(sim_data[:, INF] > 0)[0]

    # Grab tours that are on current_date only direct contact_type
    # TODO split up dataframe for direct transport, p2p,etc.
    curr_tours = tour_net[(tour_net['event_date'] == curr_date) & (tour_net['contact_type'] == "d")].to_numpy()

    # Loop through infected farms
    for farm_idx in infected_farm_idx:

        # TODO Remove these two steps since I will have access to tvd_id from tour_net
        infected_tvd_id = list(farm_dict.values()).index(farm_idx)
        infected_tvd = list(farm_dict.keys())[infected_tvd_id]

        # Total number of pigs in the infected farm
        N = sim_data[farm_idx, SU] + sim_data[farm_idx, EX] + sim_data[farm_idx, INF]

        # Transport Network Spread

        # Check to see if the infected farm has a tour
        # TODO Replace this with look-up in tour_np_array
        if sum(np.isin(curr_tours[:, 0], infected_tvd)):  # sum counts how many booleans

            # Grab row where infected farm transport occurs
            # inf_farm_tour = curr_tours[np.isin(infected_tvd, curr_tours[:, 0])]
            inf_farm_tour = curr_tours[np.where(curr_tours[:, 0] == infected_tvd)[0]][0]
            print(f"Found a tour of an infected farm! {inf_farm_tour}", flush=True)

            # Get index of destination farm
            dest_tvd_id = farm_dict[inf_farm_tour[1]]

            # Calculate the number of infected pigs sent on the tour
            tran_inf_pigs = min(sim_data[farm_idx, INF],
                                np.random.poisson(TAU * inf_farm_tour[3] * sim_data[farm_idx, INF] / N))

            print("trans inf pigs", tran_inf_pigs, flush=True)
            infected_pig_list.append([curr_date, 'd', tran_inf_pigs])

            # Update infected pig count for infected farm and destination farm (ensure it isn't negative)
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
                        ind_inf_pigs = np.random.poisson(
                            TAU * tran_inf_pigs / inf_farm_tour[3] * INDIRECT_TRANS_RATE * sum_sus_pigs_i)
                        print("ind inf pigs: ", ind_inf_pigs, flush=True)
                        infected_pig_list.append([curr_date, 'i', ind_inf_pigs])

                        # Update infected pig count for the indirect destination farm
                        sim_data[dest_contact_tvd_id, INF] = sim_data[dest_contact_tvd_id, INF] + ind_inf_pigs

                    elif row[4] == 'p':
                        # TODO - pull in data from transport regarding source tvd num of pigs on the truck
                        # Search for the farms that drop off pigs at the same destination to get total # of
                        # susceptible pigs
                        pig_to_pig = tour_net[(tour_net['event_date'] == curr_date) &
                                              (tour_net['contact_type'] == 'd') &
                                              (tour_net['tvd_dest'] == dest_contact_tvd) &
                                              (tour_net['tvd_source'] != infected_tvd)]

                        # print(pig_to_pig, flush=True)
                        # sum all the susceptible pigs
                        sum_sus_pigs_p = pig_to_pig['n_pigs'].sum()

                        # Calculate the number of pigs infected
                        pig_inf_pigs = np.random.poisson(TAU * (tran_inf_pigs / inf_farm_tour[3]) * PIG_PIG_TRANS_RATE *
                                                         sum_sus_pigs_p)
                        print("p2p: ", pig_inf_pigs, flush=True)
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
                        fom_inf_pigs = np.random.poisson(
                            TAU * tran_inf_pigs / inf_farm_tour[3] * FOMITE_TRANS_RATE * sum_sus_pigs_t)
                        print("formites: ", fom_inf_pigs, flush=True)
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
                geo_inf_pigs = np.random.poisson(
                    TAU * sim_data[dest_geo_idx, SU] * sim_data[farm_idx, INF] / N * GEO_TRANS_RATE)
                # print("geo: ", geo_inf_pigs, flush=True)
                if geo_inf_pigs > 0:
                    infected_pig_list.append([curr_date, 'g', geo_inf_pigs])
                    # Update infected pig count for the indirect destination farm
                    sim_data[dest_geo_idx, INF] = sim_data[dest_geo_idx, INF] + geo_inf_pigs

    return sim_data, infected_pig_list
