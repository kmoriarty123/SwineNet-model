#############################################################
## title: "Plot Seasonality
## author : Kathleen Moriarty
## date_created : 23.05.2022
## desc: 
## output: various summary plots
#############################################################
rm(list=ls()) 

library(ggplot2)
library(ggh4x)
library(viridis)
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

####### compart_data  #######

setwd("Z:/Datasets/NetworkMaterial/SwineNet-model/output/")

# load data from preprocess_compart_no_surv.R

load("all_NS_compart_data.RData") 
load("all_NS_compart_data_sum_long.RData")
load("all_NS_compart_data_sum_long_phipsi.RData")

# SEASONALITY only
all_NS_compart_data_sum_long <- all_NS_compart_data_sum_long %>% 
mutate(name_desc = case_when(name =='med_farm_count' ~'Median Infected Farms', 
                          name == 'med_cum_infected' ~'Median Infected Pigs', 
                          name =='max_farm_count' ~ 'Max Infected Farms',
                          name == 'max_cum_infected' ~ 'Max Infected Pigs' ))
  
# filter for only #infected, asymptomatic, farm_count AND 1.0 phi factor and 1.0 psi factor
s1 <- all_NS_compart_data_sum_long %>% 
  filter(name %in% c('med_farm_count', 'med_cum_infected')) %>% 
  filter(surv_pgrm == 'phi_factor_1.0_psi_factor_1.0') %>% 
ggplot(., 
       aes(x=as.numeric(day), 
           y=value, 
           color=factor(start_date, levels = c('2014-01-01', '2014-05-01', '2019-01-01','2019-05-01')))) +
  #geom_line(position=position_dodge(width=2), size=1.5) +
  geom_point() +
  labs(#title="Seasonal and Annual Start Date Changes",
       #subtitle = "Median Summary Values",
       x="Days Since Disease Introduction",
       color="Start Date",
       y=" ") +
  theme_bw() +
  scale_colour_manual(values=cbPalette) +
  facet_grid2(disease ~ 
               factor(name_desc),#, levels = c('Median Infected Farms', 'Median Infected Pigs')), 
               scales="free_y",
              independent = 'y')

# Max values
all_NS_compart_data_sum_long %>% 
  filter(name %in% c('max_farm_count', 'max_cum_infected')) %>% 
  filter(surv_pgrm == 'phi_factor_1.0_psi_factor_1.0') %>% 
  ggplot(., 
         aes(x=as.numeric(day), y=value, 
             color=factor(start_date, levels = c('2014-01-01', '2014-05-01', '2019-01-01','2019-05-01')))) +
  #geom_line(position=position_dodge(width=2), size=1.5) +
  geom_point() +
  labs(#title="Seasonal and Annual Start Date Changes",
       #subtitle = "Max Summary Values",
       x="Days from Disease Introduction",
       color="Start Date",
       y=" ") +
  theme_bw() +
  scale_colour_manual(values=cbPalette) +
  facet_grid2(disease ~ 
                factor(name_desc),#, levels = c('max_farm_count','max_cum_infected')), 
              scales="free_y",
              independent = 'y')

# Median and Maximum combined
all_NS_compart_data_sum_long %>% 
  filter(name %in% c('med_farm_count','max_farm_count', 'med_cum_infected', 'max_cum_infected')) %>% 
  filter(surv_pgrm == 'phi_factor_1.0_psi_factor_1.0') %>% 
 ggplot(., 
         aes(x=as.numeric(day), 
             y=value, 
             color=factor(start_date, levels = c('2014-01-01', '2014-05-01', '2019-01-01','2019-05-01')))) +
  #geom_line(position=position_dodge(width=2), size=1.5) +
  geom_point() +
  labs(#title="Seasonal and Annual Start Date Changes",
    #subtitle = "Median Summary Values",
    x="Days from Disease Introduction",
    color="Start Date",
    y=" ") +
  theme_bw() +
  scale_colour_manual(values=cbPalette) +
  facet_grid2(disease ~ 
                factor(name_desc, levels = c('Median Infected Farms', 'Max Infected Farms',
                                             'Median Infected Pigs', 'Max Infected Pigs')), 
              scales="free_y",
              independent = 'y')

