"""Command Line Processing File.

Interprets the arguments from the commandline,
creates instance of TranscriptSampler and
runs the functions from TranscriptSampler class

"""

import argparse
import datetime
import time  # just for checking run time

import pandas as pd

import network_functions as fun

parser = argparse.ArgumentParser(description='Simulate Network Spread')
parser.add_argument('--start_date', type=datetime.date.fromisoformat, help="The Start Date - format YYYY-MM-DD", )
parser.add_argument('--end_date', type=datetime.date.fromisoformat, help="The End Date - format YYYY-MM-DD", )
parser.add_argument('--index_case_tvd_id', type=int, help="The TVD ID of the index case", )


# parser.add_argument('--my_file', type=str, help='dest file name')

def main():
    """Main function.

    Interprets the arguments from the commandline and
    simulates spread of infection within farms and between farms.
    """
    run_start = time.perf_counter()

    args = parser.parse_args()
    start_date = args.start_date
    end_date = args.end_date
    curr_date = start_date
    index_case_tvd = args.index_case_tvd_id
    infected_farm_list = []
    infected_pig_list = []

    # Create farm index dictionary
    farm_dict, farm_list = fun.create_farm_dict(start_date.year, end_date.year)

    # Set index case and find the matching dictionary index for provided index case
    inf_tvd = index_case_tvd
    index_case = farm_dict[inf_tvd]

    print(inf_tvd, index_case)

    # Create simulation data array
    disease_array = fun.create_sim_data(index_case, farm_dict, farm_list)

    # Create tour network dataframe for only concerned dates
    tour_net = fun.create_tour_df(start_date, end_date)

    # Create geo network array
    geo_net = fun.create_geo_arr()

    while curr_date <= end_date:
        # Spread infection among pigs in the farm
        disease_array, infected_farm_list = fun.update_spread_within_farms(disease_array, infected_farm_list, curr_date)

        # Spread infection between farms
        disease_array, infected_pig_list = fun.update_spread_between_farms(farm_dict,
                                                                           tour_net,
                                                                           disease_array,
                                                                           curr_date,
                                                                           geo_net,
                                                                           infected_pig_list)

        # move to the next day
        curr_date += datetime.timedelta(days=1)

    # Rearrange infected farm list data
    results_all = pd.DataFrame(infected_farm_list, columns=['date', 'farm_idx', 'susceptible', 'exposed', 'infected',
                                                            'deceased'])

    results_all_long = pd.melt(results_all, id_vars=['date', 'farm_idx'], value_vars=['susceptible', 'exposed',
                                                                                      'infected',
                                                                                      'deceased'])

    results_by_compart = results_all.groupby('date', as_index=False).agg({
        'farm_idx': "count",
        'exposed': sum,
        'infected': sum,
        'deceased': sum
    })

    results_by_compart_long = pd.melt(results_by_compart, id_vars='date', value_vars=['farm_idx', 'exposed',
                                                                                      'infected', 'deceased'])

    # Rearrange infected pig list data
    results_by_contact = pd.DataFrame(infected_pig_list, columns=['date', 'contact_type', 'num_inf_pigs'])

    results_by_contact_grp = results_by_contact.groupby(['date', 'contact_type'], as_index=False).agg({
        'num_inf_pigs': sum})

    # Save data to file
    results_all.to_csv("output/" + str(index_case) + "_results_all.csv", sep=",", header=True)
    results_all_long.to_csv("output/" + str(index_case) + "_results_all_long.csv", sep=",", header=True)
    results_by_compart.to_csv("output/" + str(index_case) + "_results_by_compart.csv", sep=",", header=True)
    results_by_compart_long.to_csv("output/" + str(index_case) + "_results_by_compart_long.csv", sep=",", header=True)
    results_by_contact.to_csv("output/" + str(index_case) + "_results_by_contact.csv", sep=",", header=True)
    results_by_contact_grp.to_csv("output/" + str(index_case) + "_results_by_contact_grp.csv", sep=",", header=True)

    run_end = time.perf_counter()

    print(f"Runtime in {run_end - run_start:0.2f} seconds")


if __name__ == '__main__':
    """Initiates main.
    """
    main()
