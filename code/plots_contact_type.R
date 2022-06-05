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

####### Plot contact_data #######

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

cbPalette3 <- c(#"#999999", # grey
  #"#009E73", # yellowy orange
  "#F0E442", # sky blue
  "#56B4E9", # green 
  "#CC79A7", # yellow
  "#E69F00", # blue
  "#0072B2", # mauve
  "#D55E00", # orangey red
  "#000000", 
  "#7570b3" )

surv_level = c('0.25',
               '1.0',
               '10.0',
               '50.0',
               '200.0')

contact_name_level = c('Direct Transfer',
                       'Direct Truck Share',
                       'Indirect Truck Share',
                       'External Truck',
                       'Geographic',
                       'Within Farm')

list_surv_pgrm2 = c('phi_factor_1.0_psi_factor_1.0', 
                    'phi_factor_1.0_psi_factor_200.0',
                    'phi_factor_200.0_psi_factor_1.0')

### load data
load('2019-05-01_no_surv_contact_cum_sum.RData') #total_rows_join_cum_sum
load('all_NS_compart_data_sum_long_phipsi.RData')
load('2019-05-01_no_surv_contact_prop.RData')
load('2019-05-01_no_surv_contact_prop_lim.RData')
load("total_NS_contact_sum.RData")
load("total_NS_contact_sum_take_off.RData")

# Adjust Psi - Median Cum Infected

# filter plot for only truck transmission and psi factors
total_rows_join_cum_sum %>% 
  filter(contact_name %in% c('Direct Truck Share',
                             'Indirect Truck Share',
                             'External Truck',
                             'Geographic'),
         phi_factor == '1.0',
         psi_factor %in% c('0.25','1.0','10.0','50.0','200.0')) %>% 
  ggplot(., 
         aes(x=as.numeric(day), 
             y=med_cum_inf, 
             color=factor(psi_factor, levels = surv_level))) +
  geom_point()+
  labs(title="Median Cumulative Sum of Infected Pigs by Mode of Truck Transmission",
       subtitle = "Adjusting Psi Parameter (start date: 2019-05-01)",
       color="Factor of Psi",
       x="Days Since Introduction",
       y="Cumulative Infected Pigs") +
  theme_bw() +
  scale_colour_manual(values=cbPalette) +
  facet_grid2(disease~contact_name, 
              scales="free_y",
              independent='y')

# Adjust Phi - Median Cum Infected

total_rows_join_cum_sum %>% 
  filter(contact_name %in% c('Direct Truck Share',
                             'Indirect Truck Share',
                             'External Truck',
                             'Geographic'),
         #disease == 'ASF',
         #day < 100,
         #start_date=='2019-05-01',
         psi_factor == '1.0',
         phi_factor %in% c('0.25','1.0','10.0','50.0','200.0')) %>% 
  ggplot(., 
         aes(x=as.numeric(day), 
             y=med_cum_inf, 
             color=factor(phi_factor, levels = surv_level))) +
  geom_point()+
  labs(title="Median Cumulative Sum of Infected Pigs by Mode of Truck Transmission",
       subtitle = "Adjusting Phi Parameter (start date: 2019-05-01)",
       color="Factor of Phi",
       x="Days Since Introduction",
       y="Cumulative Infected Pigs") +
  theme_bw() +
  #theme(axis.text.x = element_text(angle = 90, vjust = 0.5, hjust=1)) +
  scale_colour_manual(values=cbPalette) +
  facet_grid2(disease~contact_name, 
              scales="free_y",
              independent='y')

# Adjust Psi - Max Cum Infected

# filter plot for only truck transmission and psi factors
total_rows_join_cum_sum %>% 
  filter(contact_name %in% c('Direct Truck Share',
                             'Indirect Truck Share',
                             'External Truck',
                             'Geographic'),
         phi_factor == '1.0',
         psi_factor %in% c('0.25','1.0','10.0','50.0','200.0')) %>% 
  ggplot(., 
         aes(x=as.numeric(day), 
             y=max_cum_inf, 
             color=factor(psi_factor, levels = surv_level))) +
  geom_point()+
  labs(title="Maximum Cumulative Sum of Infected Pigs by Mode of Truck Transmission",
       subtitle = "Adjusting Psi Parameter (start date: 2019-05-01)",
       color="Factor of Psi",
       x="Days Since Introduction",
       y="Cumulative Infected Pigs") +
  theme_bw() +
  scale_colour_manual(values=cbPalette) +
  facet_grid2(disease~contact_name, 
              scales="free_y",
              independent='y')

