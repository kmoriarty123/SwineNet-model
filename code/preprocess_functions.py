""" SwineNet Network Simulation Model.

Preprocess data

"""
import pickle
from io import StringIO

import numpy as np
import pandas as pd

# Indices from simulated_data matrix
SU, EX, INF, DE = 0, 1, 2, 3

# Indices for farm_list
TVD, NPIGS = 1, 6

# Indices for tour
SRC, DEST, DATE, T_NPIGS, CNTCT = 0, 1, 2, 3, 4
column_names_direct = ['source_idx', 'dest_idx', 'event_date', 'n_pigs']
column_names_tour = ['source_idx', 'dest_idx', 'event_date', 'n_pigs', 'contact_type']

# Indices for geo
G_SRC, G_DEST, DIST = 0, 1, 2
column_names_geo = ['source_idx', 'dest_idx', 'dist']

# Years of data
beg_yr = 2014
end_yr = 2020 #only until 2019 for AGIS data & Tour data

def create_farm_dict():
    """ Initiates the farm matrix.

    """

    # From file, import farms from agis_data and create dict
    farm_df = pd.read_csv('../data/agis_data_lim.csv', encoding='latin-1')

    # replace all na for n_pigs with zeros
    farm_df['tot_pigs'] = farm_df['tot_pigs'].fillna(0)

    tmp_farm_dict = {}
    #rev_tmp_farm_dict = {}

    # create separate farm_dict and farm_list for each year
    for yr in range(beg_yr, end_yr):
        # subset for only the year
        tmp_farm_df = farm_df[farm_df['year'] == yr]
        # reset index of the df
        tmp_farm_df.reset_index(drop=True)
        # create list
        tmp_farm_list = tmp_farm_df.values.tolist()

        # Store farm data as dictionary with tvd as key and idx as value
        # REMOVED - And another dictionary with idx as key and tvd as value
        # TODO make sure index here is reset and not taking on old indices
        for idx, farm_info in enumerate(tmp_farm_list):
            tmp_farm_dict[farm_info[TVD]] = idx
            #rev_tmp_farm_dict[idx] = farm_info[TVD]

        # Save farm_dict to file
        tmp_farm_dict_file = open("../data/farm_dict_" + str(yr) + ".pkl", "wb")
        pickle.dump(tmp_farm_dict, tmp_farm_dict_file)
        tmp_farm_dict_file.close()

        #rev_tmp_farm_dict_file = open("../data/rev_farm_dict_" + str(yr) + ".pkl", "wb")
        #pickle.dump(rev_tmp_farm_dict, rev_tmp_farm_dict_file)
        #rev_tmp_farm_dict_file.close()

        # Save farm_list to file
        with open('../data/farm_list_'+ str(yr) + '.pkl', 'wb') as pickle_file:
            pickle.dump(tmp_farm_list, pickle_file, protocol=pickle.HIGHEST_PROTOCOL)

    return

# TODO Incorporate this functionality into previous function to speed up preprocess
def create_sim_data():

    # Create different sim_data from each year
    for yr in range(beg_yr, end_yr):

        # Load farm_list from file
        with open('../data/farm_list_' + str(yr) + '.pkl', 'rb') as pickle_load:
            tmp_farm_list = pickle.load(pickle_load)

        # initialize num_farms x 4 integer array (columns: susceptible, exposed, infected, deceased, isolated)
        tmp_sim_data = np.zeros((len(tmp_farm_list), 5), dtype=int)

        # update susceptible values with num of pigs for each farm
        for idx, row in enumerate(tmp_farm_list):
            tmp_sim_data[idx, SU] = row[NPIGS]

        # Replace all nans with 0.0
        tmp_sim_data = np.nan_to_num(tmp_sim_data)

        # Save sim_data to file
        np.save('../data/sim_data_' + str(yr) + '.npy', tmp_sim_data)


