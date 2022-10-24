""" SwineNet Network Simulation Model.

Simple network simulation model
"""
import random
import datetime
from random import choices
import numpy as np
import pandas as pd

import global_setup as gs
import transmit_disease as ts


def create_slaughterhouse_list_old(
        farm_list: list,
        curr_run: int,
        output_dir: str,
        num_slaughter: int) -> list:
    """ Pick num_slaughter slaughterhouses at random to be surveilled

    :return: Index of slaughterhouses that were chosen for surveillance
    """

    slaughter_all_indices = []

    # Find slaughter houses by holding_cat variable
    for idx, row in enumerate(farm_list):
        if row[gs.TYPE] == "SlaughterEnterprise":
            slaughter_all_indices.append(idx)

    # Pick one random index from 0 to 1 less than total farms
    slaughter_indices_list = choices(slaughter_all_indices, k=num_slaughter)

    # Save the info re index case to file
    print(f"slaughter_indices_list: {slaughter_indices_list}")
    with open(output_dir + "\slaughters_chosen_" + str(curr_run) + ".csv", 'w') as out_file:
        # f.write(f'{item}\n')
        # f.write(farm_to_save + "\n")
        out_file.write('\n'.join(map(str, slaughter_indices_list)))

    return slaughter_indices_list


def create_slaughterhouse_list(
        farm_dict: dict,
        num_slaughter: int) -> list:
    """ Pick num_slaughter slaughterhouses at random to be surveilled

    :return: Index of slaughterhouses that were chosen for surveillance
    """
    if num_slaughter == 9:
        slaughter_tvd_list = pd.read_csv('../data/slaughter_surv_9.csv', header=None).values.tolist()[0]
    elif num_slaughter == 18:
        slaughter_tvd_list = pd.read_csv('../data/slaughter_surv_18.csv', header=None).values.tolist()[0]
    elif num_slaughter == 36:
        slaughter_tvd_list = pd.read_csv('../data/slaughter_surv_36.csv', header=None).values.tolist()[0]

    slaughter_all_indices = []

    for tvd in slaughter_tvd_list:
        if tvd in farm_dict:
            slaughter_all_indices.append(farm_dict[tvd])

    return slaughter_all_indices


def find_transports_to_slaughter(slaughter_indices_list: list,
                                 direct_trans_df: np.array,
                                 start_year: int,
                                 end_year: int) -> pd.DataFrame:
    """ Put a marker on transports to the slaughterhouses that would be tagged for inspection.

        :return: direct_trans_df with additional column for tagged for inspection
    """
    # Subset for all transports to that slaughterhouse
    slaughter_transports_df = direct_trans_df[direct_trans_df['dest_idx'].isin(slaughter_indices_list)]
    # Start of the active surveillance program
    inspect_start = datetime.date.fromisoformat(str(start_year) + "-" + gs.inspection_start_date)
    inspect_end = datetime.date.fromisoformat(str(start_year) + "-" + gs.inspection_end_date)

    # Limit transports to only those within the inspection timeframe
    slaughter_transports_lim = slaughter_transports_df[
        (slaughter_transports_df['event_date'] >= inspect_start) &
        (slaughter_transports_df['event_date'] <= inspect_end)]

    # Create subset of transports for the slaughterhouses as destination
    for sh_idx in slaughter_indices_list:  # for each randomly selected slaughterhouse
        # Only include those with at least 6 pigs
        curr_slaughter_df = slaughter_transports_lim[(slaughter_transports_lim['dest_idx'] == sh_idx) &
                                                     (slaughter_transports_lim['n_pigs'] >= 6)]

        # Only want to include the top MAX_FARMS_PER_SH
        curr_slaughter_df = curr_slaughter_df[0:gs.MAX_FARMS_PER_SH]

        # set inspection indicator to 1
        curr_slaughter_df['inspection_ind'] = 1

        # merge this subset with main direct transport dataframe
        direct_trans_df.update(curr_slaughter_df)

    # bug in pandas update function that converts all ints to floats
    # https://github.com/pandas-dev/pandas/issues/4094
    # Need to convert all back to ints
    direct_trans_df.iloc[:, [gs.SRC, gs.DEST, gs.T_NPIGS, gs.INSPCT]] = \
        direct_trans_df.iloc[:, [gs.SRC, gs.DEST, gs.T_NPIGS, gs.INSPCT]].values.astype(int)

    return direct_trans_df


