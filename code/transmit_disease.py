""" SwineNet Network Simulation Model.

Simple network simulation model
"""
import datetime
import numpy as np
import pandas as pd

import global_setup as gs

# To import global disease variables later
# def global_imports(module_name, abbr):
#    globals()[abbr] = __import__(module_name)

# def set_disease_config():
#    globals()["ds"] = __import__("ASF_setup")

def update_spread_within_farms(
        sim_data: np.array,
        infected_farm_list: list,
        curr_date: datetime,
        infected_pig_list: list,
        ds) -> np.array:
    """ Updates spread within the farms"""
    for idx in np.arange(0, sim_data.shape[0]):

        # Store information of all entries with at least 1 infected, 1 exposed, or 1 deceased pig
        if sim_data[idx, gs.INF] > 0 or sim_data[idx, gs.ASY] > 0 or \
                sim_data[idx, gs.EX] > 0 or sim_data[idx, gs.EXS] > 0 or \
                sim_data[idx, gs.REM] > 0 or sim_data[idx, gs.REC] > 0 or \
                sim_data[idx, gs.ISO] or sim_data[idx, gs.QUA_S] or sim_data[idx, gs.QUA_E] or sim_data[idx, gs.QUA_A]:

            infected_farm_list.append([curr_date, idx,
                                       sim_data[idx, gs.SU] + sim_data[idx, gs.SUS],
                                       sim_data[idx, gs.EX] + sim_data[idx, gs.EXS],
                                       sim_data[idx, gs.INF], sim_data[idx, gs.ASY],
                                       sim_data[idx, gs.REM], sim_data[idx, gs.REC],
                                       sim_data[idx, gs.ISO],
                                       sim_data[idx, gs.QUA_S], sim_data[idx, gs.QUA_E], sim_data[idx, gs.QUA_A]])

            # Select all entries with at least 1 infectious (symp or asymp) or exposed pig
            if sim_data[idx, gs.EX] > 0 or sim_data[idx, gs.EXS] > 0 or \
                    sim_data[idx, gs.INF] > 0 or sim_data[idx, gs.ASY] > 0:
                # Call function to run spread within the farm
                new_su, new_sus, new_exp, new_exps, new_inf, new_asy, new_rem, new_rec, e_to_ai = run_farm_spread(
                    sim_data[idx, gs.SU],
                    sim_data[idx, gs.SUS],
                    sim_data[idx, gs.EX],
                    sim_data[idx, gs.EXS],
                    sim_data[idx, gs.INF],
                    sim_data[idx, gs.ASY],
                    sim_data[idx, gs.REM],
                    sim_data[idx, gs.REC],
                    ds)
                # Update new values
                sim_data[idx, gs.SU] = new_su
                sim_data[idx, gs.SUS] = new_sus
                sim_data[idx, gs.EX] = new_exp
                sim_data[idx, gs.EXS] = new_exps
                sim_data[idx, gs.INF] = new_inf
                sim_data[idx, gs.ASY] = new_asy
                sim_data[idx, gs.REM] = new_rem
                sim_data[idx, gs.REC] = new_rec

                # update list to track daily values
                infected_pig_list.append([curr_date, 'f', e_to_ai])

    return sim_data, infected_farm_list, infected_pig_list


