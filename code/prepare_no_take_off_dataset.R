# Prepare datasets for looking only at the scenarios that "took off"
# more than 10 farms with positive cases
rm(list=ls()) 
library(dplyr)

#start_date = "2014_1_1"

load('all_total_compart_data.RData')
load('all_NS_compart_data.RData')


# Find the simulations that have taken off
total_compart_data_take_off <- all_total_compart_data %>% 
  group_by(disease, start_date, surv_pgrm, num_run) %>% 
  mutate(max_farm_count = max(farm_count)) %>% 
  filter(max_farm_count > 10) %>% 
  ungroup()

total_ns_compart_data_take_off <- all_NS_compart_data %>% 
  group_by(disease, start_date, surv_pgrm, num_run) %>% 
  mutate(max_farm_count = max(farm_count)) %>% 
  filter(max_farm_count > 10) %>% 
  ungroup()

#save(total_compart_data_take_off, file='total_compart_data_take_off.RData')

# Save scenarios that have taken off
list_total_compart_take_off <- total_compart_data_take_off %>% 
  select(disease, start_date, surv_pgrm, num_run) %>% 
  distinct()

list_total_ns_compart_take_off <- total_ns_compart_data_take_off %>% 
  select(disease, start_date, surv_pgrm, num_run) %>% 
  distinct()

list_scenarios_take_off <- rbind(list_total_ns_compart_take_off, list_total_compart_take_off)
list_scenarios_take_off <- list_scenarios_take_off %>% distinct()

save(list_scenarios_take_off, file='list_scenarios_take_off.RData')

# select data of run @ point of first detection
total_first_detect_take_off <- total_compart_data_take_off %>% 
    filter(isolated > 0) %>% 
    group_by(disease, surv_pgrm, num_run) %>% 
    arrange(date) %>% 
    filter(row_number()==1) %>%
    ungroup()
  
# if there was no detection for the run, then grab last row
total_first_detect_never_take_off <- total_compart_data_take_off %>% 
    anti_join(total_first_detect_take_off, by = c('disease', 'surv_pgrm', 'num_run')) %>% 
    group_by(disease, surv_pgrm, num_run) %>% 
    slice_max(date) %>%
    ungroup()
  
# join detected and detected_never dataframes
first_detect_all_take_off <- rbind(total_first_detect_take_off, total_first_detect_never_take_off)

#save 
save(first_detect_all_take_off, file='first_detect_all_take_off.RData')

# proportion of true cases found over the total number of cases
total_compart_data_take_off_last_day <- total_compart_data_take_off %>%
  filter(date=="2014-08-31")

# Calculate total cases and total cases detected
total_compart_data_take_off_last_day_cases <- total_compart_data_take_off_last_day %>% 
  mutate(total_cases = exposed + infected + asymptomatic + removed + recovered + isolated + quarantined_a + quarantined_e,
         total_detected = isolated + quarantined_a + quarantined_e,
         prop_detected = total_detected / total_cases)

