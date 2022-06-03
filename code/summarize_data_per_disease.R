#############################################################
## title: "Summarize SwineNet Model Output per Disease"
## author : Kathleen Moriarty
## date_created : 08.04.2022
## desc: creates multiple .RData files with summary of data
## NEED TO CHANGE variables disease and start_date depending on simulation run
## output: various summary dataframes
#############################################################

rm(list=ls()) 
library(dplyr)
setwd("Z:/Datasets/NetworkMaterial/SwineNet-model/output/")

# to modify depending on start date
disease = "PRRS"
start_date = '2019_5_1'
folder = paste0(disease, '/', start_date)
# used to subset the directory name for the surv_pgrm_title
#date <- '2014_1_1/'
compart_filename <- '/results_by_compart_all.txt'

# grab list of results_by_compart_all.txt files
list_of_compart_files <- list.files(path = folder, 
                            recursive = TRUE,
                            pattern = "results_by_compart_all.txt", 
                            full.names = TRUE)

# Preparing compartment txt files
compart_colnames <- c('date', 'farm_count', 
                      'exposed', 'infected', 'asymptomatic',
                      'removed', 'recovered', 'isolated',
                      'quarantined_s', 'quarantined_e','quarantined_a',
                      'num_run')

# to store all results
all_compart_data <- data.frame()
all_compart_data_sum <- data.frame()
all_first_detect <- data.frame()
sum_first_detect <- data.frame(surv_pgrm = character(),
                               surv_type = character(),
                               med_date = as.Date(character()),
                               med_farm_count = double(),
                               med_cum_inf = double())
all_outbreak_data <- data.frame(surv_pgrm = character(),
                                surv_type = character(),
                                prop_under_20 = double(),
                                prop_no_new_inf_20 = double())

# Prepares the general compartment DF (name columns, add cumulative columns)
prep_compart_files <- function(tmp_compart_df, 
                               compart_colnames){
  
  # set col names
  colnames(tmp_compart_df) <- compart_colnames
  
  # create total quarantined group
  # create cumulative infected number of pigs
  tmp_compart_df <- tmp_compart_df %>% 
    mutate(quarantined = quarantined_s + quarantined_e + quarantined_a) %>% 
    mutate(cum_infected = (infected + removed + recovered + isolated + quarantined_e + quarantined_a)) %>%
    mutate(date = as.Date(date))
  
  return(tmp_compart_df)
}

# combines all the compart dataframes from all surveillance progams
combo_all_compart <- function(surv_pgrm_name,
                             surv_type,
                             tmp_compart_df,
                             all_compart_data){
  
  # set surv_prgrm_name
  tmp_compart_df$surv_pgrm = surv_pgrm_name
  tmp_compart_df$surv_type = surv_type
  
  # bind rows to all dataframe
  all_compart_data <- rbind(all_compart_data, tmp_compart_df)
  
  return(all_compart_data)
}

# Summarizes the general compartment group 
prep_compart_grp <- function(surv_pgrm_name,
                             surv_type,
                             tmp_compart_df,
                             all_compart_data_sum){
  
   # summarize median and iqr for each seed group
  tmp_compart_df_grp_seed <- tmp_compart_df %>% 
    group_by(date) %>%
    select(-c(num_run)) %>% # remove num_run
    #summarize(med_farm_count = median(farm_count, na.rm = TRUE))
    summarize(across(farm_count:cum_infected, 
                     list(median=median, 
                          iqr1 =~ quantile(.,probs = 0.25),
                          iqr3 =~ quantile(.,probs = 0.75)),
                     .names="{.fn}_{.col}")) %>% 
    ungroup()
  
   
  # set surv_prgrm_name
  tmp_compart_df_grp_seed$surv_pgrm = surv_pgrm_name
  tmp_compart_df_grp_seed$surv_type = surv_type
  
  # bind rows to all dataframe
  all_compart_data_sum <- rbind(all_compart_data_sum, tmp_compart_df_grp_seed)
  
  return(all_compart_data_sum)
}

# Find the first date of detection for each simulation and then summarize 
prep_first_detect <- function(surv_pgrm_name,
                              surv_type,
                              tmp_compart_df,
                              all_first_detect){
  
  # select data of run @ point of first detection
  tmp_first_detect <- tmp_compart_df %>% 
    filter(isolated > 0) %>% 
    group_by(num_run) %>% 
    arrange(date) %>% 
    filter(row_number()==1) %>%
    ungroup()
  
  # if there was no detection for the run, then grab last row
  tmp_first_detect_never <- tmp_compart_df %>% 
    filter(!num_run %in% tmp_first_detect$num_run) %>% 
    group_by(num_run) %>% 
    slice_max(date) %>%
    ungroup()
  
  # join detected and detected_never dataframes
  tmp_first_detect_all <- rbind(tmp_first_detect, tmp_first_detect_never)
  
  # set surv_prgrm_name
  tmp_first_detect_all$surv_pgrm = surv_pgrm_name
  tmp_first_detect_all$surv_type = surv_type
  
  all_first_detect <- rbind(all_first_detect, tmp_first_detect_all)
                          

  return(all_first_detect)
}

