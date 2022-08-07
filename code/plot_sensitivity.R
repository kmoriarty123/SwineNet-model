#############################################################
## title: "Plots for the sensitivity of tour parameters AND
##        index case
## author : Kathleen Moriarty
## date_created : 08.04.2022
## desc: 
## output: various summary surveillance plots
#############################################################


# all_total_compart_data %>% 
#   filter(str_detect(surv_pgrm, "limit_tour") | surv_pgrm == 'no_surv') %>%  
#   group_by(disease, start_date, surv_pgrm, date) %>% 
#   summarize(mfc = median(farm_count))
library(ggpubr)
library(dplyr)
library(tidyr)

load('total_compart_data_take_off.RData')

cbPalette <- c(#"#999999", # grey
  "#E69F00", # yellowy orange
  "#CC79A7", # mauve
  "#009E73", # green 
  "#0072B2", # blue
  #"#56B4E9", # sky blue
  #"#F0E442", # yellow
  "#D55E00", # orangey red
  "#000000", 
  "#7570b3" )# purply blue


total_compart_data_take_off_sum <- total_compart_data_take_off %>% 
  filter(start_date == '2019-05-01') %>% 
  mutate(all_inf = exposed + infected + asymptomatic + removed + recovered) %>% 
  group_by(disease, start_date, surv_pgrm, surv_type, days_since_intro) %>% 
  summarize(med_farm_count = median(farm_count),
            quantile_0.95 = quantile(farm_count, 0.95),
            max_farm_count = max(farm_count),
            med_pig_count = median(all_inf),
            quantile_0.95_pig = quantile(all_inf, 0.95),
            max_pig_count = max(all_inf))  %>% 
  ungroup() %>% 
  pivot_longer(med_farm_count:max_pig_count) %>% 
  mutate(name_desc = case_when(name =='med_farm_count' ~ 'Median Farm Count',
                               name =='max_farm_count' ~ 'Maximum Farm Count',
                               name =='quantile_0.95' ~ '95th Percentile',
                               name =='med_pig_count' ~ 'Median Pig Count',
                               name =='max_pig_count' ~ 'Maximum Pig Count',
                               name =='quantile_0.95_pig' ~ '95th Percentile pig', )) %>% 
  mutate(surv_type_desc = case_when(surv_pgrm == 'no_surv' ~ "none", 
                                    surv_pgrm == 'phi_factor_50.0' ~ 'phi',
                                    surv_pgrm == 'phi_factor_100.0' ~ 'phi',
                                    surv_pgrm == 'phi_factor_200.0' ~ 'phi',
                                    surv_pgrm == 'psi_factor_50.0' ~ 'psi',
                                    surv_pgrm == 'psi_factor_100.0' ~ 'psi',
                                    surv_pgrm == 'psi_factor_200.0' ~ 'psi',
                                    surv_pgrm == 'eta_factor_50.0' ~ 'eta',
                                    surv_pgrm == 'eta_factor_100.0' ~ 'eta',
                                    surv_pgrm == 'eta_factor_200.0' ~ 'eta',
                                    surv_pgrm == 'limit_tour_contacts_0.000001' ~ 'tour',
                                    surv_pgrm == 'limit_tour_contacts_0.05' ~ "tour",
                                    surv_pgrm == 'limit_tour_contacts_0.1' ~ "tour",
                                    surv_pgrm == 'limit_tour_contacts_0.5' ~ "tour",
                                    surv_pgrm == 'idx_case_factor_1' ~ "index",
                                    surv_pgrm == 'idx_case_factor_3' ~ "index")) %>% 
  mutate(surv_type_level = case_when(surv_pgrm == 'no_surv' ~ "2", 
                                    surv_pgrm == 'phi_factor_50.0' ~ '50',
                                    surv_pgrm == 'phi_factor_100.0' ~ '100',
                                    surv_pgrm == 'phi_factor_200.0' ~ '200',
                                    surv_pgrm == 'psi_factor_50.0' ~ '50',
                                    surv_pgrm == 'psi_factor_100.0' ~ '100',
                                    surv_pgrm == 'psi_factor_200.0' ~ '200',
                                    surv_pgrm == 'eta_factor_50.0' ~ '50',
                                    surv_pgrm == 'eta_factor_100.0' ~ '100',
                                    surv_pgrm == 'eta_factor_200.0' ~ '200',
                                    surv_pgrm == 'limit_tour_contacts_0.000001' ~ '0.0',
                                    surv_pgrm == 'limit_tour_contacts_0.05' ~ "0.05",
                                    surv_pgrm == 'limit_tour_contacts_0.1' ~ "0.1",
                                    surv_pgrm == 'limit_tour_contacts_0.5' ~ "0.5",
                                    surv_pgrm == 'idx_case_factor_1' ~ "1",
                                    surv_pgrm == 'idx_case_factor_3' ~ "3"))


 
