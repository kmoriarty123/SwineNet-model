"""Command Line Processing File.

Interprets the arguments from the commandline,
spreads disease on farms and between farms.

"""

import argparse
import datetime
import os
import pickle
import random

import numpy as np
import pandas as pd

import surveillance_functions as surv

parser = argparse.ArgumentParser(description='Simulate Network Spread')
# parser.add_argument('--output_dir', type=argparse.FileType('w'), help="File for output")
parser.add_argument('--start_date', type=datetime.date.fromisoformat, help="The Start Date - format YYYY-MM-DD", )
parser.add_argument('--end_date', type=datetime.date.fromisoformat, help="The End Date - format YYYY-MM-DD", )
parser.add_argument('--curr_run', type=int, help="The current run number")
parser.add_argument('--stochastic', action='store_true', help='Include to run stochastic methods.')
parser.add_argument('--not_stochastic', action='store_true', help='Include to run more deterministic methods.')
parser.add_argument('--seed', type=int, help="Seed for the current run")
parser.add_argument('--surveillance', type=str, help="Surveillance Program(s). Options: none, slaughter, farm, all")


def main():
    """Main function.

    Interprets the arguments from the commandline and
    simulates spread of infection within farms and between farms.
    """
    # To determine runtime
    start = datetime.datetime.now()

    # Read arguments
    args = parser.parse_args()
    start_date = args.start_date
    end_date = args.end_date
    curr_run = args.curr_run
    output_dir = "../output/stochastic/" + str(start_date.year) + "_" + str(start_date.month) + "_" + str(
        start_date.day) + "/"
    stochastic = args.stochastic
    deterministic = args.not_stochastic
    seed = args.seed
    surveillance_type = args.surveillance

    # Set seed for the current run
    random.seed(seed)

    # initialize lists
    infected_farm_list = []
    infected_pig_list = []
    inspected_tours_list = []

    # Set current date
    curr_date = start_date

    print(f"run: {curr_run}", flush=True)

    # Run stochastic functions if passed as parameter
    if stochastic:
        import network_functions_stochastic as fun
    elif deterministic:
        import network_functions as fun

    # Load preprocessed farm dictionary from file
    farm_dict_file = open("../data/farm_dict_" + str(start_date.year) + ".pkl", "rb")
    farm_dict = pickle.load(farm_dict_file)
    farm_dict_file.close()

    # Load preprocessed farm list from file
    with open('../data/farm_list_' + str(start_date.year) + '.pkl', 'rb') as pickle_load:
        farm_list = pickle.load(pickle_load)

    # Load preprocessed simulation data array from file
    sim_data = np.load('../data/sim_data_' + str(start_date.year) + '.npy')

    # Load preprocessed geo network from file
    geo_arr = np.load('../data/geo_arr_' + str(start_date.year) + '.npy')

    # Load the preprocessed direct and other transport dfs from file
    direct_trans_df = pd.read_pickle("../data/direct_trans_" + str(start_date.year) + ".pkl")
    other_trans_df = pd.read_pickle("../data/other_trans_" + str(start_date.year) + ".pkl")

    # Generate random index farm
    index_farm_idx, index_farm_tvd = fun.set_index_case(farm_list,
                                                        curr_run,
                                                        output_dir)

    # Update sim data with index case information
    sim_data = fun.update_sim_data(index_farm_idx,
                                   sim_data)

    # Create tour network dataframe for only concerned dates
    tour_arr, direct_trans_df = fun.create_tour_arr(start_date,
                                end_date,
                                farm_dict,
                                direct_trans_df)

    day_count = 0  # To keep track of number of days passed (for tour_array column index)

    # Add surveillance programs if passed
    if surveillance_type == 'slaughter':

        # Create list of slaughter houses that are randomly selected for surveillance
        slaughter_indices = surv.create_slaughterhouse_list(farm_list, curr_run, output_dir)

        direct_trans_df = surv.find_transports_to_slaughter(slaughter_indices, direct_trans_df)

        while curr_date <= end_date:
            # Spread infection among pigs in the farm
            sim_data, infected_farm_list = fun.update_spread_within_farms(sim_data,
                                                                          infected_farm_list,
                                                                          curr_date,
                                                                          infected_pig_list)
            # Spread infection between farms
            sim_data, infected_pig_list, inspected_tours_list = surv.update_spread_between_farms_surv(tour_arr,
                                                                                direct_trans_df,
                                                                                other_trans_df,
                                                                                sim_data,
                                                                                curr_date,
                                                                                day_count,
                                                                                geo_arr,
                                                                                infected_pig_list,
                                                                                inspected_tours_list)
            # move to the next day
            curr_date += datetime.timedelta(days=1)
            day_count = day_count + 1

    else:
        while curr_date <= end_date:
            # Spread infection among pigs in the farm
            sim_data, infected_farm_list = fun.update_spread_within_farms(sim_data,
                                                                      infected_farm_list,
                                                                      curr_date,
                                                                      infected_pig_list)

            # Spread infection between farms
            sim_data, infected_pig_list = fun.update_spread_between_farms(tour_arr,
                                                                      direct_trans_df,
                                                                      other_trans_df,
                                                                      sim_data,
                                                                      curr_date,
                                                                      day_count,
                                                                      geo_arr,
                                                                      infected_pig_list)

            # move to the next day
            curr_date += datetime.timedelta(days=1)
            day_count = day_count + 1

    # Summarize data for that run
    results_all = pd.DataFrame(infected_farm_list,
                               columns=['date', 'farm_idx', 'susceptible', 'exposed', 'infected', 'deceased'])

    results_by_compart = results_all.groupby('date', as_index=False).agg({
        'farm_idx': "count",
        'exposed': sum,
        'infected': sum,
        'deceased': sum
    })

    # Add the number of the curr run
    results_by_compart['run_num'] = curr_run

    # Create df and group
    results_by_contact = pd.DataFrame(infected_pig_list, columns=['date', 'contact_type', 'num_inf_pigs'])
    results_by_contact_grp = results_by_contact.groupby(['date', 'contact_type'], as_index=False).agg({
        'num_inf_pigs': sum})

    # Add the number of the curr run
    results_by_contact_grp['run_num'] = curr_run

    # Transports that were inspected
    inspected_tours_df = pd.DataFrame(inspected_tours_list,
                               columns=['source_idx', 'dest_idx', 'event_date', 'n_pigs', 'inspect_ind'])
    # Add the number of the curr run
    inspected_tours_df['run_num'] = curr_run

    # Save data to file
    np.savetxt(output_dir + "results_by_contact_grp_" + str(curr_run) + ".csv",
               results_by_contact_grp, delimiter=", ", fmt='%s,%s,%i,%i')
    np.savetxt(output_dir + "results_by_compart_" + str(curr_run) + ".csv",
               results_by_compart, delimiter=", ", fmt='%s,%i,%i,%i,%i,%i')
    np.savetxt(output_dir + "results_inspected_trans_" + str(curr_run) + ".csv",
               inspected_tours_df, delimiter=", ", fmt='%i,%i,%s,%i,%i,%i')

    end = datetime.datetime.now()
    print("Run time: ", str(end - start)[5:])


if __name__ == '__main__':
    """Initiates main.
    """
    main()
