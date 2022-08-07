""" SwineNet Network Simulation Model.

Simple network simulation model
"""
import datetime
import numpy as np

import global_setup as gs
import transmit_disease as ts


def update_spread_within_farms_surv(
        sim_data: np.array,
        infected_farm_list: list,
        curr_date: datetime,
        infected_pig_list: list,
        mortality_rate_inc: float,
        morbidity_rate: float,
        farmer_prop: float,
        farmer_alert_dict: dict,
        farmer_alert_arr: np.array,
        farmer_no_init: np.array,
        ds) -> np.array:
    for idx in np.arange(0, sim_data.shape[0]):

        # Store information of all entries with at least 1 infected, 1 exposed, or 1 deceased pig (or
        # isolated/quarantined)
        if sim_data[idx, gs.INF] > 0 or sim_data[idx, gs.ASY] > 0 or \
                sim_data[idx, gs.EX] > 0 or sim_data[idx, gs.EXS] > 0 or sim_data[idx, gs.REM] > 0 or sim_data[
            idx, gs.REC] > 0 or \
                sim_data[idx, gs.ISO] or sim_data[idx, gs.QUA_S] or sim_data[idx, gs.QUA_E] or sim_data[idx, gs.QUA_A]:

            infected_farm_list.append([curr_date, idx,
                                       sim_data[idx, gs.SU] + sim_data[idx, gs.SUS],
                                       sim_data[idx, gs.EX] + sim_data[idx, gs.EXS],
                                       sim_data[idx, gs.INF], sim_data[idx, gs.ASY],
                                       sim_data[idx, gs.REM], sim_data[idx, gs.REC],
                                       sim_data[idx, gs.ISO],
                                       sim_data[idx, gs.QUA_S], sim_data[idx, gs.QUA_E], sim_data[idx, gs.QUA_A]])

            # Select all entries with at least 1 infected (symp or asymp) or exposed pig
            if sim_data[idx, gs.INF] > 0 or sim_data[idx, gs.EX] > 0 or sim_data[idx, gs.EXS] > 0 or sim_data[
                idx, gs.ASY] > 0:
                new_su, new_sus, new_exp, new_exps, new_inf, new_asy, new_rem, new_rec, e_to_ai = \
                    ts.run_farm_spread(sim_data[idx, gs.SU],
                                       sim_data[idx, gs.SUS],
                                       sim_data[idx, gs.EX],
                                       sim_data[idx, gs.EXS],
                                       sim_data[idx, gs.INF],
                                       sim_data[idx, gs.ASY],
                                       sim_data[idx, gs.REM],
                                       sim_data[idx, gs.REC],
                                       ds)

                sim_data[idx, gs.SU] = new_su
                sim_data[idx, gs.SUS] = new_sus
                sim_data[idx, gs.EX] = new_exp
                sim_data[idx, gs.EXS] = new_exps
                sim_data[idx, gs.INF] = new_inf
                sim_data[idx, gs.ASY] = new_asy
                sim_data[idx, gs.REM] = new_rem
                sim_data[idx, gs.REC] = new_rec

                infected_pig_list.append([curr_date, 'f', e_to_ai])

                # Check if mortality rate increase is more than surveillance threshold
                if sim_data[idx, gs.REM] > 0 and not farmer_alert_arr[idx] and not farmer_no_init[idx]:
                    num_tot_pigs = sim_data[idx, gs.SU] + sim_data[idx, gs.EX] + \
                                   sim_data[idx, gs.SUS] + sim_data[idx, gs.EXS] + \
                                   sim_data[idx, gs.ASY] + sim_data[idx, gs.INF] + \
                                   sim_data[idx, gs.REM] + sim_data[idx, gs.REC]

                    prop_dec = sim_data[idx, gs.REM] / num_tot_pigs  # proportion of deceased since start of simulation

                    # if proportion is greater than surveillance threshold, then add farm to "farmer alerted" field
                    if prop_dec > (mortality_rate_inc + gs.INIT_FARM_MORT):

                        # randomly select farms that will not initiate surveillance based on param farmer_prop
                        r_int = np.random.randint(1,10)

                        if r_int > (farmer_prop * 10): # the random number draw leads to farmer inaction
                            farmer_no_init[idx] = True
                        else:
                            # set testing_date to be farmer_surv_day_delay number of days after reaching threshold
                            test_date = curr_date + datetime.timedelta(days=gs.FARM_SURV_DAY_DELAY)
                            if test_date in farmer_alert_dict:
                                farmer_alert_dict[test_date].append(idx)
                            else:
                                farmer_alert_dict[test_date] = [idx]

                            # set flag of farmer_alert in array to TRUE so I don't keep adding the farm to the dictionary
                            farmer_alert_arr[idx] = True

                # Check for morbidity proportion of symptomatic is more than surveillance threshold
                if sim_data[idx, gs.INF] > 0 and not farmer_alert_arr[idx] and not farmer_no_init[idx]:
                    num_tot_pigs = sim_data[idx, gs.SU] + sim_data[idx, gs.EX] + \
                                   sim_data[idx, gs.SUS] + sim_data[idx, gs.EXS] + \
                                   sim_data[idx, gs.ASY] + sim_data[idx, gs.INF] + \
                                   sim_data[idx, gs.REM] + sim_data[idx, gs.REC]

                    # proportion of infected or removed since start of simulation
                    prop_inf = (sim_data[idx, gs.INF] + sim_data[idx, gs.REM]) / num_tot_pigs
                    # if proportion is greater than surveillance threshold, then add farm to "farmer alerted" field
                    if prop_inf > morbidity_rate:
                        # print("prop_inf: " + str(prop_inf))

                        # randomly select farms that will not initiate surveillance based on param farmer_prop
                        r_int = np.random.randint(1, 10)  # returns a list so need the first element

                        if r_int > (farmer_prop * 10):  # the random number draw leads to farmer inaction
                            farmer_no_init[idx] = True
                        else:
                            # set testing_date to be farmer_surv_day_delay number of days after reaching threshold
                            test_date = curr_date + datetime.timedelta(days=gs.FARM_SURV_DAY_DELAY)
                            if test_date in farmer_alert_dict:
                                farmer_alert_dict[test_date].append(idx)
                            else:
                                farmer_alert_dict[test_date] = [idx]

                            # set flag of farmer_alert in array to TRUE so I don't keep adding the farm to the dictionary
                            farmer_alert_arr[idx] = True

    return sim_data, infected_farm_list, infected_pig_list, farmer_alert_dict, farmer_alert_arr, farmer_no_init