# Adjust Phi - Maximum Cum Infected

total_rows_join_cum_sum %>% 
  filter(contact_name %in% c('Direct Truck Share',
                             'Indirect Truck Share',
                             'External Truck',
                             'Geographic'),
         #disease == 'ASF',
         #day < 100,
         #start_date=='2019-05-01',
         psi_factor == '1.0',
         phi_factor %in% c('0.25','1.0','10.0','50.0','200.0')) %>% 
  ggplot(., 
         aes(x=as.numeric(day), 
             y=max_cum_inf, 
             color=factor(phi_factor, levels = surv_level))) +
  geom_jitter()+
  labs(title="Maximum Cumulative Sum of Infected Pigs by Mode of Truck Transmission",
       subtitle = "Adjusting Phi Parameter (start date: 2019-05-01)",
       color="Factor of Phi",
       x="Days Since Introduction",
       y="Cumulative Infected Pigs") +
  theme_bw() +
  #theme(axis.text.x = element_text(angle = 90, vjust = 0.5, hjust=1)) +
  scale_colour_manual(values=cbPalette) +
  facet_grid2(disease~contact_name, 
              scales="free_y",
              independent='y')

# Looking at Factor of Phi/Psi and Median Cum Sum Infected Pigs

all_NS_compart_data_sum_long_phipsi %>% 
  filter(value %in% c('0.25', '1.0', '10.0','50.0','200.0'),
         start_date=='2019-05-01') %>% 
  ggplot(., 
         aes(x=as.numeric(day), 
             y=med_cum_infected, 
             color=factor(value, levels = surv_level))) +
  geom_jitter(height = 0.05, width=0.5) +
  labs(title="Median Cumulative Infected by Phi and Psi Factor",
       subtitle = "Start Date: 2019-05-01",
       color="Factor",
       x="Days Since Introduction",
       y="Number of Infected Pigs") +
  theme_bw() +
  scale_colour_manual(values=cbPalette) +
  facet_grid(disease~name, scales="free")

# Looking at Factor of Phi/Psi and Cum Sum Maximum Infected Pigs

all_NS_compart_data_sum_long_phipsi %>% 
  filter(value %in% c('0.25', '1.0', '10.0','50.0','200.0'),
         start_date=='2019-05-01') %>% 
  ggplot(., 
         aes(x=as.numeric(day), 
             y=max_cum_infected, 
             color=factor(value, levels = surv_level))) +
  geom_jitter(height = 0.01) +
  labs(title="Maximum Cumulative Infected by Phi and Psi Factor",
       subtitle = "Start Date: 2019-05-01",
       color="Factor",
       x="Days Since Introduction",
       y="Number of Infected Pigs") +
  theme_bw() +
  scale_colour_manual(values=cbPalette) +
  facet_grid(disease~name, scales="free")

# Zooming into Factor of Phi

all_NS_compart_data_sum_long_phipsi %>% 
  filter(value %in% c('0.25', '1.0', '10.0','50.0','200.0'),
         start_date=='2019-05-01',
         disease=="ASF",
         day > 160,
         day < 200) %>% 
  ggplot(., 
         aes(x=as.numeric(day), 
             y=med_cum_infected, 
             color=factor(value, levels = surv_level))) +
  geom_jitter(height = 0.01) +
  labs(title="Median Cumulative Infected by Phi and Psi Factor",
       subtitle = "ASF Only and 160-200 Days Since Infection",
       color="Factor",
       x="Days Since Introduction",
       y="Number of Infected Pigs") +
  theme_bw() +
  scale_colour_manual(values=cbPalette) +
  facet_grid(disease~name, scales="free")

# Plotting Proportion of spread per route of transmission

