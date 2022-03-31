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
import network_functions as fun

parser = argparse.ArgumentParser(description='Simulate Network Spread')
# parser.add_argument('--output_dir', type=argparse.FileType('w'), help="File for output")
parser.add_argument('--start_date', type=datetime.date.fromisoformat, help="The Start Date - format YYYY-MM-DD", )
parser.add_argument('--end_date', type=datetime.date.fromisoformat, help="The End Date - format YYYY-MM-DD", )
parser.add_argument('--curr_run', type=int, help="The current run number")
# parser.add_argument('--stochastic', action='store_true', help='Include to run stochastic methods.')
# parser.add_argument('--not_stochastic', action='store_true', help='Include to run more deterministic methods.')
parser.add_argument('--seed', type=int, help="Seed for the current run")
parser.add_argument('--surveillance', type=str, default='no',
                    help="Surveillance Program(s). Options: no, slaughter, farmer, network")
parser.add_argument('--mort_rate_inc', type=float, default=0.10,
                    help="Mortality rate increase for farmer-based surveillance")
parser.add_argument('--test_date_int', type=int, default=90,
                    help="Number of days between testing at farms with specific network metrics")
parser.add_argument('--test_contact_net', nargs="*", type=str, default=['d'],
                    help="Contact Network types as list for testing farms")
