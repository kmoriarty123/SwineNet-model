#############################################################
## title: "Summarize SwineNet Model Output for all diseases"
## author : Kathleen Moriarty
## date_created : 19.05.2022
## desc: Prepare datasets for looking only at the scenarios that "took off"
## 'took off' as defined by more than 10 farms with positive cases
## output: 
#############################################################

rm(list=ls()) 
library(dplyr)

setwd("Z:/Datasets/NetworkMaterial/SwineNet-model/output/")

load('all_total_compart_data.RData')

# Find the simulations that have taken off
total_compart_data_take_off_all_scen <- all_total_compart_data %>% 
  group_by(disease, start_date, surv_pgrm, num_run) %>% 
  mutate(max_farm_count = max(farm_count)) %>% 
  filter(max_farm_count > 10) %>% 
  ungroup()

save(total_compart_data_take_off_all_scen, file='total_compart_data_take_off_all_scen.RData')

# Save scenarios that have taken off
list_scenarios_take_off_all_scen <- total_compart_data_take_off_all_scen %>% 
  select(disease, start_date, surv_pgrm, num_run) %>% 
  distinct()

save(list_scenarios_take_off_all_scen, file='list_scenarios_take_off_all_scen.RData')


# Count of Num runs that have taken off for each surv
take_off_10_runs <- total_compart_data_take_off_all_scen %>% 
  filter(start_date == '2019-05-01') %>% 
  group_by(disease, surv_pgrm, start_date, num_run) %>% 
  count() %>% 
  ungroup()

take_off_10 <- total_compart_data_take_off_all_scen %>% 
  filter(start_date == '2019-05-01') %>% 
  group_by(disease, surv_pgrm, start_date, num_run) %>% 
  count() %>% ungroup() %>% 
  group_by(disease, surv_pgrm, start_date) %>% 
  summarize(n=n()) %>% arrange(disease, surv_pgrm) %>% 
  ungroup()

# Num run that have taken off with no surv
# num_run_take_off_no_surv <- total_compart_data_take_off_all_scen %>% 
#   filter(surv_pgrm == 'no_surv') %>%
#   group_by(disease, start_date) %>% 
#   distinct(num_run) %>% 
#   ungroup()
# 
# save(num_run_take_off_no_surv, file='num_run_take_off_no_surv.RData')


##### 
## Select data of run @ point of first detection
#####

total_first_detect_take_off <- total_compart_data_take_off %>% 
    filter(isolated > 0) %>% 
    group_by(disease, start_date, surv_pgrm, num_run) %>% 
    arrange(date) %>% 
    filter(row_number()==1) %>%
    ungroup()
  
# if there was no detection for the run, then grab last row
total_first_detect_never_take_off <- total_compart_data_take_off %>% 
    anti_join(total_first_detect_take_off, by = c('disease', 'surv_pgrm','start_date', 'num_run')) %>% 
    group_by(disease, start_date, surv_pgrm, num_run) %>% 
    slice_max(date) %>%
    ungroup()
  
# join detected and detected_never dataframes
first_detect_all_take_off <- rbind(total_first_detect_take_off, total_first_detect_never_take_off)

#save 
save(first_detect_all_take_off, file='first_detect_all_take_off.RData')

#####
## Proportion of true cases found over the total number of case
#####

# Grab the group's last day and filter for that
total_compart_data_take_off_last_day <- total_compart_data_take_off %>% 
  group_by(disease, start_date, surv_pgrm, num_run) %>% 
  slice_max(date) %>% 
  mutate(last_day = date) %>% 
  ungroup() %>% 
  filter(date==last_day)

# Calculate total cases and total cases detected
total_compart_data_take_off_last_day_cases <- total_compart_data_take_off_last_day %>% 
  mutate(total_cases = exposed + infected + asymptomatic + removed + recovered + isolated + quarantined_a + quarantined_e,
         total_detected = isolated + quarantined_a + quarantined_e,
         prop_detected = total_detected / total_cases)

save(total_compart_data_take_off_last_day_cases, file = "total_compart_data_take_off_last_day_cases.RData")
