#############################################################
## title: "Plot Contact Model data"
## author : Kathleen Moriarty
## date_created : 23.05.2022
## desc: 
## output: various summary plots
#############################################################
rm(list=ls()) 

library(ggplot2)
library(ggh4x)
library(viridis)
library(dplyr)
# To combine plots
library(ggpubr)

setwd("Z:/Datasets/NetworkMaterial/SwineNet-model/output/")

####### Plot contact_data #######

cbPalette2 <- c(#"#999999", # grey
  "#56B4E9", # green
  "#F0E442", # yellow
  "#E69F00", # pink 
  "#CC79A7", # light blue
  "#009E73", # orange
  "#0072B2", # blue
  "#D55E00", # orangey red
  "#000000", 
  "#7570b3" )# purply blue

surv_level = c('50.0',
               '100.0',
               '200.0')

contact_name_level = c('Direct Transfer',
                       'Direct Truck Share',
                       'Indirect Truck Share',
                       'External Truck',
                       'Geographic',
                       'Within Farm')

rate_factor_level = c("All Tours (+++)",
                      "-10% Tours (+++)",
                      "Baseline")
rate_factor_level_direct = c("+ Direct","++ Direct", "+++ Direct")
rate_factor_level_indirect = c("+ Indirect","++ Indirect", "+++ Indirect")
rate_factor_level_ext = c("+ Exterior","++ Exterior", "+++ Exterior")

tour_factor_level = c("All Tours (+++)", 
                      '-5% Tours (+++)', 
                      '-10% Tours (+++)')

# Plotting Proportion of spread per route of transmission from those that "took off"
load("2019-05-01contact_prop_take_off.RData")

contact_prop_take_off <- contact_prop_take_off %>% 
  mutate(surv_pgrm_name_desc = case_when(surv_pgrm == 'no_surv' ~ "Baseline", 
                                         surv_pgrm == 'phi_factor_50.0' ~ "+ Direct",
                                         surv_pgrm == 'phi_factor_100.0' ~ "++ Direct",
                                         surv_pgrm == 'phi_factor_200.0' ~ "+++ Direct",
                                         surv_pgrm == 'psi_factor_50.0' ~ "+ Indirect",
                                         surv_pgrm == 'psi_factor_100.0' ~ "++ Indirect",
                                         surv_pgrm == 'psi_factor_200.0' ~ "+++ Indirect",
                                         surv_pgrm == 'eta_factor_50.0' ~ "+ Exterior",
                                         surv_pgrm == 'eta_factor_100.0' ~ "++ Exterior",
                                         surv_pgrm == 'eta_factor_200.0' ~ "+++ Exterior",
                                         surv_pgrm == 'limit_tour_contacts_0.000001' ~ "All Tours (+++)",
                                         surv_pgrm == 'limit_tour_contacts_0.05' ~ "-5% Tours (+++)",
                                         surv_pgrm == 'limit_tour_contacts_0.1' ~ "-10% Tours (+++)",
                                         surv_pgrm == 'limit_tour_contacts_0.5' ~ "-50% Tours (+++)"))
          
# Baseline
t0 <- contact_prop_take_off %>% 
  filter(surv_pgrm %in% c('no_surv')) %>% 
  ggplot(., aes(x=day, y=prop_cum_inf, 
                fill=factor(contact_name, levels = contact_name_level))) +
  geom_col() +
  theme_bw() +
  labs(fill="Transmission Route",
       x="Days Since Introduction",
       y="Proportion") +
  scale_fill_manual(values=cbPalette2) +
  facet_grid2(factor(disease, 
                     levels = c('PRRS','ASF','APP'))~factor(surv_pgrm_name_desc, levels=rate_factor_level))

# Baseline with added plot for combining with below sensitivity analysis
#t1 <- contact_prop_take_off_test %>%
t1 <- contact_prop_take_off %>% 
  filter(surv_pgrm %in% c('no_surv',
                          'limit_tour_contacts_0.1')) %>% 
  ggplot(., aes(x=day, y=prop_cum_inf, 
                fill=factor(contact_name, levels = contact_name_level))) +
  geom_col() +
  theme_bw() +
  labs(fill="Transmission Route",
       x="Days Since Introduction",
       y="Proportion") +
  scale_fill_manual(values=cbPalette2) +
  facet_grid2(factor(disease, 
                     levels = c('PRRS','ASF','APP'))~factor(surv_pgrm_name_desc, levels=rate_factor_level))

