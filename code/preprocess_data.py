"""Pre Processing File.

Creates farm_lists and farm_dicts and saves all the networks in preprocessed format for each year

Requires:
'../data/agis_data_lim.csv'
'../data/tour_network.csv'
'../data/geo_network.csv'
With Data Structure:
agis_data_lim: "year" "tvd_nr" "gde_nr" "gde_name" "is_pig_stall" "holding_cat" "tot_pigs" "sows_boar_ind"
    "idx_weight_PRRS" "idx_weight_ASF" "idx_weight_APP" "idx_weight_PRRS_low" "idx_weight_ASF_low"
    "idx_weight_APP_low"  "idx_weight_PRRS_med" "idx_weight_ASF_med"  "idx_weight_APP_med"
tour_network:"tvd_source" "tvd_dest" "event_date" "n_pigs" "contact_type" "tour_id"
geo_network: "tvd_source" "tvd_dest" "dist" "contact_type"

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
