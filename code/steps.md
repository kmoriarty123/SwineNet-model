## Preprocessing files

Compartment Files

1. summarize_data_per_disease.R

- all_compart_data, all_compartment.RData
- all_compart_data_sum, all_compart_data_sum.RData
- all_first_detect, all_first_detect.RData
- all_outbreak_data, all_outbreak_data.RData

2. summarize_data_all_diseases.R

- all_total_compart_data, all_total_compart_data.RData
- all_total_first_detect, all_total_first_detect.RData
- all_total_outbreak_data, all_total_outbreak_data.RData

3. prepare_only_take_off_dataset_NEW and prepare_only_take_off_dataset

prepare_only_take_off_dataset_NEW:
The NEW file is because I create a list of num_runs from the no_surv scenario to use as a list of scenarios for the other surveillance programs when focusing on "take-off" only

- list_scenarios_take_off, list_scenarios_take_off.RData
all scenarios that took off

- first_detect_all_take_off, first_detect_all_take_off.RData

- total_compart_data_take_off_last_day_cases, total_compart_data_take_off_last_day_cases.RData

prepare_only_take_off_dataset:
I still need this data for the index case sensitivity analysis


Contact Files

1. prepare_contact_grp

- contact_data, paste0(disease, '/', start_date, "/contact_data.RData")
contact data for each disease +start_date

- all_total_contact_data, total_contact_data.RData
all disease, all start_dates

- all_total_contact_data_sum, all_total_contact_data_sum.RData
summary of above

- total_rows, dummy_simulation_template.RData
mock dataframe with all possible scenarios and runs

- total_rows_join, paste0(start_date_lim, contact_data_filled.RData
mock joined with all contact group to fill missing dates

- total_rows_join_cum_sum, paste0(start_date_lim, contact_data_cum_sum.RData
summary of above

- contact_data_prop, paste0(start_date_lim, contact_data_prop.RData
proportion excluding within farm contact group

- total_rows_join_take_off_cum_sum, paste0(start_date_lim, contact_take_off_cum_sum.RData

- contact_prop_take_off, paste0(start_date_lim, contact_prop_take_off.RData
proportion per contact group with only runs that takes off

- contact_prop_take_off_lim, paste0(start_date_lim, contact_prop_lim_take_off.RData
proportion excluding within farm contact group with only runs that takes off


## Plots

1. plot_overall_no_surveillance
- median, max, 95th % of cum infected farms for all simulations and limited to those that took off
cum_farm_count_with_all_and_only_take_off.png

2. plot_seasonality
- compart_grp_season_prop_take_off.png
proportion of runs that took off

- seasonal_cum_sum.png

3. plot_contact_types

- contact_grp_prop_takeoff_baseline.png
baseline
- the other contact grp takeoff with sens ana of tour params
- tour_reduce_prop.png 
limit tours

4. plot_surveillance
- first detect
- proportion detected

5. plot_sensitivity

- compart_phi_psi_eta_cum_sum.png
- compart_tours_removed_cum_sum.png
- compart_idx_weight_cum_sum.png

example of obtaining values for paper:
load('total_compart_data_take_off_sum.RData')
total_compart_data_take_off_sum %>% 
filter(name %in% c('med_pig_count','med_farm_count'), disease=='ASF', 
days_since_intro == 55,
surv_type =='slaughter_surv')

5. Comparison of slaughterhouse selection (random vs largest)

code: compare_slaughterhouse_choice.R
input: 
load('first_detect_all_take_off.RData') # largest slaughterhouses
load("total_compart_data_take_off_random_slaugher.RData") # randomly drawn slaughterhouses
output: random_largest_sl_choice.png

6. statistical testing of seasonality and tour reductions
stats_test_seasonality_tour_reduce.R
input:
output: cum_prob_seasonality.png