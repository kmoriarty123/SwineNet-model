"""Pre Processing File.

Creates farm_lists and farm_dicts and saves all the networks in preprocessed format for each year

"""

import preprocess_functions as prep

def main():
    """Main function.

    """

    # Create farm index dictionary
    prep.create_farm_dict()

    # Create simulation data array
    prep.create_sim_data()

    # Create tour network dataframe
    prep.create_tours()

    # Create geo network array
    prep.create_geo_arr()


if __name__ == '__main__':
    """Initiates main.
    """
    main()