## Focus just on scenarios that "took off"

# limit to those only with greater than 10
all_NS_compart_data_lim <- all_NS_compart_data %>% 
  group_by(disease, surv_pgrm, start_date, num_run) %>% 
  mutate(max_farm_count = max(farm_count)) %>% 
  filter(max_farm_count > 10) %>% 
  ungroup()

# median/maximum of data
tmp_NS_compart_data_sum_lim <- all_NS_compart_data_lim %>% 
  group_by(disease, date, start_date, surv_pgrm, phi_factor, psi_factor, day) %>% 
  summarize(med_farm_count = median(farm_count),
            med_infected = median(infected),
            med_aysm = median(asymptomatic),
            med_curr_infected = median(curr_infected),
            med_removed = median(removed),
            med_recovered = median(recovered),
            med_cum_infected = median(cum_infected),
            max_farm_count = max(farm_count),
            max_infected = max(infected),
            max_aysm = max(asymptomatic),
            max_curr_infected = max(curr_infected),
            max_cum_infected = max(cum_infected),
            max_removed = max(removed),
            max_recovered = max(recovered)) %>% 
  ungroup()

# make data long on summary type
tmp_NS_compart_data_sum_long_lim <- tmp_NS_compart_data_sum_lim %>% 
  pivot_longer(med_farm_count:max_recovered)

tmp_NS_compart_data_sum_long_lim <- tmp_NS_compart_data_sum_long_lim %>% 
  mutate(name_desc = case_when(name =='med_farm_count' ~'Median Infected Farms', 
                               name == 'med_cum_infected' ~'Median Infected Pigs', 
                               name =='max_farm_count' ~ 'Max Infected Farms',
                               name == 'max_cum_infected' ~ 'Max Infected Pigs' ))

# filter for only #infected, asymptomatic, farm_count AND 1.0 phi factor and 1.0 psi factor
s2 <- tmp_NS_compart_data_sum_long_lim %>% 
  filter(name %in% c('med_farm_count', 'med_cum_infected')) %>% 
  filter(surv_pgrm == 'phi_factor_1.0_psi_factor_1.0') %>% 
  ggplot(., 
         aes(x=as.numeric(day), 
             y=value, 
             color=factor(start_date, levels = c('2014-01-01', '2014-05-01', '2019-01-01','2019-05-01')))) +
 geom_point() +
  labs(#title="Seasonal and Annual Start Date Changes",
    #subtitle = "Median Summary Values",
    x="Days Since Disease Introduction",
    color="Start Date",
    y=" ") +
  theme_bw() +
  theme(plot.margin = margin(6, 0, 6, 0)) +
  scale_colour_manual(values=cbPalette) +
  facet_grid2(disease ~ 
                factor(name_desc),#, levels = c('Median Infected Farms', 'Median Infected Pigs')), 
              scales="free_y",
              independent = 'y')


# plot proportion that take off based on start_date

load('all_total_outbreak_data.RData')

all_total_outbreak_data %>% 
  filter(surv_pgrm =='phi_factor_1.0_psi_factor_1.0') %>% 
  ggplot(., aes(x=as.factor(start_date), y=prop_under_10,
                fill=factor(start_date, 
                             levels = c('2014-01-01', '2014-05-01', '2019-01-01','2019-05-01')))) +
  geom_col() +
  labs(#title="Seasonal and Annual Start Date Changes",
    #subtitle = "Median Summary Values",
    x="",
    fill="Start Date",
    y="Proporiton of Simulations") +
  theme_bw() +
  theme(axis.ticks.x = element_blank(),
        axis.text.x = element_blank())+
  scale_fill_manual(values=cbPalette) +
  geom_text(aes(label = round(prop_under_10, digits=2)), vjust = -0.3)+
  facet_wrap(~disease)

# To combine plots
library(ggpubr)

ggarrange(s1, s2,
          align='v', labels=c('A', 'B'),
          common.legend = T,
          legend='right')

