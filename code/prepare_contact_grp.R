#############################################################
## title: "Preprocess Contact Type Groupings
## author : Kathleen Moriarty
## date_created : 29.05.2022
## output: .RData files:

#############################################################

rm(list=ls())
library(dplyr)
setwd("Z:/Datasets/NetworkMaterial/SwineNet-model/output/")
# load data
list_disease = c("APP", "ASF", "PRRS")
list_disease = c("APP")
start_date_lim = '2019-05-01' 
list_start_date = c('2014_1_1','2014_5_1','2019_1_1','2019_5_1')
list_start_date = c('2019_5_1')
# for storing results
total_contact_data_sum = data.frame()
total_contact_data = data.frame()
all_total_contact_data_sum = data.frame()
all_total_contact_data = data.frame()

for (j in 1:(length(list_disease))){
  for (k in 1:(length(list_start_date))){
    
    disease <- list_disease[j]
    start_date <- list_start_date[k]
    print(disease)
    print(start_date)
    
    # folders for no_surv and all the sensitivity folders
    folder1 = paste0(disease, '/', start_date, "/no_surv")
    folder2 = paste0(disease, '/', start_date, "/sensitivity")
    
    # used to subset the directory name for the surv_pgrm_title
    contact_filename <- '/results_by_contact_grp_all.txt'
    
    total_contact_data <- data.frame()
    
    # grab list of results_by_compart_all.txt files
    list_of_contact_files1 <- list.files(path = folder1, 
                                        recursive = TRUE,
                                        pattern = "results_by_contact_grp_all.txt", 
                                        full.names = TRUE)
    
    list_of_contact_files2 <- list.files(path = folder2, 
                                        recursive = TRUE,
                                        pattern = "results_by_contact_grp_all.txt", 
                                        full.names = TRUE)
    
    # combine the no_surv with sensitivty files
    list_of_contact_files = append(list_of_contact_files1, list_of_contact_files2)
    
    # Preparing compartment txt files
    contact_colnames <- c('date', 'contact_type', 'num_inf_pigs','num_run')
    
    for (i in 1:(length(list_of_contact_files))){
      print(i)
      # read in file
      tmp_contact_df <- read.table(list_of_contact_files[i], 
                                   header = FALSE, 
                                   sep = ",")
      
      # set name of surveillance program
      file_name_strings <- stringr::str_split(list_of_contact_files[i], "/")
      surv_type <- file_name_strings[[1]][3]
      surv_pgrm_name <- file_name_strings[[1]][4]
      
      # set col names
      colnames(tmp_contact_df) <- contact_colnames
      
      # Create cumulative sum of infected by contact type
      #tmp_contact_df <- tmp_contact_df %>% 
      #  group_by(contact_type, num_run) %>% 
      #  arrange(date) %>% 
      #  mutate(cum_num_inf = cumsum(num_inf_pigs)) %>% 
      #  ungroup()
      
      tmp_contact_df$disease <- disease
      tmp_contact_df$surv_pgrm <- surv_pgrm_name
      tmp_contact_df$start_date <- as.Date(start_date, "%Y_%m_%d")
      
      # create new "day" to difference from start
      tmp_contact_df <- tmp_contact_df %>% 
        mutate(date = as.Date(date)) %>% 
        mutate(day = as.integer(difftime(date, start_date, units = "days")))
      
      total_contact_data <- rbind(tmp_contact_df, total_contact_data)
      
    }
    
    contact_data <- total_contact_data %>% 
      mutate(contact_name = case_when(contact_type == 'f' ~ 'Within Farm',
                                      contact_type == 'd' ~ 'Direct Transfer',
                                      contact_type == 'g' ~ 'Geographic',
                                      contact_type == 't' ~ 'Direct Truck Share',
                                      contact_type == 'i' ~ 'Indirect Truck Share',
                                      contact_type == 'e' ~ 'External Truck'))
    
    # Save individual disease + start_date raw data to file
    save(contact_data, file= paste0(disease, '/', start_date, "/contact_data.RData"))
    
    # median/maximum of data across num_runs
    #contact_data_sum <- contact_data %>% 
    #  group_by(disease, start_date, date, day, surv_pgrm, contact_name) %>% 
    #  summarize(med_num_inf_pigs = median(num_inf_pigs),
    #            max_num_inf_pigs = max(num_inf_pigs),
    #            med_cum_inf = median(cum_num_inf),
    #            mean_num_inf_pigs = mean(num_inf_pigs),
    #            mean_cum_inf = mean(cum_num_inf)) %>% 
    #  ungroup()
    
    # make data longer based on median/max values
    #contact_data_sum_long <- contact_data_sum %>% 
    #  pivot_longer(med_num_inf_pigs:mean_cum_inf)
    
    # bind all diseases
    all_total_contact_data <- rbind(all_total_contact_data, contact_data)
    #all_total_contact_data_sum <- rbind(all_total_contact_data_sum, contact_data_sum)
    
  }
}