no_surv_contact_prop %>% 
  ggplot(., aes(x=day, y=prop_cum_inf, 
                fill=factor(contact_name, levels = contact_name_level))) +
  geom_col() +
  theme_bw() +
  labs(fill="Transmission Route",
       x="Days Since Introduction",
       y="Proportion") +
  scale_fill_manual(values=cbPalette2) +
  facet_grid2(disease~surv_pgrm_name)

#### Plotting Proportion of spread per route of transmission WITHOUT WITHIN FARM

no_surv_contact_prop_lim %>% 
  ggplot(., aes(x=day, y=prop_cum_inf, 
                fill=factor(contact_name, levels = contact_name_level))) +
  geom_col() +
  theme_bw() +
  labs(fill="Transmission Route",
       x="Days Since Introduction",
       y="Proportion") +
  scale_fill_manual(values=cbPalette2) +
  facet_grid2(disease~surv_pgrm_name)

## Plot median sum num infected by contact type by start date and disease
ggplot(total_NS_contact_sum, 
       aes(x=surv_pgrm, y=med_sum_num_inf, fill=contact_type))+
  geom_col() +
  facet_grid2(disease ~ start_date, scales = 'free', independent = 'all')

# same as above but with only phi_factor_1.0_psi_factor_1.0

total_NS_contact_sum_main <- total_NS_contact_sum %>% 
  filter(surv_pgrm %in% list_surv_pgrm2) 

total_NS_contact_sum_main %>% 
  filter(surv_pgrm == 'phi_factor_1.0_psi_factor_1.0' ) %>% 
  ggplot(., aes(x=as.factor(start_date), y=med_sum_num_inf, fill=contact_type))+
  geom_col()  +
  theme_bw() +
  scale_fill_manual(values=cbPalette) +
  facet_grid2(~disease, scales = 'free', independent = "all")

# 3 main phi psi factors for only May 2019 start
ggplot(total_NS_contact_sum_main, aes(x=as.factor(start_date), y=med_sum_num_inf, fill=contact_type))+
  geom_col()  +
  theme_bw() +
  scale_fill_manual(values=cbPalette) +
  facet_grid2(disease ~ surv_pgrm, scales = 'free', independent = "all")


###### NOW ONLY LOOKING AT THOSE RUNS THAT TOOK OFF #####
total_NS_contact_sum_main_take_off <- total_NS_contact_sum_take_off %>% 
  filter(surv_pgrm %in% list_surv_pgrm2) 

total_NS_contact_sum_main_take_off %>% 
  filter(surv_pgrm == 'phi_factor_1.0_psi_factor_1.0' ) %>% 
  ggplot(., aes(x=as.factor(start_date), y=med_sum_num_inf, fill=contact_type))+
  geom_col()  +
  theme_bw() +
  scale_fill_manual(values=cbPalette) +
  facet_grid2(~disease, scales = 'free', independent = "all")

# 3 main phi psi factors for only May 2019 start
ggplot(total_NS_contact_sum_main, aes(x=as.factor(start_date), y=med_sum_num_inf, fill=contact_type))+
  geom_col()  +
  theme_bw() +
  scale_fill_manual(values=cbPalette) +
  facet_grid2(disease ~ surv_pgrm, scales = 'free', independent = "all")

# Plotting Proportion of spread per route of transmission from those that "took off"

no_surv_contact_prop_take_off %>% 
  ggplot(., aes(x=day, y=prop_cum_inf, 
                fill=factor(contact_name, levels = contact_name_level))) +
  geom_col() +
  theme_bw() +
  labs(fill="Transmission Route",
       x="Days Since Introduction",
       y="Proportion") +
  scale_fill_manual(values=cbPalette2) +
  facet_grid2(disease~surv_pgrm_name)

#### Plotting Proportion of spread per route of transmission WITHOUT WITHIN FARM from those that "took off"

no_surv_contact_prop_lim_take_off %>% 
  ggplot(., aes(x=day, y=prop_cum_inf, 
                fill=factor(contact_name, levels = contact_name_level))) +
  geom_col() +
  theme_bw() +
  labs(fill="Transmission Route",
       x="Days Since Introduction",
       y="Proportion") +
  scale_fill_manual(values=cbPalette2) +
  facet_grid2(disease~surv_pgrm_name)