# Factor of 50
#t1 <- contact_prop_take_off_test %>%
t2 <- contact_prop_take_off %>% 
  filter(surv_pgrm %in% c('phi_factor_50.0',
                          'phi_factor_100.0')) %>% 
                          #'phi_factor_200.0')) %>% 
  ggplot(., aes(x=day, y=prop_cum_inf, 
                fill=factor(contact_name, levels = contact_name_level))) +
  geom_col() +
  theme_bw() +
  labs(fill="Transmission Route",
       x="Days Since Introduction",
       y="Proportion") +
  scale_fill_manual(values=cbPalette2) +
  facet_grid2(factor(disease, 
                     levels = c('PRRS','ASF','APP'))~factor(surv_pgrm_name_desc, levels=rate_factor_level_direct))

# Factor of 100
#t1 <- contact_prop_take_off_test %>%
t3 <- contact_prop_take_off %>% 
  filter(surv_pgrm %in% c('psi_factor_50.0',
                          'psi_factor_100.0')) %>% 
                          #'psi_factor_200.0')) %>% 
  ggplot(., aes(x=day, y=prop_cum_inf, 
                fill=factor(contact_name, levels = contact_name_level))) +
  geom_col() +
  theme_bw() +
  labs(fill="Transmission Route",
       x="Days Since Introduction",
       y="Proportion") +
  scale_fill_manual(values=cbPalette2) +
  facet_grid2(factor(disease, 
                     levels = c('PRRS','ASF','APP'))~factor(surv_pgrm_name_desc, levels=rate_factor_level_indirect))

# Factor of 200
#t1 <- contact_prop_take_off_test %>%
t4 <- contact_prop_take_off %>% 
  filter(surv_pgrm %in% c('eta_factor_50.0',
                          'eta_factor_100.0')) %>% 
                          #'eta_factor_200.0')) %>% 
  ggplot(., aes(x=day, y=prop_cum_inf, 
                fill=factor(contact_name, levels = contact_name_level))) +
  geom_col() +
  theme_bw() +
  labs(fill="Transmission Route",
       x="Days Since Introduction",
       y="Proportion") +
  scale_fill_manual(values=cbPalette2) +
  facet_grid2(factor(disease, 
                     levels = c('PRRS','ASF','APP'))~factor(surv_pgrm_name_desc, levels=rate_factor_level_ext))


ggarrange(t1,t2,t3,t4,
          #align='v', 
          labels=c('A', 'B', 'C','D'),
          common.legend = T,
          legend='right')

# for article values
tmp <- contact_prop_take_off %>% 
  filter(day==244,
         contact_name == 'Within Farm')

tmp2 <- contact_prop_take_off_lim %>% 
  filter(day==244,
         #contact_name == 'Within Farm',
         surv_pgrm_name_desc == 'Baseline') %>% 
  select(disease, contact_name, prop_cum_inf)

tmp3 <- contact_prop_take_off_lim %>% 
  filter(#day==244,
         #contact_name == 'Within Farm',
         #surv_pgrm_name_desc == 'Baseline') %>% 
         disease == 'APP',
         surv_pgrm == 'psi_factor_100.0',
         contact_name == 'Indirect Truck Share'
  ) %>% 
  select(disease, surv_pgrm, day, contact_name, prop_cum_inf)

#### Plotting Proportion of spread per route of transmission WITHOUT WITHIN FARM from those that "took off"
load("2019-05-01contact_prop_lim_take_off.RData") #contact_prop_take_off_lim

contact_prop_take_off_lim <- contact_prop_take_off_lim %>% 
  mutate(surv_pgrm_name_desc = case_when(surv_pgrm == 'no_surv' ~ "Baseline", 
                                         surv_pgrm == 'phi_factor_50.0' ~ "+ Direct",
                                         surv_pgrm == 'phi_factor_100.0' ~ "++ Direct",
                                         surv_pgrm == 'phi_factor_200.0' ~ "+++ Direct",
                                         surv_pgrm == 'psi_factor_50.0' ~ "+ Indirect",
                                         surv_pgrm == 'psi_factor_100.0' ~ "++ Indirect",
                                         surv_pgrm == 'psi_factor_200.0' ~ "+++ Indirect",
                                         surv_pgrm == 'eta_factor_50.0' ~ "+ Exterior",
                                         surv_pgrm == 'eta_factor_100.0' ~ "++ Exterior",
                                         surv_pgrm == 'eta_factor_200.0' ~ "+++ Exterior",
                                         surv_pgrm == 'limit_tour_contacts_0.000001' ~ "All Tours (+++)",
                                         surv_pgrm == 'limit_tour_contacts_0.05' ~ "-5% Tours (+++)",
                                         surv_pgrm == 'limit_tour_contacts_0.1' ~ "-10% Tours (+++)",
                                         surv_pgrm == 'limit_tour_contacts_0.5' ~ "-50% Tours (+++)"))

