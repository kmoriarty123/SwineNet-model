#############################################################
## title: "Plots for SwineNet Model Surveillance
## author : Kathleen Moriarty
## date_created : 08.04.2022
## desc: 
## output: various summary surveillance plots
#############################################################

rm(list=ls()) 
library(dplyr)
library(tidyr)
library(ggplot2)
setwd("Z:/Datasets/NetworkMaterial/SwineNet-model/output/")

#end_date = as.Date('2014-08-31')
start_date = '2014_1_1'

# load data
load(paste0("total_compart_data_", start_date, ".RData"))
load(paste0("total_first_detect_", start_date, ".RData"))
load(paste0("total_outbreak_data_", start_date, ".RData"))

# set initial values

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

total_first_detect <- total_first_detect %>% 
  mutate(surv_pgrm_desc = case_when(surv_pgrm == 'phi_factor_1.0_psi_factor_1.0' ~ "None",
                                    surv_pgrm == 'num_sh_9' ~ "9 Slaughterhouses",
                                    surv_pgrm == 'num_sh_36' ~ "36 Slaughterhouses",
                                    surv_pgrm == 'num_sh_18' ~ "18 Slaughterhouses",
                                    surv_pgrm == 'nets_250_90_t' ~ "Exterior Truck Fomites",
                                    surv_pgrm == 'nets_250_90_p' ~ "Direct Truck Share",
                                    surv_pgrm == 'nets_250_90_i' ~ "Indirect Truck Share",
                                    surv_pgrm == 'nets_250_90_g' ~ "Geographic",
                                    surv_pgrm == 'nets_250_90_d' ~ "Direct Transfer",
                                    surv_pgrm == 'mort_rate_inc_0.15' ~ "15% Mortality Rate Increase",
                                    surv_pgrm == 'mort_rate_inc_0.1' ~ "10% Mortality Rate Increase",
                                    surv_pgrm == 'mort_rate_inc_0.05' ~ "5% Mortality Rate Increase",
                                    surv_pgrm == 'morbid_rate_0.4' ~ "40% Morbidity",
                                    surv_pgrm == 'morbid_rate_0.3' ~ "30% Morbidity",
                                    surv_pgrm == 'morbid_rate_0.2' ~ "20% Morbidity"
  ))

first_detect_all_take_off <- first_detect_all_take_off %>% 
  mutate(surv_pgrm_desc = case_when(surv_pgrm == 'phi_factor_1.0_psi_factor_1.0' ~ "None",
                                    surv_pgrm == 'num_sh_9' ~ "9 Slaughterhouses",
                                    surv_pgrm == 'num_sh_36' ~ "36 Slaughterhouses",
                                    surv_pgrm == 'num_sh_18' ~ "18 Slaughterhouses",
                                    surv_pgrm == 'nets_250_90_t' ~ "Exterior Truck Fomites",
                                    surv_pgrm == 'nets_250_90_p' ~ "Direct Truck Share",
                                    surv_pgrm == 'nets_250_90_i' ~ "Indirect Truck Share",
                                    surv_pgrm == 'nets_250_90_g' ~ "Geographic",
                                    surv_pgrm == 'nets_250_90_d' ~ "Direct Transfer",
                                    surv_pgrm == 'mort_rate_inc_0.15' ~ "15% Mortality Rate Increase",
                                    surv_pgrm == 'mort_rate_inc_0.1' ~ "10% Mortality Rate Increase",
                                    surv_pgrm == 'mort_rate_inc_0.05' ~ "5% Mortality Rate Increase",
                                    surv_pgrm == 'morbid_rate_0.4' ~ "40% Morbidity",
                                    surv_pgrm == 'morbid_rate_0.3' ~ "30% Morbidity",
                                    surv_pgrm == 'morbid_rate_0.2' ~ "20% Morbidity"
  ))

