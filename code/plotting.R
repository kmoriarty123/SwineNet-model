#############################################################
## title: "Plots for SwineNet Model Output Data"
## author : Kathleen Moriarty
## date_created : 08.04.2022
## desc: 
## output: various summary plots
#############################################################

rm(list=ls()) 
library(dplyr)
library(tidyr)
setwd("Z:/Datasets/NetworkMaterial/SwineNet-model/output/")
folder = "APP/2019_5_1/"

load(paste0(folder, "all_compartment.RData"))
load(paste0(folder, "all_compart_data_sum.RData"))
load(paste0(folder, "all_first_detect.RData"))
load(paste0(folder, "all_outbreak_data.RData"))

library(ggplot2)
library(viridis)
# The palette with grey:
cbPalette <- c("#999999", 
               "#E69F00", # yellowy orange
               "#56B4E9", # sky blue
               "#009E73", # dark green 
               "#F0E442", # yellow
               "#0072B2", # blue
               "#D55E00", # orange
               "#CC79A7", # mauve
               "#000000", 
               "#7570b3" )# purply blue

# Cumulative Infected Pigs
ggplot(all_compart_data_sum, aes(x=date, 
                             y=median_cum_infected, 
                             color=surv_pgrm)) +
  geom_line(size=1) +
  theme_minimal() + 
  theme(axis.text.x = element_text(angle = 90, vjust = 0.5, hjust=1)) +
  scale_x_date(breaks = all_compart_data_sum$date[seq(1, length(unique(all_compart_data_sum$date)), by = 14)]) +
  labs(title = "Median Number of Cumulative Infected Pigs by Surveillance Program",
       x="Date", y="Median Number of Cumulative Infected Pigs") +
  #scale_colour_manual(values=cbPalette)
  scale_color_viridis(discrete=TRUE)

# Cumulative Infected Pig - separated by surv_type
all_compart_data_grp <- all_compart_data_sum %>% 
  group_by(surv_type) %>% 
  mutate(line_type = match(surv_pgrm, unique(surv_pgrm)))

ggplot(all_compart_data_grp, aes(x=date, 
                             y=median_cum_infected, 
                             color=surv_type)) +#,
                             #linetype=as.factor(line_type))) +
  geom_line(size=1) +
  theme_minimal() + 
  theme(axis.text.x = element_text(angle = 90, vjust = 0.5, hjust=1)) +
  scale_x_date(breaks = all_compart_data_grp$date[seq(1, length(unique(all_compart_data_grp$date)), by = 14)]) +
  labs(title = "Median Number of Cumulative Infected Pigs by Surveillance Program",
       x="Date", y="Median Number of Cumulative Infected Pigs") +
  #scale_colour_manual(values=cbPalette)
  scale_color_viridis(discrete=TRUE)

ggplot(all_compart_data_grp, aes(x=date, 
                                 y=median_cum_infected, 
                                 color=surv_type)) +#,
  #linetype=as.factor(line_type))) +
  #geom_jitter() +'
  geom_point() +
  theme_minimal() + 
  theme(axis.text.x = element_text(angle = 90, vjust = 0.5, hjust=1)) +
  scale_x_date(breaks = all_compart_data_grp$date[seq(1, length(unique(all_compart_data_grp$date)), by = 14)]) +
  labs(title = "Median Number of Cumulative Infected Pigs by Surveillance Program",
       x="Date", y="Median Number of Cumulative Infected Pigs") +
  #scale_colour_manual(values=cbPalette)
  scale_color_viridis(discrete=TRUE)

# Median infected farm
ggplot(all_compart_data_sum, aes(x=date, 
                             y=median_farm_count, 
                             color=surv_type)) +
  geom_jitter(size=1) +
  theme_minimal() + 
  theme(axis.text.x = element_text(angle = 90, vjust = 0.5, hjust=1)) +
  scale_x_date(breaks = all_compart_data_sum$date[seq(1, length(unique(all_compart_data_sum$date)), by = 14)]) +
  labs(title = "Median Number of Farms Infected by Surveillance Program",
       x="Date", y="Median Number of Infected Farms") +
  #scale_colour_manual(values=cbPalette)
  scale_color_viridis(discrete=TRUE)