# save combined raw data to file
save(all_total_contact_data, file="total_contact_data.RData")
#load("total_contact_data.RData")
#save(all_total_contact_data_sum, file="all_total_contact_data_sum.RData")

#####
## Fill the missing days in which no transfer of pathogen was simulated
## Only care about the 2019_5_1 start_date, in which I have run all sensitivity
#####

# Limit all_total_contact_data to 2019-05-01
total_contact_data_2019_5 <- all_total_contact_data %>% 
  filter(start_date == '2019-05-01') 
  
# Create df with all possible dates
list_surv_pgrm_df <- all_total_contact_data %>% distinct(surv_pgrm)
list_surv_pgrm <- list_surv_pgrm_df$surv_pgrm
list_contact_type_df <- all_total_contact_data %>% distinct(contact_type)
list_contact_type <- list_contact_type_df$contact_type
total_rows = data.frame()
n=244

# create dummy dataframe 
for (i in 1:(length(list_disease))){
  for (j in 1:(length(list_surv_pgrm))){
    for (k in 1:(length(list_contact_type))){
      
        tmp_df <- data.frame('disease' = list_disease[i],
                           'surv_pgrm' = list_surv_pgrm[j],
                           'contact_type' = list_contact_type[k],
                           'day' = 0:n)
      
      rows= c(1:nrow(tmp_df))
      # repeat rows for each simulation row
      tmp_df <- tmp_df[rep(rows, 1000),]
      #create variable for num_run
      tmp_df <- tmp_df %>% 
        group_by(day) %>% 
        mutate(num_run = 1:1000)
      
      
      total_rows = rbind(tmp_df, total_rows)
    }
  }
}

#load('dummy_simulation_template.RData')
save(total_rows, file="dummy_simulation_template.RData")

# merge this dataframe with contact data
total_rows_join <- total_contact_data_2019_5  %>% 
  full_join(total_rows,
            by = c("disease" = "disease",
                   "surv_pgrm" = "surv_pgrm",
                   "contact_type" = "contact_type",
                   "day" = "day",
                   "num_run" = "num_run"))

# Update num_inf_rows to 0 where NA
total_rows_join <- total_rows_join %>% 
  mutate(num_inf_pigs = ifelse(is.na(num_inf_pigs), 0, num_inf_pigs)) %>% 
  select(-c(date, start_date)) %>% 
  mutate(contact_name = case_when(contact_type == 'f' ~ 'Within Farm',
                                contact_type == 'd' ~ 'Direct Transfer',
                                contact_type == 'g' ~ 'Geographic',
                                contact_type == 't' ~ 'Direct Truck Share',
                                contact_type == 'i' ~ 'Indirect Truck Share',
                                contact_type == 'e' ~ 'External Truck'))

# Check the table
tmp <- total_contact_data_2019_5 %>%
  filter(disease == 'APP', 
         surv_pgrm == 'psi_factor_4.0',
         contact_type == 't')

tmp <- total_rows %>%
  filter(disease == 'APP', 
         surv_pgrm == 'eta_factor_50.0',
         contact_type == 't',
         day == 244)

tmp <- total_rows_join %>%
  filter(disease == 'APP', 
         surv_pgrm == 'eta_factor_50.0',
         contact_type == 't',
         day == 244)

save(total_rows_join, file=paste0(start_date_lim, "contact_data_filled.RData"))
#load('2019-05-01contact_data_filled.RData')

#####
## Run summary Stats on the data
#####

# Don't need total_rows nor total_contact_data sets anymore
total_rows = NULL
total_contact_data_2019_5 = NULL

# Create cumulative values
total_rows_join_cum <- total_rows_join %>% 
  group_by(disease, 
           contact_name, 
           surv_pgrm, 
           num_run) %>% 
  arrange(day) %>% 
  mutate(cum_num_inf = cumsum(num_inf_pigs)) %>% 
  ungroup()

# check some rows
tmp <- total_rows_join_cum %>% 
  filter(surv_pgrm == "eta_factor_50.0",
         disease == "ASF",
         contact_name == "Direct Truck Share",
         num_run == 393)

# Create median
total_rows_join_cum_sum <- total_rows_join_cum %>% 
  group_by(disease, day, surv_pgrm, contact_name) %>% 
  summarize(med_num_inf_pigs = median(num_inf_pigs),
            max_num_inf_pigs = max(num_inf_pigs),
            med_cum_inf = median(cum_num_inf),
            max_cum_inf = max(cum_num_inf)) %>% 
  ungroup()

save(total_rows_join_cum_sum, file=paste0(start_date_lim, "contact_data_cum_sum.RData"))

#####
## For proportions of routes of transmission
#####

# Add total daily total median cumulative inf # of pigs column
contact_data_prop <- total_rows_join_cum_sum %>% 
  group_by(disease, day, surv_pgrm) %>% 
  mutate(daily_total_cum_inf_pigs = sum(med_cum_inf)) %>% 
  ungroup()