total_compart_data <- total_compart_data %>% 
  mutate(surv_pgrm_desc = case_when(surv_pgrm == 'phi_factor_1.0_psi_factor_1.0' ~ "None",
                                    surv_pgrm == 'num_sh_9' ~ "9 Slaughterhouses",
                                    surv_pgrm == 'num_sh_36' ~ "36 Slaughterhouses",
                                    surv_pgrm == 'num_sh_18' ~ "18 Slaughterhouses",
                                    surv_pgrm == 'nets_250_90_t' ~ "Exterior Truck Fomites",
                                    surv_pgrm == 'nets_250_90_p' ~ "Direct Truck Share",
                                    surv_pgrm == 'nets_250_90_i' ~ "Indirect Truck Share",
                                    surv_pgrm == 'nets_250_90_g' ~ "Geographic",
                                    surv_pgrm == 'nets_250_90_d' ~ "Direct Transfer",
                                    surv_pgrm == 'mort_rate_inc_0.15' ~ "15% Mortality Rate Increase",
                                    surv_pgrm == 'mort_rate_inc_0.1' ~ "10% Mortality Rate Increase",
                                    surv_pgrm == 'mort_rate_inc_0.05' ~ "5% Mortality Rate Increase",
                                    surv_pgrm == 'morbid_rate_0.4' ~ "40% Morbidity",
                                    surv_pgrm == 'morbid_rate_0.3' ~ "30% Morbidity",
                                    surv_pgrm == 'morbid_rate_0.2' ~ "20% Morbidity"
  ))

total_compart_data_take_off_last_day_cases <- total_compart_data_take_off_last_day_cases %>% 
  mutate(surv_pgrm_desc = case_when(surv_pgrm == 'phi_factor_1.0_psi_factor_1.0' ~ "None",
                                    surv_pgrm == 'num_sh_9' ~ "9 Slaughterhouses",
                                    surv_pgrm == 'num_sh_36' ~ "36 Slaughterhouses",
                                    surv_pgrm == 'num_sh_18' ~ "18 Slaughterhouses",
                                    surv_pgrm == 'nets_250_90_t' ~ "Exterior Truck Fomites",
                                    surv_pgrm == 'nets_250_90_p' ~ "Direct Truck Share",
                                    surv_pgrm == 'nets_250_90_i' ~ "Indirect Truck Share",
                                    surv_pgrm == 'nets_250_90_g' ~ "Geographic",
                                    surv_pgrm == 'nets_250_90_d' ~ "Direct Transfer",
                                    surv_pgrm == 'mort_rate_inc_0.15' ~ "15% Mortality Rate Increase",
                                    surv_pgrm == 'mort_rate_inc_0.1' ~ "10% Mortality Rate Increase",
                                    surv_pgrm == 'mort_rate_inc_0.05' ~ "5% Mortality Rate Increase",
                                    surv_pgrm == 'morbid_rate_0.4' ~ "40% Morbidity",
                                    surv_pgrm == 'morbid_rate_0.3' ~ "30% Morbidity",
                                    surv_pgrm == 'morbid_rate_0.2' ~ "20% Morbidity"
  ))

total_outbreak_data <- total_outbreak_data %>% 
  mutate(surv_pgrm_desc = case_when(surv_pgrm == 'phi_factor_1.0_psi_factor_1.0' ~ "None",
                                    surv_pgrm == 'num_sh_9' ~ "9 Slaughterhouses",
                                    surv_pgrm == 'num_sh_36' ~ "36 Slaughterhouses",
                                    surv_pgrm == 'num_sh_18' ~ "18 Slaughterhouses",
                                    surv_pgrm == 'nets_250_90_t' ~ "Exterior Truck Fomites",
                                    surv_pgrm == 'nets_250_90_p' ~ "Direct Truck Share",
                                    surv_pgrm == 'nets_250_90_i' ~ "Indirect Truck Share",
                                    surv_pgrm == 'nets_250_90_g' ~ "Geographic",
                                    surv_pgrm == 'nets_250_90_d' ~ "Direct Transfer",
                                    surv_pgrm == 'mort_rate_inc_0.15' ~ "15% Mortality Rate Increase",
                                    surv_pgrm == 'mort_rate_inc_0.1' ~ "10% Mortality Rate Increase",
                                    surv_pgrm == 'mort_rate_inc_0.05' ~ "5% Mortality Rate Increase",
                                    surv_pgrm == 'morbid_rate_0.4' ~ "40% Morbidity",
                                    surv_pgrm == 'morbid_rate_0.3' ~ "30% Morbidity",
                                    surv_pgrm == 'morbid_rate_0.2' ~ "20% Morbidity"
  ))

