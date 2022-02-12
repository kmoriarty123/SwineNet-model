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


def create_slaughterhouse_surv_list(
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
    slaughter_indicies_list = choices(slaughter_all_indices, k=9)

    print(f"info re index case: {farm_list[slaughter_indicies_list[0]]} {farm_list[slaughter_indicies_list[1]]}", flush=True)
    #slaughter_tvd_list = map(farm_list.__getitem__, slaughter_indicies_list][0]

    # Save the info re index case to file
    slaughters_to_save = map(farm_list.__getitem__, slaughter_indicies_list)
    #farm_to_save.append(curr_run)  # include curr_run
    #farm_to_save = ", ".join(map(str, farm_to_save))  # save as string (need to convert ints to string first)
    with open(output_dir + "slaughters_chosen_" + str(curr_run) + ".csv", 'w') as outputf:
        #f.write(f'{item}\n')
        #f.write(farm_to_save + "\n")
        outputf.write('\n'.join(slaughters_to_save))

    return slaughter_indicies_list