# Define the simulation function for PRRS
def run_farm_spread(sus, sus_s, exp, exp_s, inf, asy, rem, rec, ds):
    # Initial number of infected and recovered individuals
    S0, SS0, E0, ES0, I0, A0, RM0, RC0 = sus, sus_s, exp, exp_s, inf, asy, rem, rec

    # Total pig population on the farm, N.
    N = S0 + SS0 + E0 + ES0 + I0 + A0 + RC0

    # Calculate expected values and probabilities
    # Note difference from RHO and THETA
    exp_S_to_E = gs.TAU * ds.BET * S0 * (I0 + ds.KAP * A0) / N
    exp_SS_to_ES = gs.TAU * ds.BET * SS0 * (I0 + ds.KAP * A0) / N
    prob_E_to_IA = 1 - np.exp(-ds.SIG * gs.TAU)
    prob_ES_to_IA = 1 - np.exp(-ds.SIG * gs.TAU)
    prob_I_to_R = 1 - np.exp(-ds.DEL * gs.TAU)
    prob_A_to_RC = 1 - np.exp(-ds.GAM * gs.TAU)

    # Calculate the random draws
    S_to_E = np.random.poisson(exp_S_to_E)
    SS_to_ES = np.random.poisson(exp_SS_to_ES)
    E_to_IA = np.random.binomial(E0, prob_E_to_IA)
    ES_to_IA = np.random.binomial(ES0, prob_ES_to_IA)
    I_to_R = np.random.binomial(I0, prob_I_to_R)
    A_to_RC = np.random.binomial(A0, prob_A_to_RC)

    # Draws for the E to I and E to A split and I to RC and I to RM split
    E_to_A = np.random.binomial(E_to_IA, ds.RHO)
    E_to_I = E_to_IA - E_to_A
    ES_to_A = np.random.binomial(ES_to_IA, ds.RHO_S)
    ES_to_I = ES_to_IA - ES_to_A
    I_to_RM = np.random.binomial(I_to_R, ds.THE)
    I_to_RC = I_to_R - I_to_RM

    S = S0 - min(S_to_E, S0)  # ensure S is never negative
    SS = SS0 - min(SS_to_ES, SS0)  # ensure SS is never negative
    E = E0 + min(S_to_E, S0) - E_to_I - E_to_A
    ES = ES0 + min(SS_to_ES, SS0) - ES_to_I - ES_to_A
    I = I0 + E_to_I + ES_to_I - I_to_RM - I_to_RC
    A = A0 + E_to_A + ES_to_A - A_to_RC
    RM = RM0 + I_to_RM
    RC = RC0 + A_to_RC + I_to_RC

    return S, SS, E, ES, I, A, RM, RC, E_to_A + E_to_I + ES_to_A + ES_to_I


