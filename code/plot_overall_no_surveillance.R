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
setwd("Z:/Datasets/NetworkMaterial/SwineNet-model/output/")

#end_date = as.Date('2014-08-31')
#start_date = '2019_5_1'

# load data
load("all_total_compart_data.RData")

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

all_total_compart_data <- all_total_compart_data %>% 
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

# Without surveillance, summarize the farm_counts
total_compart_data_no_surv <- all_total_compart_data %>% 
  filter(surv_pgrm_desc == "None")

total_compart_data_no_surv_sum <- total_compart_data_no_surv %>% 
  group_by(disease, start_date, date, days_since_intro) %>% 
  summarize(med_farm_count = median(farm_count),
            max_farm_count = max(farm_count),
            quantile_0.75 = quantile(farm_count, 0.75),
            quantile_0.95 = quantile(farm_count, 0.95),
            quantile_0.975 = quantile(farm_count, 0.975)) %>%
  pivot_longer(cols=med_farm_count:quantile_0.975) %>% 
  ungroup()

ggplot(total_compart_data_no_surv_sum, aes(x=days_since_intro, y=value, color=name)) +
  geom_point() +
  theme_bw() +
  #scale_colour_manual(values=c("#E69F00", "#56B4E9"))+
  scale_colour_manual(values=cbPalette) +
  labs(#title="Median and Maximum Infected Farm Count for No Surveillance", 
       y='Farm Count',
       x="Date",
       color="Summary Statistic") +
  facet_grid2(disease~start_date, scales = "free_y", independent = "y")

# same as above, but just for May 2019 start day
total_compart_data_no_surv_sum %>% 
  filter(start_date == '2019-05-01') %>% 
ggplot(., aes(x=days_since_intro, y=value, color=name)) +
  geom_point() +
  theme_bw() +
  #scale_colour_manual(values=c("#E69F00", "#56B4E9"))+
  scale_colour_manual(values=cbPalette) +
  labs(#title="Median and Maximum Infected Farm Count for No Surveillance", 
    y='Farm Count',
    x="Date",
    color="Summary Statistic") +
  facet_wrap(~disease, scales = "free_y")

# same as above, but just for May 2019 start day and summary_statistic
# BASED ON NAKUL'S ADVICE!!
total_compart_data_no_surv_sum %>% 
  filter(start_date == '2019-05-01') %>% 
  filter(name %in% c('med_farm_count', 'quantile_0.95', 'max_farm_count')) %>% 
  ggplot(., aes(x=days_since_intro, y=value, color=name)) +
  geom_point() +
  theme_bw() +
  scale_colour_manual(values=cbPalette) +
  labs(#title="Median and Maximum Infected Farm Count for No Surveillance", 
    y='Farm Count',
    x="Date",
    color="Summary Statistic") +
  facet_wrap(~disease, scales = "free_y")