surv_pgrm_levels = c('None',
                     "9 Slaughterhouses",
                     "18 Slaughterhouses",
                     "36 Slaughterhouses",
                     "20% Morbidity",
                     "30% Morbidity",
                     "40% Morbidity",
                     "5% Mortality Rate Increase",
                     "10% Mortality Rate Increase",
                     "15% Mortality Rate Increase",
                     "Direct Transfer",
                     "Direct Truck Share",
                     "Indirect Truck Share",
                     "Exterior Truck Fomites",
                     "Geographic")

############## SURVEILLANCE ##############  

# distribution of first date of detection for all runs
ggplot(total_first_detect, aes(x=date, 
                               y=factor(surv_pgrm_desc, levels = surv_pgrm_levels),
                               #fill=surv_type,
)) +
  geom_boxplot(outlier.alpha = 0, color="black") +
  geom_point(size = 3, alpha = 0.15, aes(color=surv_type)) +
  theme_bw() + 
  #theme(axis.text.x = element_text(angle = 90, vjust = 0.5, hjust=1)) +
  #scale_x_date(breaks = all_compart_data_sum$date[seq(1, length(unique(all_compart_data_sum$date)), by = 14)]) +
  labs(#title = "Date of First Detection for Each Simulation",
    x="Date", y="Surveillance Pgrm",
    fill="Surveillance Type"
  ) +
  scale_y_discrete(limits=rev) +
  guides(colour = guide_legend(override.aes = list(alpha = 1), title = "Surveillance Type")) +
  scale_colour_manual(values=cbPalette) +
  facet_wrap(~disease)

# Obtain medians from above plots
med_first_detect <- total_first_detect %>% 
  group_by(disease, surv_pgrm_desc) %>% 
  summarize(med_earliest_date = median(date))

####### Proportion of positive cases detected #########

# proportion of true cases found over the total number of cases
total_compart_data_last_day <- total_compart_data %>%
  filter(date=="2014-08-31")

# Calculate total cases and total cases detected
total_compart_data_last_day_cases <- total_compart_data_last_day %>% 
  mutate(total_cases = exposed + infected + asymptomatic + removed + recovered + isolated + quarantined_a + quarantined_e,
         total_detected = isolated + quarantined_a + quarantined_e,
         prop_detected = total_detected / total_cases)

ggplot(total_compart_data_last_day_cases, 
       aes(x=factor(surv_pgrm_desc, levels = surv_pgrm_levels), 
           y=prop_detected)) +
  geom_boxplot(outlier.alpha = 0, color="black") +
  geom_point(size = 3, alpha = 0.15, aes(color=surv_type)) +
  theme_bw() +
  facet_wrap(~disease) +
  labs(#title="Proportion of Number of Cases Detected", 
    y='Proportion',
    x="Surveillance Program") +
  scale_x_discrete(limits=rev) +
  guides(colour = guide_legend(override.aes = list(alpha = 1), title = "Surveillance Type")) +
  scale_colour_manual(values=cbPalette) +
  coord_flip()