# # plot cum num infected pigs tour parameter sensitivity 
# b1 <- total_compart_data_take_off_sum %>% 
#   filter(name %in% c('med_pig_count'),
#          surv_type_desc %in% c('phi', 'eta', 'psi')) %>% 
#   ggplot(., aes(x=days_since_intro, 
#                 y=value, 
#                 color=factor(surv_type_level, levels = c("50","100","200")))) +
#   geom_point() +
#   theme_bw() +
#   scale_colour_manual(values=cbPalette) +
#   #scale_colour_manual(values=cbPalette) +
#   labs(#title="Median and Maximum Infected Farm Count for No Surveillance", 
#     y='Cumulative Number of Infected Pigs',
#     x="Days Since Introduction",
#     color="Factor Increase") +
#   #facet_wrap(~disease+surv_type_desc, scales = "free_y")
#   facet_grid2(factor(disease, 
#                      levels = c('PRRS','ASF','APP'))~surv_type_desc, scales = "free_y")

#b2 <- total_compart_data_take_off_sum %>%
total_compart_data_take_off_sum %>% 
  filter(name %in% c('med_farm_count'),
         surv_type_desc %in% c('phi', 'eta', 'psi')) %>% 
  ggplot(., aes(x=days_since_intro, 
                y=value, 
                color=factor(surv_type_level, levels = c("50","100","200")))) +
  geom_point() +
  theme_bw() +
  scale_colour_manual(values=cbPalette) +
  #scale_colour_manual(values=cbPalette) +
  labs(#title="Median and Maximum Infected Farm Count for No Surveillance", 
    y='Cumulative Number of Infected Farms',
    x="Days Since Introduction",
    color="Factor Increase") +
  #facet_wrap(~disease+surv_type_desc, scales = "free_y")
  facet_grid2(factor(disease, 
                     levels = c('PRRS','ASF','APP'))~factor(surv_type_desc, 
                             levels = c('phi','psi','eta')), 
              scales = "free_y",
              labeller= label_parsed)

# ggarrange(b1, b2,
#           #align='v', 
#           labels=c('A', 'B'),
#           common.legend = T,
#           legend='right')

#a1 <- total_compart_data_take_off_sum %>%
total_compart_data_take_off_sum %>% 
  filter(name == 'med_farm_count',
         surv_type_desc %in% c('tour'),
         surv_type_level != '0.5') %>% 
  ggplot(., aes(x=days_since_intro, 
                y=value, 
                color=surv_type_level)) +
  geom_point() +
  theme_bw() +
  scale_colour_manual(values=cbPalette) +
  labs(#title="Median and Maximum Infected Farm Count for No Surveillance", 
    y='Cumulative Number of Infected Farms',
    x="Days Since Introduction",
    color="Proportion \n of Tours \n Removed") +
  facet_wrap(~factor(disease, 
                     levels = c('PRRS','ASF','APP')), scales = "free_y")

# values for article
rtmp <- total_compart_data_take_off_sum %>% 
  filter(name == 'med_farm_count',
         surv_type_desc %in% c('tour'),
         surv_type_level != '0.5',
         disease == 'APP',
         days_since_intro >240) 
  