parser.add_argument('--test_top_thresh', type=int, default=250,
                    help="Top number of farms with a certain network metric")


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
    seed = args.seed

    # Surveillance specific parameters
    surveillance_type = args.surveillance
    mortality_rate_inc = args.mort_rate_inc
    testing_date_interval = args.test_date_int
    testing_contact_network_list = args.test_contact_net
    test_top_thresh = args.test_top_thresh

    if surveillance_type == 'network':
        output_dir = "../output/" + str(start_date.year) + "_" + str(start_date.month) + "_" + str(
            start_date.day) + "/" + surveillance_type + "_surv" + "/" + "nets_" +  str(test_top_thresh) + "_" + \
                     str(testing_date_interval) + "_" + "_".join(testing_contact_network_list) + "/"
    elif surveillance_type == 'farmer':
        output_dir = "../output/" + str(start_date.year) + "_" + str(start_date.month) + "_" + str(
            start_date.day) + "/" + surveillance_type + "_surv" + "/" + "mort_rate_inc_" + str(mortality_rate_inc) + "/"
    else:
        output_dir = "../output/" + str(start_date.year) + "_" + str(start_date.month) + "_" + str(
            start_date.day) + "/" + surveillance_type + "_surv" + "/"

    # Set seed for the current run
    random.seed(seed)
    np.random.seed(seed)

    # initialize lists
    infected_farm_list = []
    infected_pig_list = []
    inspected_tours_list = []  # to store info regarding tours that were inspected and found infected pigs
    inspected_farm_list = []  # to store info regarding farms that were inspected and found infected pigs

    # Set current date
    curr_date = start_date

    print(f"run: {curr_run}", flush=True)

    # Run stochastic functions if passed as parameter
    # if stochastic:
    #    import network_functions_stochastic as fun
    # elif deterministic:
    #    import network_functions as fun

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
            print(f"curr_date: {curr_date}", flush=True)

            # Spread infection among pigs in the farm
            sim_data, infected_farm_list, infected_pig_list = fun.update_spread_within_farms(sim_data,
                                                                                             infected_farm_list,
                                                                                             curr_date,
                                                                                             infected_pig_list)
            # Spread infection between farms
            sim_data, infected_pig_list, inspected_tours_list = \
                surv.update_spread_between_farms_surv(tour_arr,
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

    elif surveillance_type == 'farmer':

        while curr_date <= end_date:
            print(f"curr_date: {curr_date}", flush=True)

            # Spread infection among pigs in the farm
            sim_data, infected_farm_list, infected_pig_list, inspected_farm_list = surv.update_spread_within_farms_surv(
                sim_data,
                infected_farm_list,
                curr_date,
                infected_pig_list,
                mortality_rate_inc,
                inspected_farm_list)

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

    elif surveillance_type == 'network':

        # pick testing dates for farms that have specific network metrics
        test_dates_list = surv.pick_test_dates(testing_date_interval,
                                               start_date,
                                               end_date)
        # create testing_farm_list
        testing_farm_idx = surv.create_test_farm_list(farm_dict,
                                                      testing_contact_network_list,
                                                      test_top_thresh)

        while curr_date <= end_date:
            print(f"curr_date: {curr_date}", flush=True)

            # Spread infection among pigs in the farm
            sim_data, infected_farm_list, infected_pig_list = fun.update_spread_within_farms(sim_data,
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

            if curr_date in test_dates_list:
                print("TESTING DAY!: ", curr_date)
                sim_data, inspected_farm_list = surv.network_surv_test_farm(testing_farm_idx,
                                                                            sim_data,
                                                                            inspected_farm_list,
                                                                            curr_date)

            # move to the next day
            curr_date += datetime.timedelta(days=1)
            day_count = day_count + 1

    elif surveillance_type == 'no':
        while curr_date <= end_date:
            print(f"curr_date: {curr_date}", flush=True)

            # Spread infection among pigs in the farm
            sim_data, infected_farm_list, infected_pig_list = fun.update_spread_within_farms(sim_data,
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
                               columns=['date', 'farm_idx', 'susceptible', 'exposed', 'infected', 'deceased',
                                        'isolated'])

    results_by_compart = results_all.groupby('date', as_index=False).agg({
        'farm_idx': "count",
        'exposed': sum,
        'infected': sum,
        'deceased': sum,
        'isolated': sum
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
    if surveillance_type == 'slaughter':
        inspected_tours_df = pd.DataFrame(inspected_tours_list,
                                          columns=['source_idx', 'dest_idx', 'event_date', 'n_pigs', 'inspect_ind',
                                                   'n_discover'])
        # Add the number of the curr run
        inspected_tours_df['run_num'] = curr_run

        # Save data to file
        np.savetxt(output_dir + "results_inspected_trans_" + str(curr_run) + ".csv",
                   inspected_tours_df,
                   delimiter=", ", fmt='%i,%i,%s,%i,%i,%i,%i')

    elif surveillance_type == 'farmer':
        inspected_farms_df = pd.DataFrame(inspected_farm_list,
                                          columns=['farm_idx', 'curr_date', 'n_detect'])
        # Add the number of the curr run
        inspected_farms_df['run_num'] = curr_run

        # Save data to file
        np.savetxt(output_dir + "results_inspected_farms_" + str(curr_run) + ".csv",
                   inspected_farms_df,
                   delimiter=", ", fmt='%i,%s,%i,%i')

    elif surveillance_type == 'network':
        inspected_farms_df = pd.DataFrame(inspected_farm_list,
                                          columns=['farm_idx', 'curr_date', 'surv_contact_net_type', 'n_detect'])
        # Add the number of the curr run
        inspected_farms_df['run_num'] = curr_run

        # Save data to file
        np.savetxt(output_dir + "results_inspected_farms_network_" +
                   str(curr_run) + ".csv",
                   inspected_farms_df,
                   delimiter=", ", fmt='%i,%s,%s,%i,%i')

    # Save data to file
    np.savetxt(output_dir + "results_by_contact_grp_" + str(curr_run) + ".csv",
               results_by_contact_grp,
               delimiter=", ", fmt='%s,%s,%i,%i')
    np.savetxt(output_dir + "results_by_compart_" + str(curr_run) + ".csv",
               results_by_compart,
               delimiter=", ", fmt='%s,%i,%i,%i,%i,%i,%i')

    end = datetime.datetime.now()
    print("Run time: ", (end - start).total_seconds())


if __name__ == '__main__':
    """Initiates main.
    """
    main()