# Calculate the proportion for each contact_type for that day
contact_data_prop <- contact_data_prop %>% 
  mutate(prop_cum_inf = med_cum_inf/daily_total_cum_inf_pigs,
         prop_cum_inf = ifelse(is.na(prop_cum_inf), 0, prop_cum_inf))

save(contact_data_prop, file=paste0(start_date_lim, "contact_data_prop.RData"))

#####################################################################
# LIMIT the observations to only the simulations that took off
#####################################################################

load('list_scenarios_take_off.RData')
load("total_contact_data.RData")
load('num_run_take_off_no_surv.RData')

total_compart_data_from_no_surv_take_off <- all_total_compart_data %>% 
  inner_join(num_run_take_off_no_surv, by=c('disease' = 'disease', 
                                            'num_run' = 'num_run',
                                            'start_date' = 'start_date'))

# filter for only the scenarios and num_runs that "took off"
# contact_data_take_off_old <- all_total_contact_data %>% 
#   inner_join(list_scenarios_take_off,
#              by=c("disease", 'start_date', 'surv_pgrm', 'num_run'))

contact_data_take_off <- all_total_contact_data %>% 
  inner_join(num_run_take_off_no_surv, by=c('disease' = 'disease', 
                                            'num_run' = 'num_run',
                                            'start_date' = 'start_date'))

#contact_data_take_off_sum <- contact_data_take_off %>% 
#  filter(num_inf_pigs > 0) %>% 
#  group_by(disease, surv_pgrm, start_date, num_run, contact_type) %>% 
#  summarize(sum_num_inf = sum(num_inf_pigs)) %>% 
#  ungroup()

#total_NS_contact_sum_take_off <- total_NS_contact_sum_num_run_take_off %>% 
#  group_by(disease, surv_pgrm, start_date, contact_type) %>% 
#  summarize(med_sum_num_inf = median(sum_num_inf)) %>% 
#  ungroup()

#save(total_NS_contact_sum_take_off, file='total_NS_contact_sum_take_off.RData')

# Filter total_rows_join to only the scenarios that 'took off'

list_take_off_lim <- num_run_take_off_no_surv %>% 
  filter(start_date == start_date_lim) %>% 
  select(-c(start_date))

total_rows_join_take_off <- total_rows_join %>% 
  inner_join(list_take_off_lim,
             by=c("disease", 'num_run'))

# Create cumulative values
total_rows_join_take_off_cum <- total_rows_join_take_off %>% 
  group_by(disease, 
           contact_name, 
           surv_pgrm, 
           num_run) %>% 
  arrange(day) %>% 
  mutate(cum_num_inf = cumsum(num_inf_pigs)) %>% 
  ungroup()

# check some rows
tmp <- total_rows_join_take_off_cum %>% 
  filter(surv_pgrm == "eta_factor_50.0",
         disease == "PRRS",
         contact_name == "Direct Truck Share"
         )

# Create median
total_rows_join_take_off_cum_sum <- total_rows_join_take_off_cum %>% 
  group_by(disease, day, surv_pgrm, contact_name) %>% 
  summarize(med_num_inf_pigs = median(num_inf_pigs),
            max_num_inf_pigs = max(num_inf_pigs),
            med_cum_inf = median(cum_num_inf),
            max_cum_inf = max(cum_num_inf)) %>% 
  ungroup()

save(total_rows_join_take_off_cum_sum, file=paste0(start_date_lim, "contact_take_off_cum_sum.RData"))

# For proportions of routes of transmission
contact_prop_take_off <- total_rows_join_take_off_cum_sum %>% 
  group_by(disease, day, surv_pgrm) %>% 
  mutate(daily_total_cum_inf_pigs = sum(med_cum_inf)) %>% 
  ungroup()

contact_prop_take_off <- contact_prop_take_off %>% 
  mutate(prop_cum_inf = med_cum_inf/daily_total_cum_inf_pigs,
         prop_cum_inf = ifelse(is.na(prop_cum_inf), 0, prop_cum_inf))

save(contact_prop_take_off, file=paste0(start_date_lim, "contact_prop_take_off.RData"))

# EXCLUDE WITHIN FARM data or proportions of routes of transmission

contact_prop_take_off_lim <- total_rows_join_take_off_cum_sum %>% 
  filter(contact_name != "Within Farm") %>% 
  group_by(disease, day, surv_pgrm) %>% 
  mutate(daily_total_cum_inf_pigs = sum(med_cum_inf)) %>% 
  ungroup()

contact_prop_take_off_lim <- contact_prop_take_off_lim %>% 
  mutate(prop_cum_inf = med_cum_inf/daily_total_cum_inf_pigs,
         prop_cum_inf = ifelse(is.na(prop_cum_inf), 0, prop_cum_inf))

save(contact_prop_take_off_lim, file=paste0(start_date_lim, "contact_prop_lim_take_off.RData"))

