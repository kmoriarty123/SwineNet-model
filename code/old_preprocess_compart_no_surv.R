# #############################################################
# ## title: "Preprocess Compartment datasets with Sensitivity of Phi and Psi"
# ## author : Kathleen Moriarty
# ## date_created : 23.05.2022
# ## desc: 
# ## output: all_NS_compart_data  
# #all_NS_compart_data_sum_long
# #all_NS_compart_data_sum_long_phipsi
# 
# #############################################################
# 
# rm(list=ls()) 
# library(dplyr)
# library(tidyr)
# setwd("Z:/Datasets/NetworkMaterial/SwineNet-model/output/")
# 
# ############ results_by_compart_grp_all.txt  ############
# 
# list_disease = c("APP", "ASF", "PRRS")
# list_start_date = c('2014_1_1', '2019_5_1', '2014_5_1', '2019_1_1')
# #list_start_date = c() # for additional exploration with ASF
# #list_disease = c('ASF') # only for additional start dates of ASF
# ########
# 
# # to store datasets
# all_NS_compart_data <- data.frame() 
# all_NS_compart_data_sum_long <- data.frame() 
# all_NS_compart_data_sum_long_phipsi <- data.frame() 
# 
# for (j in 1:(length(list_disease))){
#   for (k in 1:(length(list_start_date))){
#     
#     disease <- list_disease[j]
#     start_date <- list_start_date[k]
#     print(disease)
#     print(start_date)
#     # to find files
#     folder = paste0(disease, '/', start_date, "/no_surv")
#     compart_filename <- '/results_by_compart_all.txt'
#     
#     # to store records
#     no_surv_compart_data <- data.frame()
#     
#     # grab list of results_by_compart_all.txt files
#     list_of_compart_files <- list.files(path = folder, 
#                                         recursive = TRUE,
#                                         pattern = "results_by_compart_all.txt", 
#                                         full.names = TRUE)
#     
#     # Preparing compartment txt files
#     compart_colnames <- c('date', 'farm_count', 
#                           'exposed', 'infected', 'asymptomatic',
#                           'removed', 'recovered', 'isolated',
#                           'quarantined_s', 'quarantined_e','quarantined_a',
#                           'num_run')
#     
#     for (i in 1:(length(list_of_compart_files))){
#       print(i)
#       # read in file
#       tmp_compart_df <- read.table(list_of_compart_files[i], 
#                                    header = FALSE, 
#                                    sep = ",")
#       
#       # set name of surveillance type and phi/psi factors
#       file_name_strings <- stringr::str_split(list_of_compart_files[i], "/")
#       #disease <- file_name_strings[[1]][1]
#       surv_type <- file_name_strings[[1]][3]
#       surv_pgrm_name <- file_name_strings[[1]][4]
#       
#       # set col names
#       colnames(tmp_compart_df) <- compart_colnames
#       
#       # create total quarantined group
#       # create cumulative infected number of pigs
#       tmp_compart_df <- tmp_compart_df %>% 
#         mutate(quarantined = quarantined_s + quarantined_e + quarantined_a,
#                cum_infected = exposed + infected + asymptomatic + removed + recovered + isolated + quarantined_e + quarantined_a,
#                curr_infected = exposed + infected + asymptomatic,
#                date = as.Date(date))
#       
#       # Add distinguishing variables
#       tmp_compart_df$disease <- disease
#       tmp_compart_df$surv_pgrm <- surv_pgrm_name
#       tmp_compart_df$start_date <- as.Date(start_date, "%Y_%m_%d")
#       
#       # create new "day" to difference from start
#       tmp_compart_df <- tmp_compart_df %>% 
#         mutate(day = difftime(date, start_date, units = "days"))
#       
#       # split surv_pgrm by phi_factor and psi_factor
#       tmp_compart_df <- tmp_compart_df %>% 
#         mutate(phi_factor = stringr::str_split(surv_pgrm, "_")[[1]][3],
#                psi_factor = stringr::str_split(surv_pgrm, "_")[[1]][6])
#       
# 
#       no_surv_compart_data <- rbind(tmp_compart_df, no_surv_compart_data)
#       
#     }
#     
#     # save the raw disease + start_date no surveillance data to record
#     save(no_surv_compart_data, file=paste0(disease, '/', start_date, "/no_surv_compart_data.RData"))
#     
#     # median/maximum of data
#     tmp_NS_compart_data_sum <- no_surv_compart_data %>% 
#       group_by(disease, date, start_date, surv_pgrm, phi_factor, psi_factor, day) %>% 
#       summarize(med_farm_count = median(farm_count),
#                 med_infected = median(infected),
#                 med_aysm = median(asymptomatic),
#                 med_curr_infected = median(curr_infected),
#                 med_removed = median(removed),
#                 med_recovered = median(recovered),
#                 med_cum_infected = median(cum_infected),
#                 max_farm_count = max(farm_count),
#                 max_infected = max(infected),
#                 max_aysm = max(asymptomatic),
#                 max_curr_infected = max(curr_infected),
#                 max_cum_infected = max(cum_infected),
#                 max_removed = max(removed),
#                 max_recovered = max(recovered)) %>% 
#       ungroup()
#     
#     # make data long on summary type
#     tmp_NS_compart_data_sum_long <- tmp_NS_compart_data_sum %>% 
#       pivot_longer(med_farm_count:max_recovered)
#     
#     # make data long on phi/psi factor
#     tmp_NS_compart_data_sum_long_phipsi <- tmp_NS_compart_data_sum %>% 
#       pivot_longer(phi_factor:psi_factor)
#     
#     # remove all rows that are not necessary
#     tmp_NS_compart_data_sum_long_phipsi <- tmp_NS_compart_data_sum_long_phipsi %>% 
#       filter(!(surv_pgrm != 'phi_factor_1.0_psi_factor_1.0' & 
#                value == '1.0'))
#     
#     # bind these datasets to all the other datasets
#     all_NS_compart_data <- rbind(no_surv_compart_data, all_NS_compart_data)
#     all_NS_compart_data_sum_long <- rbind(all_NS_compart_data_sum_long, tmp_NS_compart_data_sum_long)
#     all_NS_compart_data_sum_long_phipsi <- rbind(all_NS_compart_data_sum_long_phipsi, tmp_NS_compart_data_sum_long_phipsi)
#     
#   }
# }
# 
# idx_weight_pgrms <- c('phi_factor_1.0_psi_factor_1.0',
#                       'phi_factor_1.0_psi_factor_1.0_idx_case_factor_1',
#                       'phi_factor_1.0_psi_factor_1.0_idx_case_factor_2')
# 
# idx_weight_only <- c('phi_factor_1.0_psi_factor_1.0_idx_case_factor_1',
#                      'phi_factor_1.0_psi_factor_1.0_idx_case_factor_2')
# 
# # Separate the idx weight sensitivity as they will be processed separately
# all_NS_compart_data_idx_w <- all_NS_compart_data %>% 
#   filter(surv_pgrm %in% idx_weight_pgrms)
# 
# all_NS_compart_data_sum_long_idx_w <- all_NS_compart_data_sum_long %>% 
#   filter(surv_pgrm %in% idx_weight_pgrms)
# 
# all_NS_compart_data <- all_NS_compart_data %>% 
#   filter(!surv_pgrm %in% idx_weight_only)
# 
# all_NS_compart_data_sum_long <- all_NS_compart_data_sum_long %>% 
#   filter(!surv_pgrm %in% idx_weight_only)
# 
# # Save all disease, all start_date data to file
# save(all_NS_compart_data, file="all_NS_compart_data.RData")
# save(all_NS_compart_data_sum_long, file="all_NS_compart_data_sum_long.RData")
# save(all_NS_compart_data_sum_long_phipsi, file="all_NS_compart_data_sum_long_phipsi.RData")
# 
# # Save idx_weights
# save(all_NS_compart_data_idx_w, file="all_NS_compart_data_idx_w.RData")
# save(all_NS_compart_data_sum_long_idx_w, file="all_NS_compart_data_sum_long_idx_w.RData")