ggplot(all_compart_data_sum, aes(x=date, 
                             y=median_isolated, 
                             color=surv_pgrm)) +
  geom_line(size=1) +
  theme_minimal() + 
  theme(axis.text.x = element_text(angle = 90, vjust = 0.5, hjust=1)) +
  scale_x_date(breaks = all_compart_data_sum$date[seq(1, length(unique(all_compart_data_sum$date)), by = 14)]) +
  labs(title = "Median Number of Detected Pigs by Surveillance Program",
       x="Date", y="Median Number of Detected Pigs") +
  #scale_colour_manual(values=cbPalette)
  scale_color_viridis(discrete=TRUE)

ggplot(all_compart_data_sum, aes(x=date, 
                             y=median_quarantined, 
                             color=surv_pgrm)) +
  geom_line(size=1) +
  theme_minimal() + 
  theme(axis.text.x = element_text(angle = 90, vjust = 0.5, hjust=1)) +
  scale_x_date(breaks = all_compart_data_sum$date[seq(1, length(unique(all_compart_data_sum$date)), by = 14)]) +
  labs(title = "Median Number of Quarantined Pigs by Surveillance Program",
       x="Date", y="Median Number of Quarantined Pigs") +
  #scale_colour_manual(values=cbPalette)
  scale_color_viridis(discrete=TRUE)

# prepare data to look at different quarantining (exposed vs susceptibles moved to quarantine)
all_compart_data_sum_long <- all_compart_data_sum %>% 
  select(date, surv_pgrm, surv_type, median_quarantined_e, median_quarantined_s) %>%
  pivot_longer(cols=starts_with("median_"), names_to = "quarantine_type", values_to = "median")

ggplot(all_compart_data_sum_long, aes(x=date, 
                             y=median, 
                             color=surv_pgrm,
                             linetype=quarantine_type)) +
  geom_line(size=1) +
  theme_minimal() + 
  theme(axis.text.x = element_text(angle = 90, vjust = 0.5, hjust=1)) +
  scale_x_date(breaks = all_compart_data_sum$date[seq(1, length(unique(all_compart_data_sum$date)), by = 14)]) +
  labs(title = "Median Number of Quarantined Pigs by Surveillance Program",
       x="Date", y="Median Number of Quarantined Pigs") +
  #scale_colour_manual(values=cbPalette)
  scale_color_viridis(discrete=TRUE)


#### First detect plots #### 

ggplot(all_first_detect, aes(x=med_date, 
                             y=surv_pgrm, 
                             color=med_farm_count,
                             size=med_cum_inf)) +
  geom_point() +
  theme_minimal() + 
  theme(axis.text.x = element_text(angle = 90, vjust = 0.5, hjust=1)) +
  scale_x_date(breaks = all_compart_data_sum$date[seq(1, length(unique(all_compart_data_sum$date)), by = 14)]) +
  labs(title = "Median Date, Cum_Inf, Inf_farm at First Detection",
       x="Date", y="Surveillance Pgrm") +
  #scale_colour_manual(values=cbPalette)
  scale_color_viridis(option="inferno")

# without "no_surv" program
all_first_detect %>% filter(surv_pgrm != "no_surv_none") %>%
ggplot(aes(x=med_date, 
                             y=surv_pgrm, 
                             color=med_farm_count,
                             size=med_cum_inf)) +
  geom_point() +
  theme_minimal() + 
  theme(axis.text.x = element_text(angle = 90, vjust = 0.5, hjust=1)) +
  scale_x_date(breaks = all_compart_data_sum$date[seq(1, length(unique(all_compart_data_sum$date)), by = 14)]) +
  labs(title = "Median Date, Cum_Inf, Inf_farm at First Detection",
       x="Date", y="Surveillance Pgrm") +
  #scale_colour_manual(values=cbPalette)
  scale_color_viridis(option="inferno")

