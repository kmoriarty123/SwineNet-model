#############################################################
## title: "Plots for SwineNet Model Output Data with ALL diseases"
## author : Kathleen Moriarty
## date_created : 08.04.2022
## desc: 
## output: various summary plots
#############################################################

rm(list=ls()) 
library(dplyr)
library(tidyr)
library(ggplot2)
library(ggh4x)
setwd("Z:/Datasets/NetworkMaterial/SwineNet-model/output/")

#end_date = as.Date('2014-08-31')
#start_date = '2019_5_1'

###################### Import data ##########################

# load data
load("all_total_compart_data.RData")
load('total_compart_data_take_off.RData')
# set initial values

###################### Defining constants ######################

cbPalette <- c(#"#999999", # grey
  "#0072B2", # yellowy orange
  #"#56B4E9", # sky blue
  "#009E73", # green 
  #"#F0E442", # yellow
  "#E69F00", # blue
  "#CC79A7", # mauve
  "#D55E00", # orangey red
  "#000000", 
  "#7570b3" )# purply blue

name_levels = c('Median Farm Count',
                '95th Percentile',
                'Maximum Farm Count')

name_levels_pig = c('Median Pig Count',
                    '95th Percentile Pig',
                    'Maximum Pig Count')

########################### Preparing data ########################

all_total_compart_data_new <- all_total_compart_data %>% 
  mutate(surv_pgrm_desc = case_when(surv_pgrm == 'no_surv' ~ "None",
                                    surv_pgrm == 'num_sh_9' ~ "9 Slaughterhouses",
                                    surv_pgrm == 'num_sh_36' ~ "36 Slaughterhouses",
                                    surv_pgrm == 'num_sh_18' ~ "18 Slaughterhouses",
                                    surv_pgrm == 'nets_250_90_t' ~ "Exterior Truck Fomites",
                                    surv_pgrm == 'nets_250_90_p' ~ "Direct Truck Share",
                                    surv_pgrm == 'nets_250_90_i' ~ "Indirect Truck Share",
                                    surv_pgrm == 'nets_250_90_g' ~ "Geographic",
                                    surv_pgrm == 'nets_250_90_d' ~ "Direct Transfer",
                                    surv_pgrm == 'farmer_prop_1.0_mort_rate_inc_0.15' ~ "100% Farmers 15% Mortality Rate Increase",
                                    surv_pgrm == 'farmer_prop_1.0_mort_rate_inc_0.1' ~ "100% Farmers 10% Mortality Rate Increase",
                                    surv_pgrm == 'farmer_prop_1.0_mort_rate_inc_0.05' ~ "100% Farmers 5% Mortality Rate Increase",
                                    surv_pgrm == 'farmer_prop_1.0_morbid_rate_0.4' ~ "100% Farmers 40% Morbidity",
                                    surv_pgrm == 'farmer_prop_1.0_morbid_rate_0.3' ~ "100% Farmers 30% Morbidity",
                                    surv_pgrm == 'farmer_prop_1.0_morbid_rate_0.2' ~ "100% Farmers 20% Morbidity",
                                    surv_pgrm == 'farmer_prop_0.9_mort_rate_inc_0.15' ~ "90% Farmers 15% Mortality Rate Increase",
                                    surv_pgrm == 'farmer_prop_0.9_mort_rate_inc_0.1' ~ "90% Farmers 10% Mortality Rate Increase",
                                    surv_pgrm == 'farmer_prop_0.9_mort_rate_inc_0.05' ~ "90% Farmers 5% Mortality Rate Increase",
                                    surv_pgrm == 'farmer_prop_0.9_morbid_rate_0.4' ~ "90% Farmers 40% Morbidity",
                                    surv_pgrm == 'farmer_prop_0.9_morbid_rate_0.3' ~ "90% Farmers 30% Morbidity",
                                    surv_pgrm == 'farmer_prop_0.9_morbid_rate_0.2' ~ "90% Farmers 20% Morbidity",
                                    surv_pgrm == 'farmer_prop_0.6_mort_rate_inc_0.15' ~ "60% Farmers 15% Mortality Rate Increase",
                                    surv_pgrm == 'farmer_prop_0.6_mort_rate_inc_0.1' ~ "60% Farmers 10% Mortality Rate Increase",
                                    surv_pgrm == 'farmer_prop_0.6_mort_rate_inc_0.05' ~ "60% Farmers 5% Mortality Rate Increase",
                                    surv_pgrm == 'farmer_prop_0.6_morbid_rate_0.4' ~ "60% Farmers 40% Morbidity",
                                    surv_pgrm == 'farmer_prop_0.6_morbid_rate_0.3' ~ "60% Farmers 30% Morbidity",
                                    surv_pgrm == 'farmer_prop_0.6_morbid_rate_0.2' ~ "60% Farmers 20% Morbidity"))

