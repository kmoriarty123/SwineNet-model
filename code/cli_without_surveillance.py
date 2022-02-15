"""Command Line Processing File.

Interprets the arguments from the commandline,
spreads disease on farms and between farms.
"""

import argparse
import datetime
import os
import random
import numpy as np
import pandas as pd

parser = argparse.ArgumentParser(description='Simulate Network Spread')
# parser.add_argument('--output_dir', type=argparse.FileType('w'), help="File for output")
parser.add_argument('--start_date', type=datetime.date.fromisoformat, help="The Start Date - format YYYY-MM-DD", )
parser.add_argument('--end_date', type=datetime.date.fromisoformat, help="The End Date - format YYYY-MM-DD", )
parser.add_argument('--curr_run', type=int, help="The current run number")
parser.add_argument('--stochastic', action='store_true', help='Include to run stochastic methods.')
parser.add_argument('--not_stochastic', action='store_true', help='Include to run more deterministic methods.')
parser.add_argument('--seed', type=int, help="Seed for the current run")


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

    # Set seed for the current run
    random.seed(seed)

    # initialize lists
    infected_farm_list = []
    infected_pig_list = []

    # Set current date
    curr_date = start_date

    print(f"run: {curr_run}", flush=True)

    # Run stochastic functions if passed as parameter
    if stochastic:
        import network_functions_stochastic as fun
    elif deterministic:
        import network_functions as fun

    # Create farm index dictionary
    farm_dict, farm_list = fun.create_farm_dict(start_date.year, end_date.year)

    # Generate random index farm
    index_farm_idx, index_farm_tvd = fun.set_index_case(farm_list, curr_run, output_dir)

    # Create simulation data array
    sim_data = fun.create_sim_data(index_farm_idx, farm_list)

    # Create tour network dataframe for only concerned dates
    tour_arr, direct_trans_df, other_trans_df = fun.create_tours(start_date, end_date, farm_dict)

    # Create geo network array
    geo_net = fun.create_geo_arr(farm_dict)
    day_count = 0  # To keep track of number of days passed (for tour_array column index)

    while curr_date <= end_date:
        # Spread infection among pigs in the farm
        sim_data, infected_farm_list = fun.update_spread_within_farms(sim_data,
                                                                      infected_farm_list,
                                                                      curr_date,
                                                                      infected_pig_list)

        # Spread infection between farms
        sim_data, infected_pig_list = fun.update_spread_between_farms(farm_dict,
                                                                      tour_arr,
                                                                      direct_trans_df,
                                                                      other_trans_df,
                                                                      sim_data,
                                                                      curr_date,
                                                                      day_count,
                                                                      geo_net,
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

    # Convert to list and append to master list
    # all_runs_infected_pig.append(results_by_contact_grp)

    # Save data to file
    np.savetxt(output_dir + "results_by_contact_grp_" + str(curr_run) + ".csv",
               results_by_contact_grp, delimiter=", ", fmt='%s,%s,%i,%i')
    np.savetxt(output_dir + "results_by_compart_" + str(curr_run) + ".csv",
               results_by_compart, delimiter=", ", fmt='%s,%i,%i,%i,%i,%i')

    end = datetime.datetime.now()
    print("Run time: ", str(end - start)[5:])


if __name__ == '__main__':
    """Initiates main.
    """
    main()