# Baseline
g0 <- contact_prop_take_off_lim %>% 
  filter(surv_pgrm %in% c('no_surv')) %>% 
  #'limit_tour_contacts_0.1')) %>% 
  ggplot(., aes(x=day, y=prop_cum_inf, 
                fill=factor(contact_name, levels = contact_name_level))) +
  geom_col() +
  theme_bw() +
  labs(fill="Transmission Route",
       x="Days Since Introduction",
       y="Proportion") +
  scale_fill_manual(values=cbPalette2) +
  facet_grid2(factor(disease, 
                     levels = c('PRRS','ASF','APP'))~factor(surv_pgrm_name_desc, levels=rate_factor_level))

# Baseline with added plot for combining with below sensitivity analysis
g1 <- contact_prop_take_off_lim %>% 
  filter(surv_pgrm %in% c('no_surv', 
                          'limit_tour_contacts_0.000001')) %>% 
                          #'limit_tour_contacts_0.1')) %>% 
  ggplot(., aes(x=day, y=prop_cum_inf, 
                fill=factor(contact_name, levels = contact_name_level))) +
  geom_col() +
  theme_bw() +
  labs(fill="Transmission Route",
       x="Days Since Introduction",
       y="Proportion") +
  scale_fill_manual(values=cbPalette2) +
  facet_grid2(factor(disease, 
                     levels = c('PRRS','ASF','APP'))~factor(surv_pgrm_name_desc, levels=rate_factor_level))

# Phi factor increase
g2 <- contact_prop_take_off_lim %>% 
  filter(surv_pgrm %in% c('phi_factor_50.0', 
                          'phi_factor_100.0')) %>% 
                          #'phi_factor_200.0')) %>% 
  ggplot(., aes(x=day, y=prop_cum_inf, 
                fill=factor(contact_name, levels = contact_name_level))) +
  geom_col() +
  theme_bw() +
  labs(fill="Transmission Route",
       x="Days Since Introduction",
       y="Proportion") +
  scale_fill_manual(values=cbPalette2) +
  facet_grid2(factor(disease, 
                     levels = c('PRRS','ASF','APP'))~factor(surv_pgrm_name_desc, levels=rate_factor_level_direct))

# Psi Factor increases
g3 <- contact_prop_take_off_lim %>% 
  filter(surv_pgrm %in% c('psi_factor_50.0', 
                          'psi_factor_100.0')) %>% 
                          ##'psi_factor_200.0')) %>% 
  ggplot(., aes(x=day, y=prop_cum_inf, 
                fill=factor(contact_name, levels = contact_name_level))) +
  geom_col() +
  theme_bw() +
  labs(fill="Transmission Route",
       x="Days Since Introduction",
       y="Proportion") +
  scale_fill_manual(values=cbPalette2) +
  facet_grid2(factor(disease, 
                     levels = c('PRRS','ASF','APP'))~factor(surv_pgrm_name_desc, levels=rate_factor_level_indirect))

# Eta Factor increases
g4 <- contact_prop_take_off_lim %>% 
  filter(surv_pgrm %in% c('eta_factor_50.0', 
                          'eta_factor_100.0')) %>% 
                          ##'eta_factor_200.0')) %>% 
  ggplot(., aes(x=day, y=prop_cum_inf, 
                fill=factor(contact_name, levels = contact_name_level))) +
  geom_col() +
  theme_bw() +
  labs(fill="Transmission Route",
       x="Days Since Introduction",
       y="Proportion") +
  scale_fill_manual(values=cbPalette2) +
  facet_grid2(factor(disease, 
                     levels = c('PRRS','ASF','APP'))~factor(surv_pgrm_name_desc, levels=rate_factor_level_ext))

ggarrange(g1,g2,g3,g4,
          #align='v', 
          labels=c('A', 'B', 'C','D'),
          common.legend = T,
          legend='right')

