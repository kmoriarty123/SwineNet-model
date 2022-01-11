""" SwineNet Network Simulation Model.

Simple network simulation model
"""
import datetime
from io import StringIO
from random import choices
import numpy as np
import pandas
import pandas as pd


def create_farm_dict(
        start_year: int,
        end_year: int
) -> dict:
    """ Initiates the farm matrix.

    Only active farms between start_date and end_date.
    """
    # Don't need start_date: datetime, end_date: datetime parameters since we take all farms (geographic)

    # From file, import farms from agis_data and create dict
    with open('data/agis_data_lim.csv') as f:
        # print("s{}s".format(start_year))

        # skip header line
        next(f)

        # read in farms that are only active during the start year and end year
        # TODO: also grab any farm between the start and end years
        text = "\n".join([line for line in f if
                          int(line.split(',')[1]) == start_year or
                          int(line.split(',')[1]) == end_year])
        farm_df = pd.read_csv(StringIO(text))

        # Concat the header and text and reset the Index.
        # farm_dict = pd.concat([header, farm_dict]).reset_index(drop=True)

    farm_df['index'] = farm_df.reset_index().index

    # Convert df to dict with row index as key and other variables as list
    farm_dict = farm_df.T.to_dict('list')

    # Create farm_key dictionary
    farm_key_df = farm_df[farm_df.columns[0:1]].T.to_dict('index')

    #Invert the values so now tvd_nr are the keys and index is the value
    farm_key = {int(val): key for key, val in farm_key_df.items()}

    # Return Dictionary
    return farm_dict, farm_key


def create_tour_df(
        start_date: datetime,
        end_date: datetime
) -> pandas.DataFrame:
    """ Creates the tour data frame.

    Only tours between start_date and end_date.
    """

    # From file, import farms from agis_data and create dict
    with open('data/tour_network.csv') as f:
        print("s{}s".format(start_date))

        # skip header line
        header = next(f).strip()

        # read in farms that are only active during the start year and end year
        # TODO: also grab any farm between the start and end years
        text = "\n".join([line for line in f if
                          start_date <= datetime.date.fromisoformat(line.split(',')[2]) <= end_date])
        tour_df = pd.read_csv(StringIO(text))

        # Add the column headings
        tour_df.columns = header.split(',')

        # Convert event_date to datetime object
        tour_df['event_date'] = pd.to_datetime(tour_df['event_date']).dt.date

        print(tour_df)

    # Return dataframe
    return tour_df


def set_index_case(
        farm_dict: dict) -> int:
    """ Pick 1 pig on random farm to be infected with ASF

    :return: Index of farm index
    """
    # TODO: calculate different probabilities for different farms based on "fencing" and "closeness" to wild boar
    # can add to function choices the parameter weights (i.e., weights = [10, 1, 1]) to achieve this

    farm_indices = []

    # Exclude all holdings that have 0 total pigs (slaughterhouses, medical center, etc.)
    for n in range(0, len(farm_dict) - 1):
        if list(farm_dict.values())[n][6] > 0:
            farm_indices.append(n)

    # Set seed to reproduce results
    np.random.seed(31415)

    # Pick one random index from 0 to 1 less than total farms
    index_farm = choices(farm_indices, k=1)[0]  # returns a list so need the first element

    return index_farm


def create_sim_data(
        index_case: int,
        farm_dict: dict) -> np.array:
    # initialize num_farms x 3 integer array (columns: susceptible, exposed, infected, time)
    sim_data = np.zeros((len(farm_dict), 4))

    # update susceptible values with num of pigs for each farm
    # TODO change to python style for loop
    for n in range(0, len(farm_dict) - 1):
        sim_data[n, 0] = list(farm_dict.values())[n][6]

    # update index_case with 1 infected pig
    sim_data[index_case, 2] = 1

    # remove one pig from index_case susceptible
    sim_data[index_case, 0] = sim_data[index_case, 0] - 1
    print("index farm: {}".format(sim_data[index_case, :]))
    return sim_data


def update_spread_within_farms(
        sim_data: np.array) -> np.array:
    i = 0
    # Select all entries with at least 1 infected pig
    for sus, exp, inf, time in sim_data:

        if inf > 0:
            new_sus, new_exp, new_inf = run_farm_spread(sus, exp, inf)
            sim_data[i, 0] = new_sus
            sim_data[i, 1] = new_exp
            sim_data[i, 2] = new_inf
        i += 1

    return sim_data


# Define the simulation function
def run_farm_spread(sus, exp, inf):
    # Initial number of infected and recovered individuals, I0 and R0.
    S0, E0, I0 = sus, exp, inf
    print(S0, E0, I0)

    # Total pig population on the farm, N.
    N = S0 + E0 + I0

    # Contact transmission rate: beta,
    # Exposed to infected rate: sigma
    # Disease causing death rate: delta
    beta, sigma, delta = 0.2, 0.4, 0.1

    S = S0 - beta * S0 * I0 / N
    E = E0 + beta * S0 * I0 / N - sigma * E0
    I = I0 + sigma * E0 - delta * I0

    return S, E, I


def update_spread_between_farms(farm_dict: dict,
                                tour_net: pd.DataFrame,
                                disease_array: np.array,
                                curr_date: datetime) -> np.array:

    # Grab tours that are on current_date only direct contact_type
    curr_tours = tour_net[(tour_net['event_date'] == curr_date) & (tour_net['contact_type'] == "d")].to_numpy()

    if len(curr_tours) > 0:
        print("found one at date: {}".format(curr_date))
        print(curr_tours)
        # For each row in tour_net_lim, move pigs from tvd_source to tvd_dest
        for tour in curr_tours:
            print(tour[0])
            # Select tvd_source and find its index in the farm_dict
            print("index: ", farm_dict[tour[0]])
            #idx_source = list(farm_dict.values()).index[0](tour[0])
            #idx_dest = list(farm_dict.values()).index[0](tour[1])
            #print(f"tvd_source {tour[0]} and idx_source {idx_source}")
            #disease_array[idx_source, 0] = disease_array[idx_source, 0]- tour[3]
            #disease_array[idx_dest, 0] = disease_array[idx_dest, 0] + tour[3]

    return disease_array
