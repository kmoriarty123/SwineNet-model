# Outdated





#############################################################
# ## title: "Preprocess Contact Dataframes with the Days in Which Infected Cases
# ## were not present and no entry exists
# ## author : Kathleen Moriarty
# ## date_created : 29.05.2022
# ## output: .RData files:
# #total_rows as dummy_simulation_template.RData
# #total_rows_join as as [start_date]_no_surv_contact_filled.RData
# #total_rows_join_cum_sum as [start_date]_no_surv_contact_cum_sum.RData
# #no_surv_contact_prop as [start_date]_no_surv_contact_prop.RData
# #no_surv_contact_prop_lim as [start_date]_no_surv_contact_prop_lim.RData
# #total_NS_contact_sum
# #############################################################
# 
# rm(list=ls()) 
# library(dplyr)
# library(tidyr)
# library(ggplot2)
# library(ggh4x)
# setwd("Z:/Datasets/NetworkMaterial/SwineNet-model/output/")
# 
# # load data
# load("total_contact_data.RData")
# 
# # set initial values
# start_date_lim = '2019-05-01'
# n=244
# list_disease = c('ASF', 'APP', 'PRRS')
# list_surv_pgrm = c('phi_factor_1.0_psi_factor_1.0',
#                    'phi_factor_10.0_psi_factor_1.0',
#                    'phi_factor_0.25_psi_factor_1.0',
#                    'phi_factor_50.0_psi_factor_1.0',
#                    'phi_factor_200.0_psi_factor_1.0',
#                    'phi_factor_1.0_psi_factor_0.25',
#                    'phi_factor_1.0_psi_factor_10.0',
#                    'phi_factor_1.0_psi_factor_50.0',
#                    'phi_factor_1.0_psi_factor_200.0')
# list_contact_type = c('Direct Transfer',
#                       'Direct Truck Share',
#                       'Indirect Truck Share',
#                       'External Truck',
#                       'Geographic',
#                       'Within Farm')
# 
# total_rows = data.frame()
# 
# total_NS_contact_data_lim <- total_NS_contact_data %>% 
#   filter(start_date == start_date_lim,
#          surv_pgrm %in% list_surv_pgrm)
# 
# total_NS_contact_data_lim <- total_NS_contact_data_lim %>% 
#   mutate(day = as.numeric(day)) %>% 
#   select (-c(contact_type, cum_num_inf, start_date, date))
# 
# #total_NS_contact_data <- NULL
# 
# for (i in 1:(length(list_disease))){
#   for (j in 1:(length(list_surv_pgrm))){
#     for (k in 1:(length(list_contact_type))){
#       
#       tmp_df <- data.frame('disease' = list_disease[i],
#                      'surv_pgrm' = list_surv_pgrm[j],
#                      'contact_name' = list_contact_type[k],
#                      'day' = 0:n)
#       
#       rows= c(1:nrow(tmp_df))
#       # repeat rows for each simulation row
#       tmp_df <- tmp_df[rep(rows, 1000),]
#       #create variable for num_run
#       tmp_df <- tmp_df %>% 
#         group_by(day) %>% 
#         mutate(num_run = 1:1000)
#         
#       
#       total_rows = rbind(tmp_df, total_rows)
#     }
#   }
# }
# 
# save(total_rows, file="dummy_simulation_template.RData")
# 
# tmp_df = NULL
# 
# 
# # merge this dataframe with limited contact data
# total_rows_join <- total_NS_contact_data_lim  %>% 
#   full_join(total_rows,
#                          by = c("disease" = "disease",
#                                 "surv_pgrm" = "surv_pgrm",
#                                 "contact_name" = "contact_name",
#                                 "day" = "day",
#                                 "num_run" = "num_run"))
# 
# # Update num_inf_rows to 0 where NA
# total_rows_join <- total_rows_join %>% 
#   mutate(num_inf_pigs = ifelse(is.na(num_inf_pigs), 0, num_inf_pigs))
# 
# save(total_rows_join, file=paste0(start_date_lim, "_no_surv_contact_filled.RData"))
# 
# # Create cumulative values
# total_rows_join_cum <- total_rows_join %>% 
#   group_by(disease, 
#            contact_name, 
#            surv_pgrm, 
#            num_run) %>% 
#   arrange(day) %>% 
#   mutate(cum_num_inf = cumsum(num_inf_pigs)) %>% 
#   ungroup()
# 
# # check some rows
# tmp <- total_rows_join_cum %>% 
#   filter(surv_pgrm == "phi_factor_1.0_psi_factor_200.0",
#          disease == "PRRS",
#          contact_name == "Direct Truck Share")
# 
# # Create median
# total_rows_join_cum_sum <- total_rows_join_cum %>% 
#   group_by(disease, day, surv_pgrm, contact_name) %>% 
#   summarize(med_num_inf_pigs = median(num_inf_pigs),
#             max_num_inf_pigs = max(num_inf_pigs),
#             med_cum_inf = median(cum_num_inf),
#             max_cum_inf = max(cum_num_inf)) %>% 
#   ungroup()
# 
# # split surv_pgrm
# total_rows_join_cum_sum <- total_rows_join_cum_sum %>% 
# mutate(surv_pgrm2 = surv_pgrm) %>% 
#   separate(surv_pgrm2, 
#            into=c("s1","s2","phi_factor","s3", "s4","psi_factor"),
#            sep="_") %>%
#   select(-c(s1, s2, s3, s4))
# 
# save(total_rows_join_cum_sum, file=paste0(start_date_lim, "_no_surv_contact_cum_sum.RData"))
# 
# # For proportions of routes of transmission
# no_surv_contact_prop <- total_rows_join_cum_sum %>% 
#   group_by(disease, day, surv_pgrm) %>% 
#   mutate(daily_total_cum_inf_pigs = sum(med_cum_inf)) %>% 
#   ungroup()
# 
# no_surv_contact_prop <- no_surv_contact_prop %>% 
#   mutate(prop_cum_inf = med_cum_inf/daily_total_cum_inf_pigs,
#          prop_cum_inf = ifelse(is.na(prop_cum_inf), 0, prop_cum_inf))
# 
# list_surv_pgrm2 = c('phi_factor_1.0_psi_factor_1.0', 
#                     'phi_factor_1.0_psi_factor_200.0',
#                     'phi_factor_200.0_psi_factor_1.0')
# 
# no_surv_contact_prop <- no_surv_contact_prop %>%
#   filter(surv_pgrm %in% list_surv_pgrm2) %>%
#   mutate(surv_pgrm_name = case_when(surv_pgrm=='phi_factor_1.0_psi_factor_1.0' ~ 'Phi Factor: 1.0, Psi Factor: 1.0',
#                                     surv_pgrm=='phi_factor_1.0_psi_factor_200.0' ~ 'Phi Factor: 1.0, Psi Factor: 200.0',
#                                     surv_pgrm=='phi_factor_200.0_psi_factor_1.0' ~ 'Phi Factor: 200.0, Psi Factor: 1.0'))
# 
# 
# save(no_surv_contact_prop, file=paste0(start_date_lim, "_no_surv_contact_prop.RData"))
# 
# # EXCLUDE WITHIN FARM data or proportions of routes of transmission
# 
# no_surv_contact_prop_lim <- total_rows_join_cum_sum %>% 
#   filter(contact_name != "Within Farm") %>% 
#   group_by(disease, day, surv_pgrm) %>% 
#   mutate(daily_total_cum_inf_pigs = sum(med_cum_inf)) %>% 
#   ungroup()
#   
# no_surv_contact_prop_lim <- no_surv_contact_prop_lim %>% 
#   mutate(prop_cum_inf = med_cum_inf/daily_total_cum_inf_pigs,
#          prop_cum_inf = ifelse(is.na(prop_cum_inf), 0, prop_cum_inf))
# 
# list_surv_pgrm2 = c('phi_factor_1.0_psi_factor_1.0', 
#                     'phi_factor_1.0_psi_factor_200.0',
#                     'phi_factor_200.0_psi_factor_1.0')
# 
# no_surv_contact_prop_lim <- no_surv_contact_prop_lim %>%
#   filter(surv_pgrm %in% list_surv_pgrm2) %>%
#   mutate(surv_pgrm_name = case_when(surv_pgrm=='phi_factor_1.0_psi_factor_1.0' ~ 'Phi Factor: 1.0, Psi Factor: 1.0',
#                                     surv_pgrm=='phi_factor_1.0_psi_factor_200.0' ~ 'Phi Factor: 1.0, Psi Factor: 200.0',
#                                     surv_pgrm=='phi_factor_200.0_psi_factor_1.0' ~ 'Phi Factor: 200.0, Psi Factor: 1.0'))
# 
# 
# save(no_surv_contact_prop_lim, file=paste0(start_date_lim, "_no_surv_contact_prop_lim.RData"))
# 
# # Looking at sum of all contact type transmissions and num_inf_pigs
# 
# total_NS_contact_sum_num_run <- total_NS_contact_data %>% 
#   filter(num_inf_pigs > 0) %>% 
#   group_by(disease, surv_pgrm, start_date, num_run, contact_type) %>% 
#   summarize(sum_num_inf = sum(num_inf_pigs)) %>% 
#   ungroup()
# 
# total_NS_contact_sum <- total_NS_contact_sum_num_run %>% 
#   group_by(disease, surv_pgrm, start_date, contact_type) %>% 
#   summarize(med_sum_num_inf = median(sum_num_inf)) %>% 
#   ungroup()
# 
# save(total_NS_contact_sum, file='total_NS_contact_sum.RData')
# 
# #####################################################################
# # LIMIT the observations to only hte simulations that took off
# #####################################################################
# 
# total_NS_contact_data_take_off <- total_NS_contact_data %>% 
#   inner_join(list_scenarios_take_off,
#              by=c("disease", 'start_date', 'surv_pgrm', 'num_run'))
# 
# 
# total_NS_contact_sum_num_run_take_off <- total_NS_contact_data_take_off %>% 
#   filter(num_inf_pigs > 0) %>% 
#   group_by(disease, surv_pgrm, start_date, num_run, contact_type) %>% 
#   summarize(sum_num_inf = sum(num_inf_pigs)) %>% 
#   ungroup()
# 
# total_NS_contact_sum_take_off <- total_NS_contact_sum_num_run_take_off %>% 
#   group_by(disease, surv_pgrm, start_date, contact_type) %>% 
#   summarize(med_sum_num_inf = median(sum_num_inf)) %>% 
#   ungroup()
# 
# save(total_NS_contact_sum_take_off, file='total_NS_contact_sum_take_off.RData')
# 
# # AND with total_rows_join
# 
# list_take_off_lim <- list_scenarios_take_off %>% 
#   filter(start_date == start_date_lim) %>% 
#   select(-c(start_date))
# 
# total_rows_join_take_off <- total_rows_join %>% 
#   inner_join(list_take_off_lim,
#              by=c("disease", 'surv_pgrm', 'num_run'))
# 
# # Create cumulative values
# total_rows_join_cum_take_off <- total_rows_join_take_off %>% 
#   group_by(disease, 
#            contact_name, 
#            surv_pgrm, 
#            num_run) %>% 
#   arrange(day) %>% 
#   mutate(cum_num_inf = cumsum(num_inf_pigs)) %>% 
#   ungroup()
# 
# # check some rows
# tmp <- total_rows_join_cum_take_off %>% 
#   filter(surv_pgrm == "phi_factor_1.0_psi_factor_200.0",
#          disease == "PRRS",
#          contact_name == "Direct Truck Share")
# 
# # Create median
# total_rows_join_cum_sum_take_off <- total_rows_join_cum_take_off %>% 
#   group_by(disease, day, surv_pgrm, contact_name) %>% 
#   summarize(med_num_inf_pigs = median(num_inf_pigs),
#             max_num_inf_pigs = max(num_inf_pigs),
#             med_cum_inf = median(cum_num_inf),
#             max_cum_inf = max(cum_num_inf)) %>% 
#   ungroup()
# 
# # split surv_pgrm
# total_rows_join_cum_sum_take_off <- total_rows_join_cum_sum_take_off %>% 
#   mutate(surv_pgrm2 = surv_pgrm) %>% 
#   separate(surv_pgrm2, 
#            into=c("s1","s2","phi_factor","s3", "s4","psi_factor"),
#            sep="_") %>%
#   select(-c(s1, s2, s3, s4))
# 
# save(total_rows_join_cum_sum_take_off, file=paste0(start_date_lim, "_no_surv_contact_cum_sum_take_off.RData"))
# 
# # For proportions of routes of transmission
# no_surv_contact_prop_take_off <- total_rows_join_cum_sum_take_off %>% 
#   group_by(disease, day, surv_pgrm) %>% 
#   mutate(daily_total_cum_inf_pigs = sum(med_cum_inf)) %>% 
#   ungroup()
# 
# no_surv_contact_prop_take_off <- no_surv_contact_prop_take_off %>% 
#   mutate(prop_cum_inf = med_cum_inf/daily_total_cum_inf_pigs,
#          prop_cum_inf = ifelse(is.na(prop_cum_inf), 0, prop_cum_inf))
# 
# no_surv_contact_prop_take_off <- no_surv_contact_prop_take_off %>%
#   filter(surv_pgrm %in% list_surv_pgrm2) %>%
#   mutate(surv_pgrm_name = case_when(surv_pgrm=='phi_factor_1.0_psi_factor_1.0' ~ 'Phi Factor: 1.0, Psi Factor: 1.0',
#                                     surv_pgrm=='phi_factor_1.0_psi_factor_200.0' ~ 'Phi Factor: 1.0, Psi Factor: 200.0',
#                                     surv_pgrm=='phi_factor_200.0_psi_factor_1.0' ~ 'Phi Factor: 200.0, Psi Factor: 1.0'))
# 
# 
# save(no_surv_contact_prop_take_off, file=paste0(start_date_lim, "_no_surv_contact_prop_take_off.RData"))
# 
# # EXCLUDE WITHIN FARM data or proportions of routes of transmission
# 
# no_surv_contact_prop_lim_take_off <- total_rows_join_cum_sum_take_off %>% 
#   filter(contact_name != "Within Farm") %>% 
#   group_by(disease, day, surv_pgrm) %>% 
#   mutate(daily_total_cum_inf_pigs = sum(med_cum_inf)) %>% 
#   ungroup()
# 
# no_surv_contact_prop_lim_take_off <- no_surv_contact_prop_lim_take_off %>% 
#   mutate(prop_cum_inf = med_cum_inf/daily_total_cum_inf_pigs,
#          prop_cum_inf = ifelse(is.na(prop_cum_inf), 0, prop_cum_inf))
# 
# no_surv_contact_prop_lim_take_off <- no_surv_contact_prop_lim_take_off %>%
#   filter(surv_pgrm %in% list_surv_pgrm2) %>%
#   mutate(surv_pgrm_name = case_when(surv_pgrm=='phi_factor_1.0_psi_factor_1.0' ~ 'Phi Factor: 1.0, Psi Factor: 1.0',
#                                     surv_pgrm=='phi_factor_1.0_psi_factor_200.0' ~ 'Phi Factor: 1.0, Psi Factor: 200.0',
#                                     surv_pgrm=='phi_factor_200.0_psi_factor_1.0' ~ 'Phi Factor: 200.0, Psi Factor: 1.0'))
# 
# 
# save(no_surv_contact_prop_lim_take_off, file=paste0(start_date_lim, "_no_surv_contact_prop_lim_take_off.RData"))