all_total_compart_data <- all_total_compart_data_new
all_total_compart_data_new = NULL

# Prepare only take-off dataset for plotting
total_compart_data_take_off_sum <- total_compart_data_take_off %>% 
  filter(start_date == '2019-05-01',
         surv_type != 'sensitivity') %>%
  mutate(tot_inf = (exposed+infected+asymptomatic+removed+recovered)) %>% 
  group_by(disease, 
           start_date, 
           surv_pgrm,
           surv_type,
           days_since_intro) %>% 
  summarize(med_farm_count = median(farm_count),
            quantile_0.95 = quantile(farm_count, 0.95),
            max_farm_count = max(farm_count),
            med_pig_count = median(tot_inf),
            quantile_0.95_pig = quantile(tot_inf, 0.95),
            max_pig_count = max(tot_inf)) %>% 
  ungroup() %>% 
  pivot_longer(med_farm_count:max_pig_count) %>% 
  mutate(name_desc = case_when(name =='med_farm_count' ~ 'Median Farm Count',
                               name =='max_farm_count' ~ 'Maximum Farm Count',
                               name =='quantile_0.95' ~ '95th Percentile',
                               name =='med_pig_count' ~ 'Median Pig Count',
                               name =='max_pig_count' ~ 'Maximum Pig Count',
                               name =='quantile_0.95_pig' ~ '95th Percentile Pig')) %>% 
  mutate(surv_pgrm_desc = case_when(surv_pgrm == 'no_surv' ~ "None",
                                    surv_pgrm == 'num_sh_9' ~ "9 Slaughterhouses",
                                    surv_pgrm == 'num_sh_36' ~ "36 Slaughterhouses",
                                    surv_pgrm == 'num_sh_18' ~ "18 Slaughterhouses",
                                    surv_pgrm == 'nets_250_90_t' ~ "Exterior Truck Fomites",
                                    surv_pgrm == 'nets_250_90_p' ~ "Direct Truck Share",
                                    surv_pgrm == 'nets_250_90_i' ~ "Indirect Truck Share",
                                    surv_pgrm == 'nets_250_90_g' ~ "Geographic",
                                    surv_pgrm == 'nets_250_90_d' ~ "Direct Transfer",
                                    surv_pgrm == 'farmer_prop_1.0_mort_rate_inc_0.15' ~ "100% Farmers 15% Mortality Rate Increase",
                                    surv_pgrm == 'farmer_prop_1.0_mort_rate_inc_0.1' ~ "100% Farmers 10% Mortality Rate Increase",
                                    surv_pgrm == 'farmer_prop_1.0_mort_rate_inc_0.05' ~ "100% Farmers 5% Mortality Rate Increase",
                                    surv_pgrm == 'farmer_prop_1.0_morbid_rate_0.4' ~ "100% Farmers 40% Morbidity",
                                    surv_pgrm == 'farmer_prop_1.0_morbid_rate_0.3' ~ "100% Farmers 30% Morbidity",
                                    surv_pgrm == 'farmer_prop_1.0_morbid_rate_0.2' ~ "100% Farmers 20% Morbidity",
                                    surv_pgrm == 'farmer_prop_0.9_mort_rate_inc_0.15' ~ "90% Farmers 15% Mortality Rate Increase",
                                    surv_pgrm == 'farmer_prop_0.9_mort_rate_inc_0.1' ~ "90% Farmers 10% Mortality Rate Increase",
                                    surv_pgrm == 'farmer_prop_0.9_mort_rate_inc_0.05' ~ "90% Farmers 5% Mortality Rate Increase",
                                    surv_pgrm == 'farmer_prop_0.9_morbid_rate_0.4' ~ "90% Farmers 40% Morbidity",
                                    surv_pgrm == 'farmer_prop_0.9_morbid_rate_0.3' ~ "90% Farmers 30% Morbidity",
                                    surv_pgrm == 'farmer_prop_0.9_morbid_rate_0.2' ~ "90% Farmers 20% Morbidity",
                                    surv_pgrm == 'farmer_prop_0.6_mort_rate_inc_0.15' ~ "60% Farmers 15% Mortality Rate Increase",
                                    surv_pgrm == 'farmer_prop_0.6_mort_rate_inc_0.1' ~ "60% Farmers 10% Mortality Rate Increase",
                                    surv_pgrm == 'farmer_prop_0.6_mort_rate_inc_0.05' ~ "60% Farmers 5% Mortality Rate Increase",
                                    surv_pgrm == 'farmer_prop_0.6_morbid_rate_0.4' ~ "60% Farmers 40% Morbidity",
                                    surv_pgrm == 'farmer_prop_0.6_morbid_rate_0.3' ~ "60% Farmers 30% Morbidity",
                                    surv_pgrm == 'farmer_prop_0.6_morbid_rate_0.2' ~ "60% Farmers 20% Morbidity"))

