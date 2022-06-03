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
setwd("Z:/Datasets/NetworkMaterial/SwineNet-model/output/")

start_date = '2019_5_1'
end_date = as.Date('2019-12-31')
load(paste0("total_compart_data_", start_date, ".RData"))
load(paste0("total_first_detect_", start_date, ".RData"))
load(paste0("total_outbreak_data_", start_date, ".RData"))

cbPalette <- c(#"#999999", # grey
  "#E69F00", # yellowy orange
  "#56B4E9", # sky blue
  "#009E73", # green 
  "#F0E442", # yellow
  "#0072B2", # blue
  "#CC79A7", # mauve
  "#D55E00", # orangey red
  "#000000", 
  "#7570b3" )# purply blue


##### ALL surveillance Program Data #####
### Distributions of ranges on the last day ###

all_compart_data_last_date <- total_compart_data %>% 
  filter(date == end_date)

ggplot(all_compart_data_last_date, aes(x=surv_pgrm, y=farm_count, fill=surv_type)) + 
  geom_boxplot() +
  theme_bw() +
  theme(axis.text.x = element_text(angle = 90, vjust = 0.5, hjust=1)) +
  #theme_minimal() +
  facet_wrap(~disease, scales = "free_y")+
  labs(x='Surveillance Program', y='Number of Farms',
       title = "Distribution of Number of Infected Farms after 8 Months")

ggplot(all_compart_data_last_date, aes(x=surv_pgrm, y=farm_count, fill=surv_type)) + 
  geom_violin() +
  theme_bw() +
  theme(axis.text.x = element_text(angle = 90, vjust = 0.5, hjust=1)) +
  #theme_minimal() +
  facet_wrap(~disease, scales = "free_y") +
  labs(x='Surveillance Program', y='Number of Farms',
       title = "Distribution of Number of Infected Farms after 8 Months")

ggplot(all_compart_data_last_date, aes(x=surv_pgrm, y=removed)) + 
  geom_boxplot() +
  theme(axis.text.x = element_text(angle = 90, vjust = 0.5, hjust=1))+
  facet_wrap(~disease) 

ggplot(all_compart_data_last_date, aes(x=surv_pgrm, y=recovered)) + 
  geom_boxplot() +
  theme(axis.text.x = element_text(angle = 90, vjust = 0.5, hjust=1)) +
  facet_wrap(~disease)

# only looking at the data that is greater than 1 and how that is distributed
# and adding the % of the data that is represented
tmp <- all_compart_data_last_date %>% 
  filter(farm_count>1) %>%
  group_by(disease, surv_pgrm) %>%
  mutate(prop_over_one = n()/1000) %>%
  ungroup()

ggplot(tmp, aes(x=surv_pgrm, y=farm_count, fill=surv_type)) + 
  geom_violin() +
  theme_bw() +
  theme(axis.text.x = element_text(angle = 90, vjust = 0.5, hjust=1)) +
  #theme_minimal() +
  facet_wrap(~disease, scales = "free_y") +
  labs(x='Surveillance Program', y='Number of Farms',
       title = "Distribution of Number of Infected Farms after 8 Months")

#### Percentage of runs that are greater than one ####

# median farm count at first detect
ggplot(total_first_detect, aes(x=surv_pgrm, y=med_farm_count, 
                               fill=surv_type)) +
  geom_col()+
  facet_wrap(~disease, scales = "free_y")



ggplot(total_first_detect, aes(x=date, 
                             y=surv_pgrm))+
                             #color=farm_count,
                             #color=farm_count)) +
  geom_boxplot()+#color = "gray60", outlier.alpha = 0) +
  geom_point(color="#56B4E9",size = 3, alpha = 0.15) +
  theme_minimal() + 
  theme(axis.text.x = element_text(angle = 90, vjust = 0.5, hjust=1)) +
  scale_x_date(breaks = all_compart_data_sum$date[seq(1, length(unique(all_compart_data_sum$date)), by = 14)]) +
  labs(title = "Date of First Detection for Each Simulation",
       x="Date", y="Surveillance Pgrm") +
  #scale_colour_manual(values=cbPalette) +
  #scale_color_viridis(option="inferno") +
  facet_wrap(~disease, scales = "free_y")
