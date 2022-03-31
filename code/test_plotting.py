import datetime
import plotly.express as px
import pandas as pd
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
    start_date.day) + "/farmer_surv/mort_rate_inc_0.05/"
output_dir_farmer_10 = "../output/" + str(start_date.year) + "_" + str(start_date.month) + "_" + str(
    start_date.day) + "/farmer_surv/mort_rate_inc_0.1/"
output_dir_farmer_15 = "../output/" + str(start_date.year) + "_" + str(start_date.month) + "_" + str(
    start_date.day) + "/farmer_surv/mort_rate_inc_0.15/"
output_dir_net_250_90_d = "../output/" + str(start_date.year) + "_" + str(start_date.month) + "_" + str(
    start_date.day) + "/network_surv/nets_250_90_d/"
output_dir_net_250_90_p = "../output/" + str(start_date.year) + "_" + str(start_date.month) + "_" + str(
    start_date.day) + "/network_surv/nets_250_90_p/"
output_dir_net_250_90_g = "../output/" + str(start_date.year) + "_" + str(start_date.month) + "_" + str(
    start_date.day) + "/network_surv/nets_250_90_g/"
output_dir_net_250_90_t = "../output/" + str(start_date.year) + "_" + str(start_date.month) + "_" + str(
    start_date.day) + "/network_surv/nets_250_90_t/"
output_dir_net_250_90_i = "../output/" + str(start_date.year) + "_" + str(start_date.month) + "_" + str(
    start_date.day) + "/network_surv/nets_250_90_i/"

# Summarise the compartment information to obtain mean and std values from all simulation runs
net_250_90_d_sum, net_250_90_d_max_farm  = plot_fun_surv.summarize_results_comp(output_dir_net_250_90_d,
                                                        columns_compart)
net_250_90_g_sum, net_250_90_g_max_farm = plot_fun_surv.summarize_results_comp(output_dir_net_250_90_g,
                                                        columns_compart)
net_250_90_t_sum, net_250_90_t_max_farm = plot_fun_surv.summarize_results_comp(output_dir_net_250_90_t,
                                                        columns_compart)
net_250_90_p_sum, net_250_90_p_max_farm = plot_fun_surv.summarize_results_comp(output_dir_net_250_90_p,
                                                        columns_compart)
net_250_90_i_sum, net_250_90_i_max_farm = plot_fun_surv.summarize_results_comp(output_dir_net_250_90_i,
                                                        columns_compart)
farmer_05_sum, farmer_05_max_farm = plot_fun_surv.summarize_results_comp(output_dir_farmer_05,
                                                        columns_compart)
farmer_10_sum, farmer_10_max_farm= plot_fun_surv.summarize_results_comp(output_dir_farmer_10,
                                                        columns_compart)
farmer_15_sum, farmer_15_max_farm = plot_fun_surv.summarize_results_comp(output_dir_farmer_15,
                                                        columns_compart)
slaughter_sum, slaughter_max_farm = plot_fun_surv.summarize_results_comp(output_dir_slaughter,
                                                        columns_compart)
no_sum, no_max_farm = plot_fun_surv.summarize_results_comp(output_dir_no,
                                                        columns_compart)

sum_all = pd.concat([net_250_90_p_sum, net_250_90_t_sum, net_250_90_g_sum, net_250_90_d_sum, net_250_90_i_sum,
                    farmer_15_sum, farmer_05_sum, farmer_10_sum, slaughter_sum, no_sum])
sum_max = pd.concat([net_250_90_p_max_farm, net_250_90_t_max_farm, net_250_90_g_max_farm, net_250_90_d_max_farm, net_250_90_i_max_farm,
                    farmer_15_max_farm, farmer_05_max_farm, farmer_10_max_farm, slaughter_max_farm, no_max_farm])

# Plot all the summary of mean and std of infected, deceased, farm_count
fig_mean_farm_count = px.line(sum_all,
                               x='date',
                               y='farm_inf_mean',
                               color='s_type',
                               template="plotly_white",
                               #error_y='farm_inf_std',
                               labels={'x': 'Date', 'y': 'Mean Number of Infected Farms'},
                               title="Compare Mean Infected Farms among Surveillance Programs")

fig_mean_inf_pig = px.line(sum_all,
                               x='date',
                               y='infected_mean',
                               color='s_type',
                               template="plotly_white",
                               #error_y='infected_std',
                               labels={'x': 'Date', 'y': 'Mean Number of Infected Pigs'},
                               title="Compare Daily Mean Infected Pigs among Surveillance Programs")

fig_mean_dec_pig = px.line(sum_all,
                               x='date',
                               y='deceased_mean',
                               color='s_type',
                               template="plotly_white",
                               #error_y='infected_std',
                               labels={'x': 'Date', 'y': 'Mean Number of Deceased Pigs'},
                               title="Compare Daily Mean Deceased Pigs among Surveillance Programs")

fig_mean_det_pig = px.line(sum_all,
                               x='date',
                               y='detected_mean',
                               color='s_type',
                               template="plotly_white",
                               #error_y='infected_std',
                               labels={'x': 'Date', 'y': 'Mean Number of Detected Pigs'},
                               title="Compare Daily Mean Detected Pigs among Surveillance Programs")
fig_mean_farm_count.show()
fig_mean_inf_pig.show()
fig_mean_det_pig.show()

##################### plot for date of first detection and cumulative number of pigs #####################
fig_max_farm_count = px.line(sum_max,
                               x='date',
                               y='max_farm_count',
                               color='s_type',
                               template="plotly_white",
                               #error_y='infected_std',
                               labels={'x': 'Date', 'y': 'Max Number of Infected Farm'},
                               title="Max Number of Infected Farm")
fig_max_farm_count.show()

##################### plot for date of first detection and how many cumulative pigs were already infected #####################
fig_max_farm_count = px.line(sum_max,
                               x='date',
                               y='max_farm_count',
                               color='s_type',
                               template="plotly_white",
                               #error_y='infected_std',
                               labels={'x': 'Date', 'y': 'Max Number of Infected Farm'},
                               title="Max Number of Infected Farm")
fig_max_farm_count.show()