def update_spread_between_farms_slaught_surv(tour_arr: np.array,
                                             direct_trans_df: pd.DataFrame,
                                             other_trans_df: pd.DataFrame,
                                             sim_data: np.array,
                                             curr_date: datetime,
                                             day_count: int,
                                             geo_data: np.array,
                                             infected_pig_list: list,
                                             inspect_trans_list: list,
                                             control: str,
                                             ds) -> np.array:
    # grab the infected farm indices
    infected_farm_idx = np.where((sim_data[:, gs.INF] > 0) | (sim_data[:, gs.ASY] > 0) |
                                 (sim_data[:, gs.EX] > 0) | (sim_data[:, gs.EXS] > 0))[0]

    # Grab direct transports that are on current_date
    curr_tours = direct_trans_df[(direct_trans_df['event_date'] == curr_date)].to_numpy()

    # Loop through infected farms
    for farm_idx in infected_farm_idx:

        # Total number of pigs in the infected farm
        N = sim_data[farm_idx, gs.SU] + sim_data[farm_idx, gs.EX] + \
            sim_data[farm_idx, gs.SUS] + sim_data[farm_idx, gs.EXS] + \
            sim_data[farm_idx, gs.INF] + sim_data[farm_idx, gs.ASY] + sim_data[farm_idx, gs.REC]

        # Transport Network Spread

        # Check to see if the infected farm has a tour
        if tour_arr[farm_idx, day_count] == 1:
            # print("FOUND A TOUR!")
            # Grab row where infected farm transport occurs
            inf_farm_tour = curr_tours[np.where(curr_tours[:, gs.SRC] == farm_idx)[0]][0]

            # Get index of destination farm
            dest_tvd_id = inf_farm_tour[gs.DEST]
            # print("inf_farm_tour:", inf_farm_tour, flush=True)

            # Calculate the number of exposed (sow farm) pigs sent on the tour
            tran_exp_pigs = min(sim_data[farm_idx, gs.EX],
                                np.random.poisson(gs.TAU *
                                                  inf_farm_tour[gs.T_NPIGS] *
                                                  sim_data[farm_idx, gs.EX] / N))

            # Calculate the number of exposed (sow farm) pigs sent on the tour
            tran_exp_pigs_sow = min(sim_data[farm_idx, gs.EXS],
                                    np.random.poisson(gs.TAU *
                                                      inf_farm_tour[gs.T_NPIGS] *
                                                      sim_data[farm_idx, gs.EXS] / N))

            # Calculate the number of infected pigs sent on the tour
            tran_inf_pigs = min(sim_data[farm_idx, gs.INF],
                                np.random.poisson(gs.TAU *
                                                  inf_farm_tour[gs.T_NPIGS] *
                                                  sim_data[farm_idx, gs.INF] / N))

            # Calculate the number of asymptomatic infected pigs sent on the tour
            tran_inf_pigs_asym = min(sim_data[farm_idx, gs.ASY],
                                     np.random.poisson(gs.TAU *
                                                       inf_farm_tour[gs.T_NPIGS] *
                                                       sim_data[farm_idx, gs.ASY] / N))

            # If an exposed/infected pig is picked for the tour, update the compartments
            if tran_exp_pigs > 0:
                infected_pig_list.append([curr_date, 'd', tran_exp_pigs])

                # Update infected pig count for infected farm and destination farm
                sim_data[farm_idx, gs.EX] = sim_data[farm_idx, gs.EX] - tran_exp_pigs
                sim_data[dest_tvd_id, gs.EX] = sim_data[dest_tvd_id, gs.EX] + tran_exp_pigs

            if tran_exp_pigs_sow > 0:
                infected_pig_list.append([curr_date, 'd', tran_exp_pigs_sow])

                # Update infected pig count for infected farm and destination farm
                sim_data[farm_idx, gs.EXS] = sim_data[farm_idx, gs.EXS] - tran_exp_pigs_sow
                sim_data[dest_tvd_id, gs.EXS] = sim_data[dest_tvd_id, gs.EXS] + tran_exp_pigs_sow

            if tran_inf_pigs > 0:
                infected_pig_list.append([curr_date, 'd', tran_inf_pigs])

                # Update infected pig count for infected farm and destination farm (ensure it isn't negative)
                sim_data[farm_idx, gs.INF] = sim_data[farm_idx, gs.INF] - tran_inf_pigs
                sim_data[dest_tvd_id, gs.INF] = sim_data[dest_tvd_id, gs.INF] + tran_inf_pigs

            if tran_inf_pigs_asym > 0:
                infected_pig_list.append([curr_date, 'd', tran_inf_pigs_asym])

                # Update infected pig count for infected farm and destination farm (ensure it isn't negative)
                sim_data[farm_idx, gs.ASY] = sim_data[farm_idx, gs.ASY] - tran_inf_pigs_asym
                sim_data[dest_tvd_id, gs.ASY] = sim_data[dest_tvd_id, gs.ASY] + tran_inf_pigs_asym

            # If an infected pig is on the truck, check for other spreading routes
            if tran_exp_pigs > 0 or tran_exp_pigs_sow > 0 or tran_inf_pigs_asym > 0 or tran_inf_pigs > 0:
                # Check if the transport is inspected at slaughter
                if inf_farm_tour[gs.INSPCT] == 1:
                    # Exposed pigs are not discovered at slaughter
                    num_discovered = inspect_herd_slaughter(inf_farm_tour[gs.T_NPIGS],
                                                            tran_inf_pigs + tran_inf_pigs_asym)
                    inspect_trans_list.append(np.append(inf_farm_tour, num_discovered))

                    # if pigs are detected at slaughterhouse, then isolate the infected pigs on the origin farm
                    # and quarantine all exposed, susceptible, and asymptomatic pigs
                    if num_discovered > 0:

                        num_discovered_farm = ts.inspect_herd_farm(sim_data[farm_idx, gs.INF],
                                                                   sim_data[farm_idx, gs.SU] + sim_data[
                                                                       farm_idx, gs.SUS],
                                                                   sim_data[farm_idx, gs.EX] + sim_data[
                                                                       farm_idx, gs.EXS],
                                                                   sim_data[farm_idx, gs.ASY])

                        # Move the detected pigs to "isolated" category
                        sim_data[farm_idx, gs.INF] = sim_data[farm_idx, gs.INF] - num_discovered_farm
                        sim_data[farm_idx, gs.ISO] = sim_data[farm_idx, gs.ISO] + num_discovered_farm

                        if control == "quarantine":
                            # Move susceptible to quarantine
                            sim_data[farm_idx, gs.QUA_S] = sim_data[farm_idx, gs.SU] + sim_data[farm_idx, gs.SUS] + \
                                                           sim_data[farm_idx, gs.QUA_S]
                            sim_data[farm_idx, gs.SU] = 0
                            sim_data[farm_idx, gs.SUS] = 0
                            # Move exposed to quarantineE
                            sim_data[farm_idx, gs.QUA_E] = sim_data[farm_idx, gs.EX] + sim_data[farm_idx, gs.EXS] + \
                                                           sim_data[farm_idx, gs.QUA_S]
                            sim_data[farm_idx, gs.EX] = 0
                            sim_data[farm_idx, gs.EXS] = 0
                            # Move asymptomatic to quarantine_A
                            sim_data[farm_idx, gs.QUA_A] = sim_data[farm_idx, gs.ASY] + sim_data[farm_idx, gs.QUA_A]
                            sim_data[farm_idx, gs.ASY] = 0

                # Check for indirect contact types
                indirect_contacts = other_trans_df[(other_trans_df['event_date'] == curr_date) &
                                                   (other_trans_df['source_idx'] == farm_idx)].to_numpy()

                if len(indirect_contacts) > 0:

                    for curr_tour in indirect_contacts:

                        # Get index of destination farm
                        dest_idx = curr_tour[gs.DEST]

                        # Direct truck sharing contacts
                        if curr_tour[gs.CNTCT] == 't':

                            # number of pigs heading to destination farm that mix with infected herd
                            pigs_2_dest = curr_tour[gs.T_NPIGS]

                            # Calculate the number of pigs infected
                            pig_inf_pigs = np.random.poisson(
                                gs.TAU *
                                (tran_inf_pigs + ds.KAP * tran_inf_pigs_asym) *
                                ds.PHI *
                                pigs_2_dest)
                            # print("p2p: ", pig_inf_pigs, flush=True)
                            infected_pig_list.append([curr_date, 't', pig_inf_pigs])

                            if pig_inf_pigs > 0:
                                # Update infected pig count for the indirect destination farm
                                sim_data[dest_idx, gs.EX] = sim_data[dest_idx, gs.EX] + pig_inf_pigs

                        # Indirect truck sharing contacts
                        elif curr_tour[gs.CNTCT] == 'i':

                            # number of pigs heading to destination farm that mix with infected herd
                            pigs_2_dest = curr_tour[gs.T_NPIGS]

                            # Calculate the number of pigs infected by fomites (uncleaned truck)
                            fom_inf_pigs = np.random.poisson(
                                gs.TAU *
                                (tran_inf_pigs + ds.KAP * tran_inf_pigs_asym) *
                                ds.PSI *
                                pigs_2_dest)

                            # print("fomites: ", fom_inf_pigs, flush=True)
                            infected_pig_list.append([curr_date, 'i', fom_inf_pigs])

                            if fom_inf_pigs > 0:
                                # Update infected pig count for the indirect destination farm
                                sim_data[dest_idx, gs.EX] = sim_data[dest_idx, gs.EX] + fom_inf_pigs

                        # Exterior truck fomites
                        if curr_tour[gs.CNTCT] == 'e':

                            # Number of pigs on the destination farm
                            dest_num_pigs = sim_data[dest_idx, gs.SU]
                            dest_num_pigs_sow = sim_data[dest_idx, gs.SUS]  # number of sows on destination farm

                            # Calculate the number of pigs indirectly infected
                            ind_inf_pigs = min(sim_data[dest_idx, gs.SU],
                                               np.random.poisson(gs.TAU *
                                                                 (tran_inf_pigs + ds.KAP * tran_inf_pigs_asym) *
                                                                 ds.ETA *
                                                                 dest_num_pigs))
                            ind_inf_pigs_sow = min(sim_data[dest_idx, gs.SUS],
                                                   np.random.poisson(gs.TAU *
                                                                     (tran_inf_pigs + ds.KAP * tran_inf_pigs_asym) *
                                                                     ds.ETA *
                                                                     dest_num_pigs_sow))

                            # print("ind inf pigs: ", ind_inf_pigs, flush=True)
                            infected_pig_list.append([curr_date, 'e', ind_inf_pigs + ind_inf_pigs_sow])

                            if ind_inf_pigs > 0:
                                # Update infected pig count for the indirect destination farm
                                sim_data[dest_idx, gs.EX] = sim_data[dest_idx, gs.EX] + ind_inf_pigs
                                sim_data[dest_idx, gs.SU] = sim_data[dest_idx, gs.SU] - ind_inf_pigs
                            if ind_inf_pigs_sow > 0:
                                # Update infected pig count for the indirect destination farm
                                sim_data[dest_idx, gs.EXS] = sim_data[dest_idx, gs.EXS] + ind_inf_pigs_sow
                                sim_data[dest_idx, gs.SUS] = sim_data[dest_idx, gs.SUS] - ind_inf_pigs_sow

        # Geographic Network Spread

        # Find any entries for infected farm in the geographic network
        geo_inf_arr = geo_data[np.where(geo_data[:, gs.G_SRC] == farm_idx)[0]]

        for curr_geo in geo_inf_arr:

            # get the index of the destination farm (returns 0 if the farm is not active during the applicable year(s))
            dest_geo_idx = curr_geo[gs.G_DEST]

            # calculate number of pigs infected thru local spread
            geo_inf_pigs = min(sim_data[dest_geo_idx, gs.SU],
                               np.random.poisson(gs.TAU *
                                                 sim_data[dest_geo_idx, gs.SU] *
                                                 (sim_data[farm_idx, gs.INF] + ds.KAP * sim_data[farm_idx, gs.ASY]) *
                                                 ds.OME))
            geo_inf_pigs_sows = min(sim_data[dest_geo_idx, gs.SUS],
                                    np.random.poisson(gs.TAU *
                                                      sim_data[dest_geo_idx, gs.SUS] *
                                                      (sim_data[farm_idx, gs.INF] + ds.KAP * sim_data[
                                                          farm_idx, gs.ASY]) *
                                                      ds.OME))

            if geo_inf_pigs > 0 or geo_inf_pigs_sows > 0:

                infected_pig_list.append([curr_date, 'g', geo_inf_pigs + geo_inf_pigs_sows])
                if geo_inf_pigs > 0:
                    # Update infected pig count for the indirect destination farm
                    sim_data[dest_geo_idx, gs.EX] = sim_data[dest_geo_idx, gs.EX] + geo_inf_pigs
                    sim_data[dest_geo_idx, gs.SU] = sim_data[dest_geo_idx, gs.SU] - geo_inf_pigs

                if geo_inf_pigs_sows > 0:
                    sim_data[dest_geo_idx, gs.EXS] = sim_data[dest_geo_idx, gs.EXS] + geo_inf_pigs_sows
                    sim_data[dest_geo_idx, gs.SUS] = sim_data[dest_geo_idx, gs.SUS] - geo_inf_pigs_sows

    return sim_data, infected_pig_list, inspect_trans_list


def inspect_herd_slaughter(num_trans: int,
                           num_inf_pigs: int):
    # Draw 6 random sample of pigs from the transported herd
    # print(num_trans, gs.MAX_PIGS_PER_FARM)
    pigs_sampled = random.sample(range(num_trans), gs.MAX_PIGS_PER_FARM)

    # Determine if any of the pigs that were sampled were also infected
    # Let first num_inf_pigs to be the infected pigs (0 is included in the pig sampling above so < num_inf_pigs)
    count = len([i for i in pigs_sampled if i < num_inf_pigs])

    return count
