"""Command Line Processing File.

Interprets the arguments from the commandline,
creates instance of TranscriptSampler and
runs the functions from TranscriptSampler class

"""

import argparse
import datetime
import time  # just for checking run time
import numpy as np
import pandas as pd
import csv  # to write dictionary to file
import network_functions as fun

parser = argparse.ArgumentParser(description='Simulate Network Spread')
parser.add_argument('--start_date', type=datetime.date.fromisoformat, help="The Start Date - format YYYY-MM-DD", )
parser.add_argument('--end_date', type=datetime.date.fromisoformat, help="The End Date - format YYYY-MM-DD", )
parser.add_argument('--curr_runs', type=int, help="The current run number")
parser.add_argument('--output_dir', type=str, help='Directory name for output')

def main():
    """Main function.

    Interprets the arguments from the commandline and
    simulates spread of infection within farms and between farms.
    """
    run_start = time.perf_counter()

    args = parser.parse_args()
    start_date = args.start_date
    end_date = args.end_date
    output_file = args.output_file
    num_runs = args.num_runs
    all_runs_infected_farm = []
    all_runs_infected_pig = []
    # column headings for result output
    column_names_1 = ['date', 'farm_idx', 'susceptible', 'exposed', 'infected', 'deceased']
    column_names_2 = ['date', 'contact_type', 'num_inf_pigs']

    # Create farm index dictionary
    farm_dict, farm_list = fun.create_farm_dict(start_date.year, end_date.year)

    for run in range(1, num_runs + 1):
        curr_date = start_date
        infected_farm_list = []
        infected_pig_list = []

        print(f"run: {run}")

        # Generate random index farm
        index_case, inf_tvd = fun.set_index_case(farm_list)

        # Create simulation data array
        sim_data = fun.create_sim_data(index_case, farm_dict, farm_list)

        # Create tour network dataframe for only concerned dates
        tour_net = fun.create_tour_df(start_date, end_date)

        # Create geo network array
        geo_net = fun.create_geo_arr()

        while curr_date <= end_date:
            # Spread infection among pigs in the farm
            sim_data, infected_farm_list = fun.update_spread_within_farms(sim_data, infected_farm_list, curr_date)

            # Spread infection between farms
            sim_data, infected_pig_list = fun.update_spread_between_farms(farm_dict,
                                                                          tour_net,
                                                                          sim_data,
                                                                          curr_date,
                                                                          geo_net,
                                                                          infected_pig_list)

            # move to the next day
            curr_date += datetime.timedelta(days=1)

        # Summarize data for that run
        results_all = pd.DataFrame(infected_farm_list,
                                   columns=['date', 'farm_idx', 'susceptible', 'exposed', 'infected', 'deceased'])

        results_by_compart = results_all.groupby('date', as_index=False).agg({
            'farm_idx': "count",
            'exposed': sum,
            'infected': sum,
            'deceased': sum
        })

        # Add the number of the run
        results_by_compart['run_num'] = run

        # Convert to list and append to master list
        all_runs_infected_farm.append(results_by_compart)

        results_by_contact = pd.DataFrame(infected_pig_list, columns=['date', 'contact_type', 'num_inf_pigs'])

        results_by_contact_grp = results_by_contact.groupby(['date', 'contact_type'], as_index=False).agg({
            'num_inf_pigs': sum})

        # Add the number of the run
        results_by_contact_grp['run_num'] = run

        # Convert to list and append to master list
        all_runs_infected_pig.append(results_by_contact_grp)

    all_runs_infected_farm_np = pd.concat(all_runs_infected_farm).to_numpy()
    all_runs_infected_pig_np = pd.concat(all_runs_infected_pig).to_numpy()
    print(all_runs_infected_farm_np)
    print(all_runs_infected_pig_np)

    # Save data to file
    np.savetxt("output/multiple_runs_farm.csv", all_runs_infected_farm_np, delimiter=", ", fmt='%s,%i,%i,%i,%i,%i')
    np.savetxt("output/multiple_runs_pig.csv", all_runs_infected_pig_np, delimiter=", ", fmt='%s,%s,%i,%i')

    run_end = time.perf_counter()

    print(f"Runtime in {run_end - run_start:0.2f} seconds")


if __name__ == '__main__':
    """Initiates main.
    """
    main()
