all_NS_compart_data_idx_w

all_NS_compart_data_sum_long_idx_w


rm(list=ls()) 
library(dplyr)
library(tidyr)
library(ggplot2)
setwd("Z:/Datasets/NetworkMaterial/SwineNet-model/output/")

#end_date = as.Date('2014-08-31')
#start_date = '2019_5_1'

# load data

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


all_NS_compart_data_idx_w <- all_NS_compart_data_idx_w %>% 
  mutate(surv_pgrm_name = case_when(surv_pgrm == 'phi_factor_1.0_psi_factor_1.0_idx_case_factor_1' ~ "I.W. Factor 1",
                                    surv_pgrm == 'phi_factor_1.0_psi_factor_1.0_idx_case_factor_2' ~ "I.W. Factor 2",
                                    surv_pgrm == 'phi_factor_1.0_psi_factor_1.0' ~ "I.W. Factor 3"),
         days_since_intro = as.integer(day))

all_NS_compart_data_idx_w_sum <- all_NS_compart_data_idx_w %>% 
  group_by(disease, surv_pgrm, surv_pgrm_name, start_date, date, days_since_intro) %>% 
  summarize(med_farm_count = median(farm_count),
            max_farm_count = max(farm_count),
            quantile_0.75 = quantile(farm_count, 0.75),
            quantile_0.95 = quantile(farm_count, 0.95),
            quantile_0.975 = quantile(farm_count, 0.975)) %>%
  pivot_longer(cols=med_farm_count:quantile_0.975) %>% 
  ungroup()

all_NS_compart_data_idx_w_sum %>% 
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
  facet_grid2(disease~surv_pgrm_name, scales = "free_y", independent = "y")

# same as above, but just for May 2019 start day and summary_statistic
# BASED ON NAKUL'S ADVICE!!
all_NS_compart_data_idx_w_sum %>% 
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
  facet_grid2(disease~surv_pgrm_name, scales = "free_y", independent = "y")

