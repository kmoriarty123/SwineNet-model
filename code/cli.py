"""Command Line Processing File.

Interprets the arguments from the commandline,
calls the functions relating to spread of disease on farms and between farms dependent on parameter
values.

"""

import argparse
import datetime
import pickle
import random

import numpy as np
import pandas as pd

import surveillance_functions_slaughter as surv_s
import surveillance_functions_farmer as surv_f
import surveillance_functions_network as surv_n
import network_functions as fun
import transmit_disease as ts

parser = argparse.ArgumentParser(description='Simulate Network Spread')
parser.add_argument('--disease', type=str, default='PRRS',
                    help="Disease To Simulate. Options: ASF, APP, PRRS, EP")
parser.add_argument('--start_date', type=datetime.date.fromisoformat,
                    help="The Start Date - format YYYY-MM-DD", )
parser.add_argument('--end_date', type=datetime.date.fromisoformat,
                    help="The End Date - format YYYY-MM-DD", )
parser.add_argument('--curr_run', type=int,
                    help="The current run number")
parser.add_argument('--seed', type=int,
                    help="Seed for the current run")
parser.add_argument('--phi_factor', type=float, default=1.0,
                    help="Factor of phi")
parser.add_argument('--psi_factor', type=float, default=1.0,
                    help="Factor of psi")
parser.add_argument('--eta_factor', type=float, default=1.0,
                    help="Factor of eta")
parser.add_argument('--prop_tour_reduce', type=float, default=0.0,
                    help='Reduction of contacts by 0.05 and 0.10 to see change in outcome')
parser.add_argument('--idx_case_factor', type=int, default=2,
                    help="Choose Risk Factor for Index Weight. Options: 1, 2, 3")
parser.add_argument('--surveillance', type=str, default='none',
                    help="Surveillance Program(s). Options: none, slaughter, farmer, network, sensitivity")
parser.add_argument('--control', type=str, default='none',
                    help="Control Measures. Options: none, quarantine")
parser.add_argument('--mort_rate_inc', type=float, default=1.0,
                    help="Mortality rate increase for farmer-based surveillance")
parser.add_argument('--morbid_rate', type=float, default=1.0,
                    help="Morbidity rate for farmer-based surveillance")
parser.add_argument('--farmer_prop', type=float, default=1.0,
                    help="Proportion of farmers that initiate surveillance for farmer-based surveillance")
parser.add_argument('--test_date_int', type=int, default=90,
                    help="Number of days between testing at farms with specific network metrics")
parser.add_argument('--test_contact_net', nargs="*", type=str, default=['d'],
                    help="Contact Network types as list for testing farms")
parser.add_argument('--test_top_thresh', type=int, default=250,
                    help="Top number of farms with a certain network metric")
parser.add_argument('--num_sh', type=int, default=9,
                    help="Number of Slaughterhouses to choose")