# a2 <- total_compart_data_take_off_sum %>% 
#   filter(name == 'med_pig_count',
#          surv_type_desc %in% c('tour'),
#          surv_type_level != '0.5') %>% 
#   ggplot(., aes(x=days_since_intro, 
#                 y=value, 
#                 color=surv_type_level)) +
#   geom_point() +
#   theme_bw() +
#   scale_colour_manual(values=cbPalette) +
#   labs(#title="Median and Maximum Infected Farm Count for No Surveillance", 
#     y='Cumulative Number of Infected Pigs',
#     x="Days Since Introduction",
#     color="Proportion \n of Tours \n Removed") +
#   facet_wrap(~factor(disease, 
#                      levels = c('PRRS','ASF','APP')), scales = "free_y")

# ggarrange(a1, a2,
#           #align='v', 
#           labels=c('A', 'B'),
#           common.legend = T,
#           legend='right')

####### IDX Case factor ##########

load('total_compart_data_take_off_all_scen.RData')
# We need to look at num_runs that are associated with each simulation run
# Because they will act individually in the worng direction
total_compart_data_take_off_sum_all_scen <- total_compart_data_take_off_all_scen %>% 
  filter(start_date == '2019-05-01') %>% 
  mutate(all_inf = exposed + infected + asymptomatic + removed + recovered) %>% 
  group_by(disease, start_date, surv_pgrm, surv_type, days_since_intro) %>% 
  summarize(med_farm_count = median(farm_count),
            quantile_0.95 = quantile(farm_count, 0.95),
            max_farm_count = max(farm_count),
            med_pig_count = median(all_inf),
            quantile_0.95_pig = quantile(all_inf, 0.95),
            max_pig_count = max(all_inf))  %>% 
  ungroup() %>% 
  pivot_longer(med_farm_count:max_pig_count) %>% 
  mutate(name_desc = case_when(name =='med_farm_count' ~ 'Median Farm Count',
                               name =='max_farm_count' ~ 'Maximum Farm Count',
                               name =='quantile_0.95' ~ '95th Percentile',
                               name =='med_pig_count' ~ 'Median Pig Count',
                               name =='max_pig_count' ~ 'Maximum Pig Count',
                               name =='quantile_0.95_pig' ~ '95th Percentile pig', )) %>% 
  mutate(surv_type_desc = case_when(surv_pgrm == 'no_surv' ~ "none", 
                                    surv_pgrm == 'phi_factor_50.0' ~ 'phi',
                                    surv_pgrm == 'phi_factor_100.0' ~ 'phi',
                                    surv_pgrm == 'phi_factor_200.0' ~ 'phi',
                                    surv_pgrm == 'psi_factor_50.0' ~ 'psi',
                                    surv_pgrm == 'psi_factor_100.0' ~ 'psi',
                                    surv_pgrm == 'psi_factor_200.0' ~ 'psi',
                                    surv_pgrm == 'eta_factor_50.0' ~ 'eta',
                                    surv_pgrm == 'eta_factor_100.0' ~ 'eta',
                                    surv_pgrm == 'eta_factor_200.0' ~ 'eta',
                                    surv_pgrm == 'limit_tour_contacts_0.000001' ~ 'tour',
                                    surv_pgrm == 'limit_tour_contacts_0.05' ~ "tour",
                                    surv_pgrm == 'limit_tour_contacts_0.1' ~ "tour",
                                    surv_pgrm == 'limit_tour_contacts_0.5' ~ "tour",
                                    surv_pgrm == 'idx_case_factor_1' ~ "index",
                                    surv_pgrm == 'idx_case_factor_3' ~ "index")) %>% 
  mutate(surv_type_level = case_when(surv_pgrm == 'no_surv' ~ "2", 
                                     surv_pgrm == 'phi_factor_50.0' ~ '50',
                                     surv_pgrm == 'phi_factor_100.0' ~ '100',
                                     surv_pgrm == 'phi_factor_200.0' ~ '200',
                                     surv_pgrm == 'psi_factor_50.0' ~ '50',
                                     surv_pgrm == 'psi_factor_100.0' ~ '100',
                                     surv_pgrm == 'psi_factor_200.0' ~ '200',
                                     surv_pgrm == 'eta_factor_50.0' ~ '50',
                                     surv_pgrm == 'eta_factor_100.0' ~ '100',
                                     surv_pgrm == 'eta_factor_200.0' ~ '200',
                                     surv_pgrm == 'limit_tour_contacts_0.000001' ~ '0.0',
                                     surv_pgrm == 'limit_tour_contacts_0.05' ~ "0.05",
                                     surv_pgrm == 'limit_tour_contacts_0.1' ~ "0.1",
                                     surv_pgrm == 'limit_tour_contacts_0.5' ~ "0.5",
                                     surv_pgrm == 'idx_case_factor_1' ~ "1",
                                     surv_pgrm == 'idx_case_factor_3' ~ "3"))