# for just baselines
ggarrange(t0,g0,
          #align='v', 
          labels=c('A', 'B'),
          common.legend = T,
          legend='right')

# for article values
tmpg1 <- contact_prop_take_off_lim %>% 
  filter(#day==244,
         disease == 'ASF',
         surv_pgrm == 'no_surv',
         contact_name == 'Geographic') %>% 
  select(day, prop_cum_inf)

#############################
## Now look at the limiting of tours
#############################
load('2019-05-01contact_data_prop.RData')
contact_data_prop <- contact_data_prop %>% 
mutate(surv_pgrm_name_desc = case_when(surv_pgrm == 'no_surv' ~ "Baseline", 
                                       surv_pgrm == 'phi_factor_50.0' ~ "+ Direct",
                                       surv_pgrm == 'phi_factor_100.0' ~ "++ Direct",
                                       surv_pgrm == 'phi_factor_200.0' ~ "+++ Direct",
                                       surv_pgrm == 'psi_factor_50.0' ~ "+ Indirect",
                                       surv_pgrm == 'psi_factor_100.0' ~ "++ Indirect",
                                       surv_pgrm == 'psi_factor_200.0' ~ "+++ Indirect",
                                       surv_pgrm == 'eta_factor_50.0' ~ "+ Exterior",
                                       surv_pgrm == 'eta_factor_100.0' ~ "++ Exterior",
                                       surv_pgrm == 'eta_factor_200.0' ~ "+++ Exterior",
                                       surv_pgrm == 'limit_tour_contacts_0.000001' ~ "All Tours (+++)",
                                       surv_pgrm == 'limit_tour_contacts_0.05' ~ "-5% Tours (+++)",
                                       surv_pgrm == 'limit_tour_contacts_0.1' ~ "-10% Tours (+++)",
                                       surv_pgrm == 'limit_tour_contacts_0.5' ~ "-50% Tours (+++)"))

# limit tours - all sims
contact_data_prop %>% 
  filter(surv_pgrm %in% c('limit_tour_contacts_0.000001',
                          'limit_tour_contacts_0.05',
                          'limit_tour_contacts_0.1')) %>% 
  mutate(surv_pgrm = ifelse(surv_pgrm =='limit_tour_contacts_0.000001',
                            'limit_tour_contacts_0.0',
                            surv_pgrm)) %>% 
  ggplot(., aes(x=day, y=prop_cum_inf, 
                fill=factor(contact_name, levels = contact_name_level))) +
  geom_col() +
  theme_bw() +
  labs(fill="Transmission Route",
       x="Days Since Introduction",
       y="Proportion") +
  scale_fill_manual(values=cbPalette2) +
  #facet_grid2(disease~factor(surv_pgrm))#_name_desc))#, levels=tour_factor_level))
  facet_grid2(factor(disease, 
                     levels = c('PRRS','ASF','APP'))~factor(surv_pgrm_name_desc, levels=tour_factor_level))

# limit tours - only take off
contact_prop_take_off %>% 
  filter(surv_pgrm %in% c('limit_tour_contacts_0.000001',
                          'limit_tour_contacts_0.05',
                          'limit_tour_contacts_0.1')) %>% 
  mutate(surv_pgrm = ifelse(surv_pgrm=='limit_tour_contacts_0.000001',
                            'limit_tour_contacts_0.0',
                            surv_pgrm)) %>%
  ggplot(., aes(x=day, y=prop_cum_inf, 
                fill=factor(contact_name, levels = contact_name_level))) +
  geom_col() +
  theme_bw() +
  labs(fill="Transmission Route",
       x="Days Since Introduction",
       y="Proportion") +
  scale_fill_manual(values=cbPalette2) +
  facet_grid2(factor(disease, 
                     levels = c('PRRS','ASF','APP'))~factor(surv_pgrm_name_desc, levels=tour_factor_level))

load('2019-05-01contact_data_prop.RData')