# Determine the proportion of runs that had more than 20 farms infected for the
# given period
# Determine the proportion of runs for which disease "died out" 
# meanding no new infections for the last 20 days
prep_prop_outbreak <- function(surv_pgrm_name,
                             surv_type,
                             tmp_compart_df,
                             all_outbreak_data){
  
  # Determine the proportion of runs that had more than 10 farms infected for the
  # given period
  
   prop_farm_count_under_20 <- tmp_compart_df %>% 
    group_by(num_run) %>% 
    slice_max(farm_count) %>% 
    slice_min(date) %>% 
    ungroup() %>%
    mutate(all_n = n()) %>% 
    filter(farm_count < 20) %>%
    mutate(prop_under_20 = n()/all_n) %>%
    distinct(prop_under_20)
  
  # Determine the proportion of runs for which disease "died out" 
  # meanding no new infections for the last 20 days
  
  prop_no_new_inf_20 <- tmp_compart_df %>%
    group_by(num_run) %>% 
    slice_max(date, n=20) %>%
    arrange(date) %>% 
    mutate(diff_last_20 = last(cum_infected) - first(cum_infected)) %>%
    distinct(num_run, diff_last_20) %>%
    ungroup() %>% 
    mutate(all_n = n()) %>% 
    filter(diff_last_20==0) %>% 
    mutate(prop_no_20 = n()/all_n) %>% 
    distinct(prop_no_20)
    
  all_outbreak_data <- all_outbreak_data %>%  
    add_row(surv_pgrm = surv_pgrm_name,
            surv_type = surv_type,
            prop_under_20 = prop_farm_count_under_20$prop_under_20,
            prop_no_new_inf_20 = prop_no_new_inf_20$prop_no_20)
  
  return(all_outbreak_data)
}
i=1

# Loop through all compartment files for each surveillance program and run above
# functions

for (i in 1:(length(list_of_compart_files))){
  print(i)
  # read in file
  tmp_compart_df <- read.table(list_of_compart_files[i], 
                               header = FALSE, 
                               sep = ",")
  
  # set name of surveillance program
  #surv_pgrm_name <- gsub(paste0(date,'*(.*)',compart_filename),'\\1', list_of_compart_files[i])
  #surv_type <- sub('(.*)/.*','\\1',surv_pgrm_name)
  #surv_sub_type <- sub('(.*)/.*','\\1',surv_pgrm_name)
  #surv_pgrm_name2 <- sub('/', '_', surv_pgrm_name)
  file_name_strings <- stringr::str_split(list_of_compart_files[i], "/")
  disease <- file_name_strings[[1]][1]
  surv_type <- file_name_strings[[1]][3]
  surv_pgrm_name <- file_name_strings[[1]][4]
  
  # call function to prepare df
  tmp_compart_df <- prep_compart_files(tmp_compart_df, 
                                         compart_colnames)
  
  all_compart_data <- combo_all_compart(surv_pgrm_name, 
                                        surv_type,
                                        tmp_compart_df, 
                                        all_compart_data)
  
  # call function to prepare compartment df
  all_compart_data_sum <- prep_compart_grp(surv_pgrm_name, 
                                         surv_type,
                                         tmp_compart_df, 
                                        all_compart_data_sum)
  
  # call function to prepare first detect df
  all_first_detect <- prep_first_detect(surv_pgrm_name, 
                                        surv_type,
                                        tmp_compart_df,
                                        all_first_detect)
  
  # call function to prepare proportion of outbreak
  all_outbreak_data <- prep_prop_outbreak(surv_pgrm_name, 
                                        surv_type,
                                        tmp_compart_df,
                                        all_outbreak_data)
  
  
  
}

# Save all the dfs
save(all_compart_data, file = paste0(folder, "/all_compartment.RData"))
save(all_compart_data_sum, file = paste0(folder, "/all_compart_data_sum.RData"))
save(all_first_detect, file=paste0(folder, "/all_first_detect.RData"))
save(all_outbreak_data, file=paste0(folder, "/all_outbreak_data.RData"))
