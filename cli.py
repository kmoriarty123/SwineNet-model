"""Command Line Processing File.

Interprets the arguments from the commandline,
creates instance of TranscriptSampler and
runs the functions from TranscriptSampler class

"""

import argparse
import datetime

import network_functions as fun

parser = argparse.ArgumentParser(description='Simulate Network Spread')
parser.add_argument('--start_date', type=datetime.date.fromisoformat, help="The Start Date - format YYYY-MM-DD", )
parser.add_argument('--end_date', type=datetime.date.fromisoformat, help="The End Date - format YYYY-MM-DD", )
# parser.add_argument('--my_file', type=str, help='dest file name')

def main():
    """Main function.

    Interprets the arguments from the commandline and
    simulates spread of infection within farms and between farms.
    """

    args = parser.parse_args()
    start_date = args.start_date
    end_date = args.end_date
    curr_date = start_date
    print(f"start_date: {start_date}")

    # Create farm index dictionary
    farm_dict, farm_key = fun.create_farm_dict(start_date.year, end_date.year)

    # Generate random index farm
    index_case = fun.set_index_case(farm_dict)

    # Create simulation data array
    disease_array = fun.create_sim_data(index_case, farm_dict)

    # Create tour network dataframe for only concerned dates
    tour_net = fun.create_tour_df(start_date, end_date)

    while curr_date < end_date:

        # Spread infection among pigs in the farm
        disease_array = fun.update_spread_within_farms(disease_array)

        # Spread infection between farms
        fun.update_spread_between_farms(farm_key, tour_net, disease_array, curr_date)

        # move to the next day
        curr_date += datetime.timedelta(days=1)


if __name__ == '__main__':
    """Initiates main.
    """
    main()

main()

