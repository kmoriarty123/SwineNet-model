"""Command Line Processing File.

Interprets the arguments from the commandline,
spreads disease on farms and between farms.
"""

import argparse
import datetime
import os
import numpy as np
import pandas as pd

parser = argparse.ArgumentParser(description='Simulate Network Spread')
parser.add_argument('--start_date', type=datetime.date.fromisoformat, help="The Start Date - format YYYY-MM-DD", )
parser.add_argument('--end_date', type=datetime.date.fromisoformat, help="The End Date - format YYYY-MM-DD", )
parser.add_argument('--curr_run', type=int, help="The current run number")
parser.add_argument('--stochastic', action='store_true', help='Include to run stochastic methods.')
parser.add_argument('--not_stochastic', action='store_true', help='Include to run more deterministic methods.')
parser.add_argument('--index_case_tvd_id', type=int, help="The TVD ID of the index case", )

def main():
    """Main function.

    Interprets the arguments from the commandline and
    simulates spread of infection within farms and between farms.
    """

    args = parser.parse_args()
    start_date = args.start_date
    end_date = args.end_date
    curr_run = args.curr_run
    output_dir = "../output/stochastic/" + str(start_date.year) + "_" + str(start_date.month) + "_" + str(start_date.day) + "/"
    stochastic = args.stochastic
    deterministic = args.not_stochastic
    index_case_tvd = args.index_case_tvd_id

    if stochastic:
        import network_functions_stochastic as fun
    elif deterministic:
        import network_functions as fun

    # Create farm index dictionary
    farm_dict, farm_list = fun.create_farm_dict(start_date.year, end_date.year)

    curr_date = start_date
    infected_farm_list = []
    infected_pig_list = []

    print(f"run: {curr_run}", flush=True)

    # Set index case and find the matching dictionary index for provided index case
    inf_tvd = index_case_tvd
    index_case = farm_dict[inf_tvd]

    # Save the info re index case to file
    farm_to_save = farm_list[index_case]
    farm_to_save.append(curr_run) # include curr_run
    farm_to_save = ", ".join(map(str, farm_to_save)) # save as string (need to convert ints to string first)
    with open(output_dir + "index_case_" + str(curr_run) + ".csv", 'w') as f:
        f.write(farm_to_save)

    # Create simulation data array
    sim_data = fun.create_sim_data(index_case, farm_dict, farm_list)

    # Create tour network dataframe for only concerned dates
    tour_net = fun.create_tour_df(start_date, end_date)

    # Create geo network array
    geo_net = fun.create_geo_arr()

    while curr_date <= end_date:
        # Spread infection among pigs in the farm
        sim_data, infected_farm_list = fun.update_spread_within_farms(sim_data,
                                                                      infected_farm_list,
                                                                      curr_date,
                                                                      infected_pig_list)

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
    results_by_compart['run_num'] = curr_run

    # Convert to list and append to master list
    # all_runs_infected_farm.append(results_by_compart)

    results_by_contact = pd.DataFrame(infected_pig_list, columns=['date', 'contact_type', 'num_inf_pigs'])

    results_by_contact_grp = results_by_contact.groupby(['date', 'contact_type'], as_index=False).agg({
        'num_inf_pigs': sum})

    # Add the number of the run
    results_by_contact_grp['run_num'] = curr_run

    # Convert to list and append to master list
    # all_runs_infected_pig.append(results_by_contact_grp)

    # Save data to file
    np.savetxt(output_dir + "results_by_contact_grp_" + str(curr_run) + ".csv",
               results_by_contact_grp, delimiter=", ", fmt='%s,%s,%i,%i')
    np.savetxt(output_dir + "results_by_compart_"+ str(curr_run) + ".csv",
               results_by_compart, delimiter=", ", fmt='%s,%i,%i,%i,%i,%i')


if __name__ == '__main__':
    """Initiates main.
    """
    main()