# limit tours - only take off no within farm
contact_prop_take_off_lim %>% 
  filter(surv_pgrm %in% c('limit_tour_contacts_0.000001',
                          'limit_tour_contacts_0.05',
                          'limit_tour_contacts_0.1')) %>% 
  mutate(surv_pgrm = ifelse(surv_pgrm=='limit_tour_contacts_0.000001',
                            'limit_tour_contacts_0.0',
                            surv_pgrm)) %>% 
  ggplot(., aes(x=day, y=prop_cum_inf, 
                fill=factor(contact_name, levels = contact_name_level))) +
  geom_col() +
  theme_bw() +
  labs(fill="Transmission Route",
       x="Days Since Introduction",
       y="Proportion") +
  scale_fill_manual(values=cbPalette2) +
  facet_grid2(factor(disease, 
                     levels = c('PRRS','ASF','APP'))~factor(surv_pgrm_name_desc, levels=tour_factor_level))


# for article values

tmpt1 <- contact_prop_take_off %>% 
  filter(surv_pgrm %in% c('limit_tour_contacts_0.000001',
                          'limit_tour_contacts_0.05',
                           'limit_tour_contacts_0.1')) %>% 
  mutate(surv_pgrm = ifelse(surv_pgrm =='limit_tour_contacts_0.000001',
                                'limit_tour_contacts_0.0',
                                surv_pgrm)) %>% 
  filter(disease== 'ASF',
         day == 244) %>% 
  select(surv_pgrm, contact_name, prop_cum_inf)

# contact_prop_take_off_lim %>% 
#   filter(surv_pgrm %in% c('limit_tour_contacts_0.000001',
#                           'limit_tour_contacts_0.05',
#                           'limit_tour_contacts_0.1')) %>% 
#   mutate(surv_pgrm = ifelse(surv_pgrm=='limit_tour_contacts_0.000001',
#                             'limit_tour_contacts_0.0',
#                             surv_pgrm)) %>% 
#   ggplot(., aes(x=day, y=prop_cum_inf, 
#                 fill=factor(surv_pgrm))) +
#   geom_col(position = "identity", alpha=.3) +
#   theme_bw() +
#   labs(fill="Transmission Route",
#        x="Days Since Introduction",
#        y="Proportion") +
#   #scale_fill_manual(values=cbPalette2) +
#   facet_grid2(disease~factor(contact_name, levels = contact_name_level))
# 


################ OLD CODE ############################

# ### load data
# load('2019-05-01_no_surv_contact_cum_sum.RData') #total_rows_join_cum_sum
# load('all_NS_compart_data_sum_long_phipsi.RData')
# load('2019-05-01_no_surv_contact_prop.RData')
# load('2019-05-01_no_surv_contact_prop_lim.RData')
# load("total_NS_contact_sum.RData")
# load("total_NS_contact_sum_take_off.RData")

# Adjust Psi - Median Cum Infected