def main():
    """Main function.

    Interprets the arguments from the commandline and
    simulates spread of infection within farms and between farms.
    """
    # To determine runtime
    start = datetime.datetime.now()

    # Read arguments
    args = parser.parse_args()
    disease = args.disease
    start_date = args.start_date
    end_date = args.end_date
    curr_run = args.curr_run
    seed = args.seed

    # Sensitivity analysis parameters
    phi_factor = args.phi_factor
    psi_factor = args.psi_factor
    eta_factor = args.eta_factor
    idx_case_factor = args.idx_case_factor
    prop_tour_reduce = args.prop_tour_reduce

    # Surveillance specific parameters
    surveillance_type = args.surveillance
    mortality_rate_inc = args.mort_rate_inc
    morbid_rate = args.morbid_rate
    farmer_prop = args.farmer_prop
    testing_date_interval = args.test_date_int
    testing_contact_network_list = args.test_contact_net
    test_top_thresh = args.test_top_thresh
    num_sh = args.num_sh

    # Control specific parameters
    control = args.control

    # Disease specific parameters
    if disease == 'PRRS':
        from PRRS_setup import Parameters as ds
    elif disease == "APP":
        from APP_setup import Parameters as ds
    elif disease == "ASF":
        from ASF_setup import Parameters as ds

    # Change phi and psi for sensitivity analysis (default factor is 1 so will remain the same)
    ds.PHI = ds.PHI * phi_factor
    ds.PSI = ds.PSI * psi_factor
    ds.ETA = ds.ETA * eta_factor

    str_start_date = str(start_date.year) + "_" + str(start_date.month) + "_" + str(start_date.day)

    # Define the output_dir based on the parameters
    if surveillance_type == 'network':
        output_dir = "../output/" + str(disease) + "/" + str_start_date + "/" + surveillance_type + "_surv" + "/" + \
                     "nets_" + str(test_top_thresh) + "_" + str(testing_date_interval) + "_" + \
                     "_".join(testing_contact_network_list) + "/"
    elif surveillance_type == 'farmer':
        if mortality_rate_inc < 1:
            output_dir = "../output/" + str(disease) + "/" + str_start_date + "/" + surveillance_type + "_surv" + "/" + \
                         "farmer_prop_" + str(farmer_prop) + "_mort_rate_inc_" + str(mortality_rate_inc) + "/"
        else:
            output_dir = "../output/" + str(disease) + "/" + str_start_date + "/" + surveillance_type + "_surv" + "/" + \
                         "farmer_prop_" + str(farmer_prop) + "_morbid_rate_" + str(morbid_rate) + "/"
    elif surveillance_type == 'slaughter':
        output_dir = "../output/" + str(disease) + "/" + str_start_date + "/" + surveillance_type + "_surv" + "/" + \
                     "num_sh_" + str(num_sh) + "/"
    elif surveillance_type == 'none':
        output_dir = "../output/" + str(disease) + "/" + str_start_date + "/" + "no_surv" + "/" + "no_surv" + "/"
    elif surveillance_type == 'sensitivity':
        if idx_case_factor != 2:
            output_dir = "../output/" + str(disease) + "/" + str_start_date + "/" + surveillance_type + "/" + \
                         "idx_case_factor_" + str(idx_case_factor) + "/"
        elif prop_tour_reduce != 0.0:
            if(prop_tour_reduce < 0.001):
                output_dir = "../output/" + str(disease) + "/" + str_start_date + "/" + surveillance_type + "/" + \
                         "limit_tour_contacts_" + '{:f}'.format(prop_tour_reduce) + "/"
            else:
                output_dir = "../output/" + str(disease) + "/" + str_start_date + "/" + surveillance_type + "/" + \
                             "limit_tour_contacts_" + str(prop_tour_reduce) + "/"
        elif phi_factor != 1.0:
            output_dir = "../output/" + str(disease) + "/" + str_start_date + "/" + surveillance_type + "/" + \
                         "phi_factor_" + str(phi_factor) + "/"
        elif psi_factor != 1.0:
            output_dir = "../output/" + str(disease) + "/" + str_start_date + "/" + surveillance_type + "/" + \
                         "psi_factor_" + str(psi_factor) + "/"
        elif eta_factor != 1.0:
            output_dir = "../output/" + str(disease) + "/" + str_start_date + "/" + surveillance_type + "/" + \
                         "eta_factor_" + str(eta_factor) + "/"

    # Set seed for the current run
    random.seed(seed)
    np.random.seed(seed)

    # initialize lists / dicts
    infected_farm_list = []
    infected_pig_list = []
    inspected_tours_list = []  # to store info regarding tours that were inspected and found infected pigs
    inspected_farm_list = []  # to store info regarding farms that were inspected and found infected pigs

    # Set current date
    curr_date = start_date

    print(f"run: {curr_run}, surv_type: {surveillance_type}", flush=True)

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

    # To limit the tour data by a certain proportion
    if prop_tour_reduce != 0.0:
        other_trans_df = fun.limit_tour_contacts(prop_tour_reduce,
                                                 other_trans_df)
        #increase parameter values of tour so that changes could be visible
        ds.PHI = ds.PHI * 200.0
        ds.PSI = ds.PSI * 200.0
        ds.ETA = ds.ETA * 200.0

    # Generate index farm based on different factors of each disease
    index_farm_idx, index_farm_tvd = fun.set_index_case(farm_list,
                                                        curr_run,
                                                        output_dir,
                                                        disease,
                                                        idx_case_factor)
    # Update sim data with index case information
    sim_data = fun.update_sim_data(index_farm_idx,
                                   sim_data)

    # For PRRS, for all farms with sows, move the susceptibles to new compartment SUS for different transmission params
    if disease == 'PRRS':
        sim_data = fun.update_sim_data_sows_PRRS(farm_list,
                                                 sim_data)

    # Create tour network dataframe for only concerned dates
    tour_arr, direct_trans_df = fun.create_tour_arr(start_date,
                                                    end_date,
                                                    farm_dict,
                                                    direct_trans_df)

    day_count = 0  # To keep track of number of days passed (for tour_array column index)

    # Add surveillance programs if passed
    if surveillance_type == 'slaughter':

        # Create list of slaughter houses that are selected for surveillance
        slaughter_indices = surv_s.create_slaughterhouse_list(farm_dict,
                                                              num_sh)

        direct_trans_df = surv_s.find_transports_to_slaughter(slaughter_indices, direct_trans_df,
                                                              start_date.year, end_date.year)

        while curr_date <= end_date:
            print(f"curr_date: {curr_date}", flush=True)
            # To test random number draws to make sure they are consistent
            # fun.testing()

            # Spread infection among pigs in the farm
            sim_data, infected_farm_list, infected_pig_list = ts.update_spread_within_farms(sim_data,
                                                                                            infected_farm_list,
                                                                                            curr_date,
                                                                                            infected_pig_list,
                                                                                            ds)
            # Spread infection between farms
            sim_data, infected_pig_list, inspected_tours_list = \
                surv_s.update_spread_between_farms_slaught_surv(tour_arr,
                                                                direct_trans_df,
                                                                other_trans_df,
                                                                sim_data,
                                                                curr_date,
                                                                day_count,
                                                                geo_arr,
                                                                infected_pig_list,
                                                                inspected_tours_list,
                                                                control,
                                                                ds)
            # move to the next day
            curr_date += datetime.timedelta(days=1)
            day_count = day_count + 1

    elif surveillance_type == 'farmer':
        # Farm tracking for surveillance delay of farm-based morbidity and mortality alerts
        farmer_alert_arr = np.full((len(sim_data), 1), False)  # to track which farms have initiated testing
        farmer_no_init = np.full((len(sim_data), 1), False)  # to track which farms have been randomly selected to not initiate testing
        farmer_alert_dict = {}  # to store farmer idx for farmer_surveilance delay

        while curr_date <= end_date:
            print(f"curr_date: {curr_date}", flush=True)
            #print("farm_idx of concern", sim_data[6901])

            # To test randome number draws to make sure they are consistent
            #fun.testing()

            if curr_date in farmer_alert_dict:
                sim_data, inspected_farm_list = surv_f.deploy_farmer_surv(farmer_alert_dict,
                                                                          sim_data,
                                                                          inspected_farm_list,
                                                                          curr_date,
                                                                          control)
            # Spread infection among pigs in the farm
            sim_data, infected_farm_list, infected_pig_list, \
            farmer_alert_dict, farmer_alert_arr, farmer_no_init  = \
                surv_f.update_spread_within_farms_surv(
                    sim_data,
                    infected_farm_list,
                    curr_date,
                    infected_pig_list,
                    mortality_rate_inc,
                    morbid_rate,
                    farmer_prop,
                    farmer_alert_dict,
                    farmer_alert_arr,
                    farmer_no_init,
                    ds)

            # Spread infection between farms
            sim_data, infected_pig_list = ts.update_spread_between_farms(tour_arr,
                                                                         direct_trans_df,
                                                                         other_trans_df,
                                                                         sim_data,
                                                                         curr_date,
                                                                         day_count,
                                                                         geo_arr,
                                                                         infected_pig_list,
                                                                         ds)
            # move to the next day
            curr_date += datetime.timedelta(days=1)
            day_count = day_count + 1

    elif surveillance_type == 'network':

        # pick testing dates for farms that have specific network metrics
        test_dates_list = surv_n.pick_test_dates(testing_date_interval,
                                                 start_date,
                                                 end_date)
        # create testing_farm_list
        testing_farm_idx = surv_n.create_test_farm_list(farm_dict,
                                                        testing_contact_network_list,
                                                        test_top_thresh)

        while curr_date <= end_date:
            print(f"curr_date: {curr_date}", flush=True)

            # Spread infection among pigs in the farm
            sim_data, infected_farm_list, infected_pig_list = ts.update_spread_within_farms(sim_data,
                                                                                            infected_farm_list,
                                                                                            curr_date,
                                                                                            infected_pig_list,
                                                                                            ds)
            # Spread infection between farms
            sim_data, infected_pig_list = ts.update_spread_between_farms(tour_arr,
                                                                         direct_trans_df,
                                                                         other_trans_df,
                                                                         sim_data,
                                                                         curr_date,
                                                                         day_count,
                                                                         geo_arr,
                                                                         infected_pig_list,
                                                                         ds)

            if curr_date in test_dates_list:
                print("TESTING DAY!: ", curr_date)
                sim_data, inspected_farm_list = surv_n.network_surv_test_farm(testing_farm_idx,
                                                                              testing_contact_network_list,
                                                                              sim_data,
                                                                              inspected_farm_list,
                                                                              curr_date,
                                                                              control)

            # move to the next day
            curr_date += datetime.timedelta(days=1)
            day_count = day_count + 1

    elif surveillance_type == 'none' or surveillance_type == 'sensitivity':
        while curr_date <= end_date:
            print(f"curr_date: {curr_date}", flush=True)

            # Spread infection among pigs in the farm
            sim_data, infected_farm_list, infected_pig_list = ts.update_spread_within_farms(sim_data,
                                                                                            infected_farm_list,
                                                                                            curr_date,
                                                                                            infected_pig_list,
                                                                                            ds)

            # Spread infection between farms
            sim_data, infected_pig_list = ts.update_spread_between_farms(tour_arr,
                                                                         direct_trans_df,
                                                                         other_trans_df,
                                                                         sim_data,
                                                                         curr_date,
                                                                         day_count,
                                                                         geo_arr,
                                                                         infected_pig_list,
                                                                         ds)

            # move to the next day
            curr_date += datetime.timedelta(days=1)
            day_count = day_count + 1

    # Summarize data for that run
    results_all = pd.DataFrame(infected_farm_list,
                               columns=['date', 'farm_idx',
                                        'susceptible', 'exposed',
                                        'infected', 'asymptomatic',
                                        'removed', 'recovered',
                                        'isolated', 'quarantined_s', 'quarantined_e', 'quarantined_a'])

    results_by_compart = results_all.groupby('date', as_index=False).agg({
        'farm_idx': "count",
        'exposed': sum,
        'infected': sum,
        'asymptomatic': sum,
        'removed': sum,
        'recovered': sum,
        'isolated': sum,
        'quarantined_s': sum,
        'quarantined_e': sum,
        'quarantined_a': sum,
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
               delimiter=", ", fmt='%s,%i,%i,%i,%i,%i,%i,%i,%i,%i,%i,%i')

    end = datetime.datetime.now()
    print("Run time: ", (end - start).total_seconds())


if __name__ == '__main__':
    """Initiates main.
    """
    main()