def create_tours():
    """ Creates the direct transport tour data frame, the other contact tour dataframe and the tour array.

    Dataframe is saved with farm indices and not farm tvds
    tour_arr is a binary 2-d array which is 1 for farm_idx that has a direct transport on that day.
    """

    # From file, import farms from agis_data and create dict
    with open('../data/tour_network.csv') as f:
        # skip header line
        header = next(f).strip()

        # read in farms that are only active during the start year and end year
        text = "\n".join(line for line in f)
        tour_df = pd.read_csv(StringIO(text))

    # Add the column headings
    tour_df.columns = header.split(',')

    # Convert event_date to datetime object
    tour_df['event_date'] = pd.to_datetime(tour_df['event_date']).dt.date

    # Convert tvds and tot_pigs to ints
    tour_df.iloc[:, [SRC, DEST,T_NPIGS]] = tour_df.iloc[:, [SRC, DEST,T_NPIGS]].values.astype(int)

    # Create tour_df for each year
    for yr in range(beg_yr, end_yr):

        # Load preprocessed farm dictionary from file
        tmp_farm_dict_file = open("../data/farm_dict_" + str(yr) + ".pkl", "rb")
        tmp_farm_dict = pickle.load(tmp_farm_dict_file)
        tmp_farm_dict_file.close()

        tmp_tour_df = tour_df.copy()

        # Add idx based on tvds
        tmp_tour_df['source_idx'] = tmp_tour_df['tvd_source'].map(tmp_farm_dict)
        tmp_tour_df['dest_idx'] = tmp_tour_df['tvd_dest'].map(tmp_farm_dict)

        # Convert indices to ints
        tmp_tour_df.loc[:, ['source_idx', 'dest_idx']] = \
            tmp_tour_df.loc[:, ['source_idx', 'dest_idx']].values.astype(int)

        # Drop tvd id columns
        tmp_tour_df = tmp_tour_df.drop(['tvd_source', 'tvd_dest'], axis=1)

        # Separate direct transports from other tour contacts
        direct_transport_df = tmp_tour_df[tmp_tour_df['contact_type'] == 'd']
        other_transport_df = tmp_tour_df[tmp_tour_df['contact_type'] != 'd']

        # Drop contact_type column from direct transport
        direct_transport_df = direct_transport_df.drop(['contact_type'], axis=1)

        # Reindex columns for df
        direct_transport_df = direct_transport_df.reindex(columns=column_names_direct)
        other_transport_df = other_transport_df.reindex(columns=column_names_tour)

        # Sort direct transport dataframe by event_date
        direct_transport_df = direct_transport_df.sort_values(by='event_date')

        # create new inspection_ind for transports
        direct_transport_df['inspection_ind'] = 0

        # Save direct_transport_df and other_transport_df to file
        direct_transport_df.to_pickle("../data/direct_trans_" + str(yr) + ".pkl")
        other_transport_df.to_pickle("../data/other_trans_" + str(yr) + ".pkl")

def create_geo_arr():
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

    for yr in range(beg_yr, end_yr):

        # Load preprocessed farm dictionary from file
        tmp_farm_dict_file = open("../data/farm_dict_" + str(yr) + ".pkl", "rb")
        tmp_farm_dict = pickle.load(tmp_farm_dict_file)
        tmp_farm_dict_file.close()

        # Make a copy of as to avoid SettingWithCopyWarning: A value is trying to be set on a copy of a slice from DF...
        tmp_geo_net = geo_net.copy()

        # Map the tvd_id with the farm_idx
        #tmp_geo_net.loc[:, 'source_idx'] = tmp_geo_net.loc[:, 'tvd_source'].map(tmp_farm_dict)
        #tmp_geo_net.loc[:, 'dest_idx'] = tmp_geo_net.loc[:, 'tvd_dest'].map(tmp_farm_dict)
        tmp_geo_net['source_idx'] = tmp_geo_net['tvd_source'].map(tmp_farm_dict)
        tmp_geo_net['dest_idx'] = tmp_geo_net['tvd_dest'].map(tmp_farm_dict)

        # Drop any values that weren't matched as not in active agis database
        tmp_geo_net.dropna(subset=['source_idx', 'dest_idx'], inplace=True, axis=0)

        # Remove contact_type_column, tvd_source, and tvd_dest
        tmp_geo_net = tmp_geo_net.drop(['tvd_source', 'tvd_dest', 'contact_type'], axis=1)

        # Reindex columns
        tmp_geo_net = tmp_geo_net.reindex(columns=column_names_geo)

        # Convert idx to int (not sure why they are floats)
        tmp_geo_net['source_idx'] = tmp_geo_net['source_idx'].astype(int)
        tmp_geo_net['dest_idx'] = tmp_geo_net['dest_idx'].astype(int)

         # Convert to numpy array
        tmp_geo_net = tmp_geo_net.to_numpy().astype(int)

        # Save geo_arr to file
        np.save('../data/geo_arr_' + str(yr) + '.npy', tmp_geo_net)