# # filter plot for only truck transmission and psi factors
# total_rows_join_cum_sum %>% 
#   filter(contact_name %in% c('Direct Truck Share',
#                              'Indirect Truck Share',
#                              'External Truck',
#                              'Geographic'),
#          phi_factor == '1.0',
#          psi_factor %in% c('0.25','1.0','10.0','50.0','200.0')) %>% 
#   ggplot(., 
#          aes(x=as.numeric(day), 
#              y=med_cum_inf, 
#              color=factor(psi_factor, levels = surv_level))) +
#   geom_point()+
#   labs(title="Median Cumulative Sum of Infected Pigs by Mode of Truck Transmission",
#        subtitle = "Adjusting Psi Parameter (start date: 2019-05-01)",
#        color="Factor of Psi",
#        x="Days Since Introduction",
#        y="Cumulative Infected Pigs") +
#   theme_bw() +
#   scale_colour_manual(values=cbPalette) +
#   facet_grid2(disease~contact_name, 
#               scales="free_y",
#               independent='y')
# 
# # Adjust Phi - Median Cum Infected
# 
# total_rows_join_cum_sum %>% 
#   filter(contact_name %in% c('Direct Truck Share',
#                              'Indirect Truck Share',
#                              'External Truck',
#                              'Geographic'),
#          #disease == 'ASF',
#          #day < 100,
#          #start_date=='2019-05-01',
#          psi_factor == '1.0',
#          phi_factor %in% c('0.25','1.0','10.0','50.0','200.0')) %>% 
#   ggplot(., 
#          aes(x=as.numeric(day), 
#              y=med_cum_inf, 
#              color=factor(phi_factor, levels = surv_level))) +
#   geom_point()+
#   labs(title="Median Cumulative Sum of Infected Pigs by Mode of Truck Transmission",
#        subtitle = "Adjusting Phi Parameter (start date: 2019-05-01)",
#        color="Factor of Phi",
#        x="Days Since Introduction",
#        y="Cumulative Infected Pigs") +
#   theme_bw() +
#   #theme(axis.text.x = element_text(angle = 90, vjust = 0.5, hjust=1)) +
#   scale_colour_manual(values=cbPalette) +
#   facet_grid2(disease~contact_name, 
#               scales="free_y",
#               independent='y')
# 
# # Adjust Psi - Max Cum Infected
# 
# # filter plot for only truck transmission and psi factors
# total_rows_join_cum_sum %>% 
#   filter(contact_name %in% c('Direct Truck Share',
#                              'Indirect Truck Share',
#                              'External Truck',
#                              'Geographic'),
#          phi_factor == '1.0',
#          psi_factor %in% c('0.25','1.0','10.0','50.0','200.0')) %>% 
#   ggplot(., 
#          aes(x=as.numeric(day), 
#              y=max_cum_inf, 
#              color=factor(psi_factor, levels = surv_level))) +
#   geom_point()+
#   labs(title="Maximum Cumulative Sum of Infected Pigs by Mode of Truck Transmission",
#        subtitle = "Adjusting Psi Parameter (start date: 2019-05-01)",
#        color="Factor of Psi",
#        x="Days Since Introduction",
#        y="Cumulative Infected Pigs") +
#   theme_bw() +
#   scale_colour_manual(values=cbPalette) +
#   facet_grid2(disease~contact_name, 
#               scales="free_y",
#               independent='y')
# 
# # Adjust Phi - Maximum Cum Infected
# 
# total_rows_join_cum_sum %>% 
#   filter(contact_name %in% c('Direct Truck Share',
#                              'Indirect Truck Share',
#                              'External Truck',
#                              'Geographic'),
#          #disease == 'ASF',
#          #day < 100,
#          #start_date=='2019-05-01',
#          psi_factor == '1.0',
#          phi_factor %in% c('0.25','1.0','10.0','50.0','200.0')) %>% 
#   ggplot(., 
#          aes(x=as.numeric(day), 
#              y=max_cum_inf, 
#              color=factor(phi_factor, levels = surv_level))) +
#   geom_jitter()+
#   labs(title="Maximum Cumulative Sum of Infected Pigs by Mode of Truck Transmission",
#        subtitle = "Adjusting Phi Parameter (start date: 2019-05-01)",
#        color="Factor of Phi",
#        x="Days Since Introduction",
#        y="Cumulative Infected Pigs") +
#   theme_bw() +
#   #theme(axis.text.x = element_text(angle = 90, vjust = 0.5, hjust=1)) +
#   scale_colour_manual(values=cbPalette) +
#   facet_grid2(disease~contact_name, 
#               scales="free_y",
#               independent='y')
# 
# # Looking at Factor of Phi/Psi and Median Cum Sum Infected Pigs
# 
# all_NS_compart_data_sum_long_phipsi %>% 
#   filter(value %in% c('0.25', '1.0', '10.0','50.0','200.0'),
#          start_date=='2019-05-01') %>% 
#   ggplot(., 
#          aes(x=as.numeric(day), 
#              y=med_cum_infected, 
#              color=factor(value, levels = surv_level))) +
#   geom_jitter(height = 0.05, width=0.5) +
#   labs(title="Median Cumulative Infected by Phi and Psi Factor",
#        subtitle = "Start Date: 2019-05-01",
#        color="Factor",
#        x="Days Since Introduction",
#        y="Number of Infected Pigs") +
#   theme_bw() +
#   scale_colour_manual(values=cbPalette) +
#   facet_grid(disease~name, scales="free")
# 
# # Looking at Factor of Phi/Psi and Cum Sum Maximum Infected Pigs
# 
# all_NS_compart_data_sum_long_phipsi %>% 
#   filter(value %in% c('0.25', '1.0', '10.0','50.0','200.0'),
#          start_date=='2019-05-01') %>% 
#   ggplot(., 
#          aes(x=as.numeric(day), 
#              y=max_cum_infected, 
#              color=factor(value, levels = surv_level))) +
#   geom_jitter(height = 0.01) +
#   labs(title="Maximum Cumulative Infected by Phi and Psi Factor",
#        subtitle = "Start Date: 2019-05-01",
#        color="Factor",
#        x="Days Since Introduction",
#        y="Number of Infected Pigs") +
#   theme_bw() +
#   scale_colour_manual(values=cbPalette) +
#   facet_grid(disease~name, scales="free")
# 
# # Zooming into Factor of Phi
# 
# all_NS_compart_data_sum_long_phipsi %>% 
#   filter(value %in% c('0.25', '1.0', '10.0','50.0','200.0'),
#          start_date=='2019-05-01',
#          disease=="ASF",
#          day > 160,
#          day < 200) %>% 
#   ggplot(., 
#          aes(x=as.numeric(day), 
#              y=med_cum_infected, 
#              color=factor(value, levels = surv_level))) +
#   geom_jitter(height = 0.01) +
#   labs(title="Median Cumulative Infected by Phi and Psi Factor",
#        subtitle = "ASF Only and 160-200 Days Since Infection",
#        color="Factor",
#        x="Days Since Introduction",
#        y="Number of Infected Pigs") +
#   theme_bw() +
#   scale_colour_manual(values=cbPalette) +
#   facet_grid(disease~name, scales="free")
# 
# # Plotting Proportion of spread per route of transmission
# 
# no_surv_contact_prop %>% 
#   ggplot(., aes(x=day, y=prop_cum_inf, 
#                 fill=factor(contact_name, levels = contact_name_level))) +
#   geom_col() +
#   theme_bw() +
#   labs(fill="Transmission Route",
#        x="Days Since Introduction",
#        y="Proportion") +
#   scale_fill_manual(values=cbPalette2) +
#   facet_grid2(disease~surv_pgrm_name)
# 
# #### Plotting Proportion of spread per route of transmission WITHOUT WITHIN FARM
# 
# no_surv_contact_prop_lim %>% 
#   ggplot(., aes(x=day, y=prop_cum_inf, 
#                 fill=factor(contact_name, levels = contact_name_level))) +
#   geom_col() +
#   theme_bw() +
#   labs(fill="Transmission Route",
#        x="Days Since Introduction",
#        y="Proportion") +
#   scale_fill_manual(values=cbPalette2) +
#   facet_grid2(disease~surv_pgrm_name)
# 
# ## Plot median sum num infected by contact type by start date and disease
# ggplot(total_NS_contact_sum, 
#        aes(x=surv_pgrm, y=med_sum_num_inf, fill=contact_type))+
#   geom_col() +
#   facet_grid2(disease ~ start_date, scales = 'free', independent = 'all')
# 
# # same as above but with only phi_factor_1.0_psi_factor_1.0
# 
# total_NS_contact_sum_main <- total_NS_contact_sum %>% 
#   filter(surv_pgrm %in% list_surv_pgrm2) 
# 
# total_NS_contact_sum_main %>% 
#   filter(surv_pgrm == 'phi_factor_1.0_psi_factor_1.0' ) %>% 
#   ggplot(., aes(x=as.factor(start_date), y=med_sum_num_inf, fill=contact_type))+
#   geom_col()  +
#   theme_bw() +
#   scale_fill_manual(values=cbPalette) +
#   facet_grid2(~disease, scales = 'free', independent = "all")
# 
# # 3 main phi psi factors for only May 2019 start
# ggplot(total_NS_contact_sum_main, aes(x=as.factor(start_date), y=med_sum_num_inf, fill=contact_type))+
#   geom_col()  +
#   theme_bw() +
#   scale_fill_manual(values=cbPalette) +
#   facet_grid2(disease ~ surv_pgrm, scales = 'free', independent = "all")


###### NOW ONLY LOOKING AT THOSE RUNS THAT TOOK OFF #####

#total_NS_contact_sum_main_take_off <- total_NS_contact_sum_take_off %>% 
#  filter(surv_pgrm %in% list_surv_pgrm2) 

# contact_sum_main_take_off %>% 
#   filter(surv_pgrm == 'no_surv' ) %>% 
#   ggplot(., aes(x=as.factor(start_date), y=med_sum_num_inf, fill=contact_type))+
#   geom_col()  +
#   theme_bw() +
#   scale_fill_manual(values=cbPalette2) +
#   facet_grid2(~disease, scales = 'free', independent = "all")

# 3 main phi psi factors for only May 2019 start
# ggplot(total_NS_contact_sum_main, aes(x=as.factor(start_date), y=med_sum_num_inf, fill=contact_type))+
#   geom_col()  +
#   theme_bw() +
#   scale_fill_manual(values=cbPalette) +
#   facet_grid2(disease ~ surv_pgrm, scales = 'free', independent = "all")