#save(total_compart_data_take_off_sum, file='total_compart_data_take_off_sum.RData')

# Without surveillance, summarize the farm_counts
total_compart_data_no_surv <- all_total_compart_data %>% 
  filter(surv_pgrm_desc == "None")

total_compart_data_no_surv_sum <- total_compart_data_no_surv %>% 
  group_by(disease, start_date, date, days_since_intro) %>% 
  summarize(med_farm_count = median(farm_count),
            max_farm_count = max(farm_count),
            quantile_0.75 = quantile(farm_count, 0.75),
            quantile_0.95 = quantile(farm_count, 0.95),
            quantile_0.975 = quantile(farm_count, 0.975),
            tot_inf = exposed+infected+asymptomatic+removed+recovered,
            med_pig_count = median(tot_inf),
            quantile_0.95_pig = quantile(tot_inf, 0.95),
            max_pig_count = max(tot_inf)) %>%
  pivot_longer(cols=med_farm_count:max_pig_count) %>% 
  ungroup()

# Include Median Max, and 95th% Quantile for each 
total_compart_data_no_surv_sum <- total_compart_data_no_surv_sum %>% 
  mutate(name_desc = case_when(name =='med_farm_count' ~ 'Median Farm Count',
                               name =='max_farm_count' ~ 'Maximum Farm Count',
                               name =='quantile_0.95' ~ '95th Percentile',
                               name =='med_pig_count' ~ 'Median Pig Count',
                               name =='max_pig_count' ~ 'Maximum Pig Count',
                               name =='quantile_0.95_pig' ~ '95th Percentile Pig'))


# limit the stats to just max_farm_count, quantile 0.95, med_farm_count
# total_compart_data_no_surv_sum %>% 
#   filter(name %in% c('max_farm_count', 
#                      'quantile_0.95', 
#                      'med_farm_count')) %>% 
# ggplot(., 
#        aes(x=days_since_intro, 
#            y=value, 
#            color=factor(name_desc, levels = name_levels))) +
#   geom_point() +
#   theme_bw() +
#   #scale_colour_manual(values=c("#E69F00", "#56B4E9"))+
#   scale_colour_manual(values=cbPalette) +
#   labs(#title="Median and Maximum Infected Farm Count for No Surveillance", 
#        y='Farm Count',
#        x="Days Since Introduction",
#        color="Summary Statistic") +
#   facet_grid2(factor(disease, 
#                      levels = c('PRRS','ASF','APP'))~start_date, scales = "free_y", independent = "y")
# 
# # same as above, but just for May 2019 start day
# total_compart_data_no_surv_sum %>% 
#   filter(start_date == '2019-05-01') %>% 
# ggplot(., aes(x=days_since_intro, y=value, color=name)) +
#   geom_point() +
#   theme_bw() +
#   #scale_colour_manual(values=c("#E69F00", "#56B4E9"))+
#   scale_colour_manual(values=cbPalette) +
#   labs(#title="Median and Maximum Infected Farm Count for No Surveillance", 
#     y='Farm Count',
#     x="Days Since Introduction",
#     color="Summary Statistic") +
#   facet_wrap(~factor(disease, 
#                      levels = c('PRRS','ASF','APP')), scales = "free_y")