c1 <- total_compart_data_take_off_sum_all_scen %>% 
  filter(name == 'med_farm_count',
         surv_type_desc %in% c('index', 'none')) %>% 
  ggplot(., aes(x=days_since_intro, 
                y=value, 
                color=surv_type_level)) +
  geom_point() +
  theme_bw() +
  scale_colour_manual(values=cbPalette) +
  labs(#title="Median and Maximum Infected Farm Count for No Surveillance", 
    y='Cumulative Number of Infected Farms',
    x="Days Since Introduction",
    color="Index Case \n Risk Factor \n Weight") +
  facet_wrap(~factor(disease, 
                     levels = c('PRRS','ASF','APP')), scales = "free_y")

c2 <- total_compart_data_take_off_sum_all_scen %>% 
  filter(name == 'med_pig_count',
         surv_type_desc %in% c('index', 'none')) %>% 
  ggplot(., aes(x=days_since_intro, 
                y=value, 
                color=surv_type_level)) +
  geom_point() +
  theme_bw() +
  scale_colour_manual(values=cbPalette) +
  labs(#title="Median and Maximum Infected Farm Count for No Surveillance", 
    y='Cumulative Number of Infected Pigs',
    x="Days Since Introduction",
    color="Index Case \n Risk Factor \n Weight") +
  facet_wrap(~factor(disease, 
                     levels = c('PRRS','ASF','APP')), scales = "free_y")

ggarrange(c1, c2,
          #align='v', 
          labels=c('A', 'B'),
          common.legend = T,
          legend='right')

############## Should not look at num_run from no_surv for "take off" ####
# c1 <- total_compart_data_take_off_sum %>% 
#   filter(name == 'med_farm_count',
#          surv_type_desc %in% c('index', 'none')) %>% 
#   ggplot(., aes(x=days_since_intro, 
#                 y=value, 
#                 color=surv_type_level)) +
#   geom_point() +
#   theme_bw() +
#   scale_colour_manual(values=cbPalette) +
#   labs(#title="Median and Maximum Infected Farm Count for No Surveillance", 
#     y='Cumulative Number of Infected Farms',
#     x="Days Since Introduction",
#     color="Index Case Weight") +
#   facet_wrap(~disease, scales = "free_y")
# 
# c2 <- total_compart_data_take_off_sum %>% 
#   filter(name == 'med_pig_count',
#          surv_type_desc %in% c('index', 'none')) %>% 
#   ggplot(., aes(x=days_since_intro, 
#                 y=value, 
#                 color=surv_type_level)) +
#   geom_point() +
#   theme_bw() +
#   scale_colour_manual(values=cbPalette) +
#   labs(#title="Median and Maximum Infected Farm Count for No Surveillance", 
#     y='Cumulative Number of Infected Pigs',
#     x="Days Since Introduction",
#     color="Index Case Weight") +
#   facet_wrap(~disease, scales = "free_y")
# 
# ggarrange(c1, c2,
#           #align='v', 
#           labels=c('A', 'B'),
#           common.legend = T,
#           legend='right')
# 
