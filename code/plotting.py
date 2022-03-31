import datetime
import plotting_functions as plot_fun
import plotting_functions_surv as plot_fun_surv

# import plotting_functions_farmer_surv as plot_fun_farmer

# parameters to change for reading and writing files
num_runs = 1000
start_date = datetime.date.fromisoformat('2014-01-01')
end_date = datetime.date.fromisoformat('2014-03-31')

# column headings
columns_compart = ['date', 'farm_count', 'exposed', 'infected', 'deceased', 'detected', 'num_run']
columns2 = ['date', 'contact_type', 'num_inf_pigs', 'num_run']
columns3 = ['tvd_nr', 'year', 'farm_type', 'gde_nr', 'gde_name',
            'pig_stall', 'tot_pigs', 'other_animals', 'which_animals',
            'bts_raus1', 'durch_tiere1', 'risk_gde', 'idx_weight', 'num_run']
columns_slaughter_inspect = ['source_idx', 'dest_idx', 'date', 'n_pigs', 'inspect_ind', 'n_detect', 'num_run']
columns_farmer_detect = ['farm_idx', 'date', 'n_detect', 'num_run']
columns_net_detect = ['farm_idx', 'date', 'net_contact', 'n_detect', 'num_run']

# directories
output_dir_no = "../output/" + str(start_date.year) + "_" + str(start_date.month) + "_" + str(
    start_date.day) + "/no_surv/"
output_dir_slaughter = "../output/" + str(start_date.year) + "_" + str(start_date.month) + "_" + str(
    start_date.day) + "/slaughter_surv/"
output_dir_farmer_05 = "../output/" + str(start_date.year) + "_" + str(start_date.month) + "_" + str(
    start_date.day) + "/farmer_surv/mort_rate_inc_0.05"
output_dir_farmer_10 = "../output/" + str(start_date.year) + "_" + str(start_date.month) + "_" + str(
    start_date.day) + "/farmer_surv/mort_rate_inc_0.1"
output_dir_farmer_15 = "../output/" + str(start_date.year) + "_" + str(start_date.month) + "_" + str(
    start_date.day) + "/farmer_surv/mort_rate_inc_0.15"
output_dir_net_250_90_d = "../output/" + str(start_date.year) + "_" + str(start_date.month) + "_" + str(
    start_date.day) + "/network_surv/nets_250_90_d"
output_dir_net_250_90_p = "../output/" + str(start_date.year) + "_" + str(start_date.month) + "_" + str(
    start_date.day) + "/network_surv/nets_250_90_p"
output_dir_net_250_90_g = "../output/" + str(start_date.year) + "_" + str(start_date.month) + "_" + str(
    start_date.day) + "/network_surv/nets_250_90_g"
output_dir_net_250_90_t = "../output/" + str(start_date.year) + "_" + str(start_date.month) + "_" + str(
    start_date.day) + "/network_surv/nets_250_90_t"
output_dir_net_250_90_i = "../output/" + str(start_date.year) + "_" + str(start_date.month) + "_" + str(
    start_date.day) + "/network_surv/nets_250_90_i"

# No surveillance - basic plots
# plot_fun.plot_all_basic(output_dir_no,
#                         num_runs
#                         columns_compart,
#                         columns2,
#                         columns3)

# slaughter surveillance - basic plots
# results_transmission_daily_slaughter = plot_fun.plot_all_basic(output_dir_slaughter,
#                                                                num_runs,
#                                                                columns_compart,
#                                                                columns2,
#                                                                columns3)
# farmer surveillance - basic plots
# plot_fun.plot_all_basic(output_dir_farmer,
#                                                             num_runs,
#                                                             columns_compart,
#                                                             columns2,
#                                                             columns3)


# Prepare dataframes for slaughter surveillance
results_all_long_slaughter, results_contact_type_slaughter, results_transmission_daily_slaughter, \
index_farm_df_slaughter, max_farm_count_slaughter, max_inf_count_merge_slaughter = \
    plot_fun.prep_dfs_for_plot(output_dir_slaughter,
                               columns_compart,
                               columns2,
                               columns3)

results_detect_daily_slaughter, results_detect_first_slaughter, combo_df_slaughter = \
    plot_fun_surv.prep_dfs_for_slaughter_plot(output_dir_slaughter, columns4, results_transmission_daily_slaughter)

# Prepare dataframes for farmer surveillance
results_all_long_farmer, results_contact_type_farmer, results_transmission_daily_farmer, \
index_farm_df_farmer, max_farm_count_farmer, max_inf_count_merge_farmer = \
    plot_fun.prep_dfs_for_plot(output_dir_farmer,
                               columns_compart,
                               columns2,
                               columns3)

results_detect_daily_farmer, results_detect_first_farmer, combo_df_farmer = \
    plot_fun_surv.prep_dfs_for_farmer_plot(output_dir_farmer, columns5, results_transmission_daily_farmer)

# Plot Slaughter Surveillance
slaughter_surv_df = plot_fun_surv.plot_slaughter_surv(results_detect_daily_slaughter,
                                                      results_detect_first_slaughter,
                                                      combo_df_slaughter,
                                                      start_date,
                                                      end_date)

# Plot Farmer Surveillance
# plot_fun_surv.plot_farmer_surv(results_detect_daily_farmer,
#                                                       results_detect_first_farmer,
#                                                       combo_df_farmer,
#                                                       start_date,
#                                                       end_date)

plot_fun_surv.plot_compare_surv(combo_df_slaughter, combo_df_farmer,
                                results_detect_first_slaughter, results_detect_first_farmer,
                                start_date, end_date)