def update_spread_between_farms(tour_arr: np.array,
                                direct_trans_df: pd.DataFrame,
                                other_trans_df: pd.DataFrame,
                                sim_data: np.array,
                                curr_date: datetime,
                                day_count: int,
                                geo_data: np.array,
                                infected_pig_list: list,
                                ds) -> np.array:
    """ Updates spread between the farms"""

    # grab the infected farm indices
    infected_farm_idx = np.where((sim_data[:, gs.INF] > 0) | (sim_data[:, gs.ASY] > 0) |
                                 (sim_data[:, gs.EX] > 0) | (sim_data[:, gs.EXS] > 0))[0]

    # Grab direct transports that are on current_date
    curr_tours = direct_trans_df[(direct_trans_df['event_date'] == curr_date)].to_numpy()

    # Loop through infected farms
    for farm_idx in infected_farm_idx:

        # Total number of pigs in the infected farm
        N = sim_data[farm_idx, gs.SU] + sim_data[farm_idx, gs.SUS] + \
            sim_data[farm_idx, gs.EX] + sim_data[farm_idx, gs.EXS] + \
            sim_data[farm_idx, gs.INF] + sim_data[farm_idx, gs.ASY] + sim_data[farm_idx, gs.REC]

        # Transport Network Spread

        # Check to see if the infected farm has a tour
        if tour_arr[farm_idx, day_count] == 1:
            #print("found a tranport!")
            # Grab record of infected farm transport
            inf_farm_tour = curr_tours[np.where(curr_tours[:, gs.SRC] == farm_idx)[0]][0]

            # Get index of destination farm
            dest_tvd_id = inf_farm_tour[gs.DEST]

            # Calculate the number of exposed (non sow farm) pigs sent on the tour
            tran_exp_pigs = min(sim_data[farm_idx, gs.EX],
                                inf_farm_tour[gs.T_NPIGS],
                                np.random.poisson(gs.TAU * inf_farm_tour[gs.T_NPIGS] *
                                                  sim_data[farm_idx, gs.EX] / N))

            # Calculate the number of exposed (sow farm) pigs sent on the tour
            tran_exp_pigs_sow = min(sim_data[farm_idx, gs.EXS],
                                    (inf_farm_tour[gs.T_NPIGS] - tran_exp_pigs),
                                    np.random.poisson(gs.TAU * inf_farm_tour[gs.T_NPIGS] *
                                                      sim_data[farm_idx, gs.EXS] / N))

            # Calculate the number of infected pigs sent on the tour
            tran_inf_pigs = min(sim_data[farm_idx, gs.INF],
                                (inf_farm_tour[gs.T_NPIGS] - tran_exp_pigs - tran_exp_pigs_sow),
                                np.random.poisson(gs.TAU * inf_farm_tour[gs.T_NPIGS] *
                                                  sim_data[farm_idx, gs.INF] / N))

            # Calculate the number of asymptomatic infected pigs sent on the tour
            tran_inf_pigs_asym = min(sim_data[farm_idx, gs.ASY],
                                     (inf_farm_tour[gs.T_NPIGS] - tran_exp_pigs - tran_exp_pigs_sow - tran_inf_pigs),
                                     np.random.poisson(gs.TAU * inf_farm_tour[gs.T_NPIGS] *
                                                       sim_data[farm_idx, gs.ASY] / N))

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

                # Update infected pig count for infected farm and destination farm
                sim_data[farm_idx, gs.INF] = sim_data[farm_idx, gs.INF] - tran_inf_pigs
                sim_data[dest_tvd_id, gs.INF] = sim_data[dest_tvd_id, gs.INF] + tran_inf_pigs

            if tran_inf_pigs_asym > 0:
                infected_pig_list.append([curr_date, 'd', tran_inf_pigs_asym])

                # Update infected pig count for infected farm and destination farm (ensure it isn't negative)
                sim_data[farm_idx, gs.ASY] = sim_data[farm_idx, gs.ASY] - tran_inf_pigs_asym
                sim_data[dest_tvd_id, gs.ASY] = sim_data[dest_tvd_id, gs.ASY] + tran_inf_pigs_asym

            # If an infected pig is on the truck, check for other spreading routes
            if tran_exp_pigs > 0 or tran_exp_pigs_sow > 0 or tran_inf_pigs_asym > 0 or tran_inf_pigs > 0:

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
                            pig_inf_pigs = np.random.poisson(gs.TAU *
                                                             (tran_inf_pigs + ds.KAP * tran_inf_pigs_asym) *
                                                             ds.PHI *
                                                             pigs_2_dest)
                            # print("p2p: ", pig_inf_pigs, flush=True)
                            infected_pig_list.append([curr_date, 't', pig_inf_pigs])

                            if pig_inf_pigs > 0:
                                # Update exposed pig count for the indirect destination farm
                                sim_data[dest_idx, gs.EX] = sim_data[dest_idx, gs.EX] + pig_inf_pigs

                        # Indirect truck sharing contacts
                        elif curr_tour[gs.CNTCT] == 'i':

                            # number of pigs heading to destination farm that mix with infected herd
                            pigs_2_dest = curr_tour[gs.T_NPIGS]

                            # Calculate the number of pigs infected by fomites from uncleaned truck
                            fom_inf_pigs = np.random.poisson(gs.TAU *
                                                             (tran_inf_pigs + ds.KAP * tran_inf_pigs_asym) *
                                                             ds.PSI *
                                                             pigs_2_dest)

                            # print("fomites: ", fom_inf_pigs, flush=True)
                            infected_pig_list.append([curr_date, 'i', fom_inf_pigs])

                            if fom_inf_pigs > 0:
                                # Update infected pig count for the indirect destination farm
                                sim_data[dest_idx, gs.EX] = sim_data[dest_idx, gs.EX] + fom_inf_pigs

                        # Exterior truck fomites
                        elif curr_tour[gs.CNTCT] == 'e':

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
                                                      (sim_data[farm_idx, gs.INF] + ds.KAP * sim_data[farm_idx, gs.ASY]) *
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

    return sim_data, infected_pig_list


def inspect_herd_farm(num_inf_pigs: int,
                      num_sus_pigs: int,
                      num_ex_pigs: int,
                      num_asym_pigs: int):
    """ Inspect herd for disease """

    # Test all pigs on farm
    # TODO: include specificity and sensitivity of testing
    pigs_detected = num_inf_pigs  # initial assumption: all pigs on the farm are detected

    return pigs_detected