####################### Plots #############################

# median, 95th, max farm count for May 2019 start day
f1 <- total_compart_data_no_surv_sum %>% 
  filter(start_date == '2019-05-01') %>% 
  filter(name %in% c('med_farm_count', 'quantile_0.95', 'max_farm_count')) %>% 
  ggplot(., aes(x=days_since_intro, 
                y=value, 
                color=factor(name_desc, levels = name_levels))) +
  geom_point() +
  theme_bw() +
  scale_colour_manual(values=cbPalette) +
  labs(#title="Median and Maximum Infected Farm Count for No Surveillance", 
    y='Cumulative Farm Count',
    x="Days Since Introduction",
    color="Summary Statistic") +
  facet_wrap(~factor(disease, 
                     levels = c('PRRS','ASF','APP')), scales = "free_y")

# median, 95th, max pig count for May 2019 start day
p1 <- total_compart_data_no_surv_sum %>% 
  filter(start_date == '2019-05-01') %>% 
  filter(name %in% c('med_pig_count', 'quantile_0.95_pig', 'max_pig_count')) %>% 
  ggplot(., aes(x=days_since_intro, 
                y=value, 
                color=factor(name_desc, levels = name_levels_pig))) +
  geom_point() +
  theme_bw() +
  scale_colour_manual(values=cbPalette) +
  labs(#title="Median and Maximum Infected Farm Count for No Surveillance", 
    y='Cumulative Pig Count',
    x="Days Since Introduction",
    color="Summary Statistic") +
  facet_wrap(~factor(disease, 
                     levels = c('PRRS','ASF','APP')), scales = "free_y")

# ONLY TAKE OFF: median, 95th, max farm count for May 2019 start day
f2 <- total_compart_data_take_off_sum %>% 
  filter(surv_pgrm == 'no_surv') %>% 
  filter(name %in% c('med_farm_count', 'quantile_0.95', 'max_farm_count')) %>% 
  ggplot(., aes(x=days_since_intro, 
                y=value, 
                color=factor(name_desc, levels = name_levels))) +
  geom_point() +
  theme_bw() +
  scale_colour_manual(values=cbPalette) +
  labs(#title="Median and Maximum Infected Farm Count for No Surveillance", 
    y='Cumulative Farm Count',
    x="Days Since Introduction",
    color="Summary Statistic") +
  facet_wrap(~factor(disease, 
                     levels = c('PRRS','ASF','APP')), scales = "free_y")

# median, 95th, max farm count for May 2019 start day
p2 <- total_compart_data_take_off_sum %>% 
  filter(surv_pgrm == 'no_surv') %>% 
  filter(name %in% c('med_pig_count', 'quantile_0.95_pig', 'max_pig_count')) %>% 
  ggplot(., aes(x=days_since_intro, 
                y=value, 
                color=factor(name_desc, levels = name_levels_pig))) +
  geom_point() +
  theme_bw() +
  scale_colour_manual(values=cbPalette) +
  labs(#title="Median and Maximum Infected Farm Count for No Surveillance", 
    y='Cumulative Pig Count',
    x="Days Since Introduction",
    color="Summary Statistic") +
  facet_wrap(~factor(disease, 
                     levels = c('PRRS','ASF','APP')), scales = "free_y")


# To combine plots
library(ggpubr)

ggarrange(p1,p2,
          #align='v', 
          labels=c('A', 'B'),
          common.legend = T,
          legend='right')

ggarrange(f1,f2,
          #align='v', 
          labels=c('A', 'B'),
          common.legend = T,
          legend='right')

# Values for article
# plot for all simultions
total_compart_data_no_surv_sum %>% 
  filter(start_date == '2019-05-01',
         name %in% c('med_farm_count', 'quantile_0.95', 'max_farm_count'), 
         days_since_intro == 244) 

# Plot for "take-off" %
tmpNS <- total_compart_data_take_off_sum %>% 
  filter(start_date == '2019-05-01',
         #name %in% c('med_farm_count','med_removed','med_inf'), #, 'quantile_0.95', 'max_farm_count'), 
         days_since_intro == 31,
         surv_pgrm == 'no_surv',
         disease == 'ASF') %>% 
  select(disease,days_since_intro, surv_pgrm, name, value)