def deploy_farmer_surv(farmer_alert_dict,
                       sim_data,
                       inspect_farm_list,
                       curr_date,
                       control):
    farmer_idx_to_inspect = farmer_alert_dict[curr_date]
    # print("farmer_surv_len: " + str(len(farmer_idx_to_inspect)))
    for idx in farmer_idx_to_inspect:

        num_discovered = ts.inspect_herd_farm(sim_data[idx, gs.INF],
                                              sim_data[idx, gs.SU] + sim_data[idx, gs.SUS],
                                              sim_data[idx, gs.EX] + sim_data[idx, gs.EXS],
                                              sim_data[idx, gs.ASY])

        # print("farm_idx: " + str(idx) + " num_dis: " + str(num_discovered))

        if num_discovered > 0:
            inspect_farm_list.append((idx, curr_date, num_discovered))

            # Move the detected pigs to "isolated" category
            sim_data[idx, gs.INF] = sim_data[idx, gs.INF] - num_discovered
            sim_data[idx, gs.ISO] = sim_data[idx, gs.ISO] + num_discovered

            if control == "quarantine":
                # Move susceptible to quarantine
                sim_data[idx, gs.QUA_S] = sim_data[idx, gs.SU] + sim_data[idx, gs.SUS] + sim_data[idx, gs.QUA_S]
                sim_data[idx, gs.SU] = 0
                sim_data[idx, gs.SUS] = 0
                # Move exposed to quarantineE
                sim_data[idx, gs.QUA_E] = sim_data[idx, gs.EX] + sim_data[idx, gs.EXS] + sim_data[idx, gs.QUA_S]
                sim_data[idx, gs.EX] = 0
                sim_data[idx, gs.EXS] = 0
                # Move asymptomatic to quarantine_A
                sim_data[idx, gs.QUA_A] = sim_data[idx, gs.ASY] + sim_data[idx, gs.QUA_A]
                sim_data[idx, gs.ASY] = 0

    return sim_data, inspect_farm_list
