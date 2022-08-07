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
compart_filename <- '/results_by_compart_all.txt'

# source file for functions
source("../code/summarize_data_per_disease_functions.R")

# list disease
list_disease = c("ASF", "APP", "PRRS")
#list_disease = c("ASF")
#list_disease = c("APP", "PRRS")
#list_start_date = c('2014_1_1', '2014_5_1', '2019_1_1', '2019_5_1')
list_start_date = c('2019_5_1')

# Preparing compartment txt files
compart_colnames <- c('date', 'farm_count', 
                      'exposed', 'infected', 'asymptomatic',
                      'removed', 'recovered', 'isolated',
                      'quarantined_s', 'quarantined_e','quarantined_a',
                      'num_run')

#disease = 'ASF'
#start_date = '2019_5_1'

# Loop through all diseases, start dates and preprocess compartment txts
for(disease in list_disease){
  for(start_date in list_start_date){
    print(disease)
    print(start_date)
    folder = paste0(disease, '/', start_date)
    # grab list of results_by_compart_all.txt files
    list_of_compart_files <- list.files(path = folder, 
                                        recursive = TRUE,
                                        pattern = "results_by_compart_all.txt", 
                                        full.names = TRUE)
    
    
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
                                    prop_under_10 = double(),
                                    prop_no_new_inf_20 = double())
    
    
    
    # Loop through all compartment files for each surveillance program  and
    # preprocess the data 
    # functions
    i=1
    for (i in 1:(length(list_of_compart_files))){
      
      # set name of surveillance program
      file_name_strings <- stringr::str_split(list_of_compart_files[i], "/")
      disease <- file_name_strings[[1]][1]
      surv_type <- file_name_strings[[1]][3]
      surv_pgrm_name <- file_name_strings[[1]][4]
      
      #KBM delete later
      #if(surv_pgrm_name %in% c('psi_factor_50.0', 'psi_factor_200.0',
      #                         'phi_factor_50.0', 'phi_factor_200.0',
      #                         'eta_factor_50.0', 'eta_factor_200.0')){
      #  next
      #}
      # read in file
      tmp_compart_df <- read.table(list_of_compart_files[i], 
                                   header = FALSE, 
                                   sep = ",")
      
      
      # exclude all of the files that are sensitivity analysis of phi, psi, index case
      #if (surv_type == "no_surv"){
      #  if(surv_pgrm_name != "phi_factor_1.0_psi_factor_1.0"){
      #    next
      #  }
      #}
      
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
  }
}