#### Outbreak Size Plots #### 
ggplot(all_outbreak_data, aes(x=surv_pgrm, 
           y=prop_under_20)) +
  geom_point() +
  theme_minimal()+
  labs(title = "Proportion of With Under 20 Infected Farms",
       y="Proportion", x="Surveillance Pgrm")+ 
  coord_flip()

ggplot(all_outbreak_data, aes(x=surv_pgrm, 
                              y=prop_no_new_inf_20)) +
  geom_point() +
  theme_minimal()+
  labs(title = "Proportion of Runs That Died Out",
       subtitle = "Defined as no new infected pigs in last 20 days",
       y="Proportion", x="Surveillance Pgrm")+ 
  coord_flip()

##### Just ONE surveillance Program

i=1 #farm_surv 0.05
# read in file
tmp_compart_df <- read.table(list_of_compart_files[i],
                             header = FALSE,
                             sep = ",")
# set col names
colnames(tmp_compart_df) <- compart_colnames

tmp_compart_df$num_run <- as.factor(tmp_compart_df$num_run)

ggplot(tmp_compart_df, aes(x=date, y = farm_count, color=num_run)) + 
  geom_point(show.legend = FALSE)

ggplot(tmp_compart_df, aes(x=date, y = isolated, color=num_run)) + 
  geom_point(show.legend = FALSE)

tmp_compart_df_grp <- tmp_compart_df %>% group_by(date) %>% 
  summarize(med_f_c = median(farm_count),
            med_iso = median(isolated),
            iso_25 = quantile(isolated, probs = 0.25),
            iso_75 = quantile(isolated, probs = 0.75)) %>% 
  ungroup()

tmp_compart_df_grp <- tmp_compart_df_grp %>% 
  mutate(date = as.Date(date))

ggplot(tmp_compart_df_grp, aes(x=date, y = med_f_c)) + 
  geom_point() + 
  theme(axis.text.x = element_text(angle = 90, vjust = 0.5, hjust=1)) +
  scale_x_date(breaks = tmp_compart_df_grp$date[seq(1, length(unique(tmp_compart_df_grp$date)), by = 14)])

ggplot(tmp_compart_df_grp, aes(x=date, y = iso_75)) + 
  geom_point() + 
  theme(axis.text.x = element_text(angle = 90, vjust = 0.5, hjust=1)) +
  scale_x_date(breaks = tmp_compart_df_grp$date[seq(1, length(unique(tmp_compart_df_grp$date)), by = 14)])

##### ALL surveillance Program Data #####
### Boxplots of ranges on the last day ###

all_compart_data_last_date <- 
  all_compart_data %>% filter(date == "2014-06-30")

ggplot(all_compart_data_last_date, aes(x=surv_pgrm, y=farm_count)) + 
  geom_boxplot() +
  theme(axis.text.x = element_text(angle = 90, vjust = 0.5, hjust=1)) 

ggplot(all_compart_data_last_date, aes(x=surv_pgrm, y=cum_infected)) + 
  geom_boxplot() +
  theme(axis.text.x = element_text(angle = 90, vjust = 0.5, hjust=1)) 

ggplot(all_compart_data_last_date, aes(x=surv_pgrm, y=removed)) + 
  geom_boxplot() +
  theme(axis.text.x = element_text(angle = 90, vjust = 0.5, hjust=1)) 

ggplot(all_compart_data_last_date, aes(x=surv_pgrm, y=recovered)) + 
  geom_boxplot() +
  theme(axis.text.x = element_text(angle = 90, vjust = 0.5, hjust=1)) 