# Look at actual median values
median_prop_detect <- total_compart_data_last_day_cases %>% 
  group_by(disease, surv_pgrm_desc) %>% 
  summarize(median_prop_detected = median(prop_detected))

############ OUTBREAK SIZE ############

ggplot(total_outbreak_data, aes(x=factor(surv_pgrm_desc, levels = surv_pgrm_levels),  
                                y=prop_under_10)) +
  geom_point(size = 3, aes(color=surv_type)) +
  theme_bw()+
  labs(#title = "Proportion of Runs With Under 20 Infected Farms",
    y="Proportion", x="Surveillance Pgrm")+  
  facet_wrap(~disease, scales = "free_x") +
  scale_x_discrete(limits=rev) +
  guides(colour = guide_legend(override.aes = list(alpha = 1), title = "Surveillance Type")) +
  scale_colour_manual(values=cbPalette) +
  coord_flip()

ggplot(total_outbreak_data, aes(x=factor(surv_pgrm_desc, levels = surv_pgrm_levels), 
                                y=prop_no_new_inf_20)) +
  geom_point(size = 3, aes(color=surv_type)) +
  theme_bw()+
  labs(#title = "Proportion of Runs That Died Out",
    #subtitle = "Defined as no new infected pigs in last 20 days",
    y="Proportion", x="Surveillance Pgrm")+ 
  facet_wrap(~disease, scales = "free_x") +
  scale_x_discrete(limits=rev) +
  guides(colour = guide_legend(override.aes = list(alpha = 1), title = "Surveillance Type")) +
  scale_colour_manual(values=cbPalette) +
  coord_flip()

#######################################################
# No Take Off
#######################################################

# distribution of first date of detection for all runs
first_detect_all_take_off %>% 
  filter(start_date == '2014-01-01') %>% 
ggplot(., aes(x=date, 
                                      y=factor(surv_pgrm_desc, levels = surv_pgrm_levels),
                                      #fill=surv_type,
)) +
  geom_boxplot(outlier.alpha = 0, color="black") +
  geom_point(size = 3, alpha = 0.15, aes(color=surv_type)) +
  theme_bw() + 
  #theme(axis.text.x = element_text(angle = 90, vjust = 0.5, hjust=1)) +
  #scale_x_date(breaks = all_compart_data_sum$date[seq(1, length(unique(all_compart_data_sum$date)), by = 14)]) +
  labs(#title = "Date of First Detection for Each Simulation",
    x="Date", y="Surveillance Pgrm",
    fill="Surveillance Type"
  ) +
  scale_y_discrete(limits=rev) +
  guides(colour = guide_legend(override.aes = list(alpha = 1), title = "Surveillance Type")) +
  scale_colour_manual(values=cbPalette) +
  facet_wrap(~disease)

############# Proportion of positive cases detected


ggplot(total_compart_data_take_off_last_day_cases, 
       aes(x=factor(surv_pgrm_desc, levels = surv_pgrm_levels), 
           y=prop_detected)) +
  geom_boxplot(outlier.alpha = 0, color="black") +
  geom_point(size = 3, alpha = 0.15, aes(color=surv_type)) +
  theme_bw() +
  facet_wrap(~disease) +
  labs(#title="Proportion of Number of Cases Detected", 
    y='Proportion',
    x="Surveillance Program") +
  scale_x_discrete(limits=rev) +
  guides(colour = guide_legend(override.aes = list(alpha = 1), title = "Surveillance Type")) +
  scale_colour_manual(values=cbPalette) +
  coord_flip()

### Total Under 10 ###
prop_farm_count_under_10_lim <- total_compart_data_lim %>% 
  group_by(disease, surv_pgrm, num_run) %>% 
  slice_max(farm_count) %>% 
  slice_min(date) %>% 
  ungroup() %>%
  mutate(all_n = n()) %>% 
  filter(farm_count < 10) %>%
  mutate(prop_under_10 = n()/all_n) %>%
  distinct(prop_under_10)

