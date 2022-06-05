#############################################################
## title: "Summarize SwineNet Model Output for all diseases"
## author : Kathleen Moriarty
## date_created : 19.05.2022
## desc: creates multiple .RData files with summary of data
## output: each of the compart, first_detect, outbreak for the different start_dates and...
#all_total_compart_data
#all_total_first_detect
#all_total_outbreak_data
#############################################################

rm(list=ls()) 
library(dplyr)
setwd("Z:/Datasets/NetworkMaterial/SwineNet-model/output/")
#start_date = '2019_5_1'
list_start_date = c('2014_1_1', '2014_5_1', '2019_1_1', '2019_5_1')

all_total_compart_data <- data.frame()
all_total_first_detect <- data.frame()
all_total_outbreak_data <- data.frame()

for(start_date in list_start_date){
  
  print(start_date)
  
  folder = paste0("APP/", start_date,"/")
  
  load(paste0(folder, "all_compartment.RData"))
  load(paste0(folder, "all_compart_data_sum.RData"))
  load(paste0(folder, "all_first_detect.RData"))
  load(paste0(folder, "all_outbreak_data.RData"))
  
  APP_all_compart_data <- all_compart_data
  APP_all_compart_data_sum <- all_compart_data_sum
  APP_all_first_detect <- all_first_detect
  APP_all_outbreak_data <- all_outbreak_data
  
  APP_all_compart_data$disease <- "APP"
  APP_all_compart_data_sum$disease <- "APP"
  APP_all_first_detect$disease <- "APP"
  APP_all_outbreak_data$disease <- "APP"
  
  folder = paste0("PRRS/", start_date,"/")
  
  load(paste0(folder, "all_compartment.RData"))
  load(paste0(folder, "all_compart_data_sum.RData"))
  load(paste0(folder, "all_first_detect.RData"))
  load(paste0(folder, "all_outbreak_data.RData"))
  
  PRRS_all_compart_data <- all_compart_data
  PRRS_all_compart_data_sum <- all_compart_data_sum
  PRRS_all_first_detect <- all_first_detect
  PRRS_all_outbreak_data <- all_outbreak_data
  
  PRRS_all_compart_data$disease <- "PRRS"
  PRRS_all_compart_data_sum$disease <- "PRRS"
  PRRS_all_first_detect$disease <- "PRRS"
  PRRS_all_outbreak_data$disease <- "PRRS"
  
  folder = paste0("ASF/", start_date,"/")
  
  load(paste0(folder, "all_compartment.RData"))
  load(paste0(folder, "all_compart_data_sum.RData"))
  load(paste0(folder, "all_first_detect.RData"))
  load(paste0(folder, "all_outbreak_data.RData"))
  
  ASF_all_compart_data <- all_compart_data
  ASF_all_compart_data_sum <- all_compart_data_sum
  ASF_all_first_detect <- all_first_detect
  ASF_all_outbreak_data <- all_outbreak_data
  
  ASF_all_compart_data$disease <- "ASF"
  ASF_all_compart_data_sum$disease <- "ASF"
  ASF_all_first_detect$disease <- "ASF"
  ASF_all_outbreak_data$disease <- "ASF"
  
  total_compart_data <- rbind(APP_all_compart_data, PRRS_all_compart_data, ASF_all_compart_data)
  total_first_detect <- rbind(APP_all_first_detect, PRRS_all_first_detect, ASF_all_first_detect)
  total_outbreak_data <- rbind(APP_all_outbreak_data, PRRS_all_outbreak_data, ASF_all_outbreak_data)
  
  # Save all the dfs
  save(total_compart_data, file = paste0("total_compart_data_", start_date, ".RData"))
  save(total_first_detect, file = paste0("total_first_detect_", start_date, ".RData"))
  save(total_outbreak_data, file = paste0("total_outbreak_data_", start_date, ".RData"))
  
  # add start_date to the datasets
  total_compart_data$start_date = as.Date(start_date, "%Y_%m_%d")
  total_first_detect$start_date = as.Date(start_date, "%Y_%m_%d")
  total_outbreak_data$start_date = as.Date(start_date, "%Y_%m_%d")
  
  # Bind so all dates are together
  all_total_compart_data <- rbind(total_compart_data, all_total_compart_data)
  all_total_first_detect <- rbind(total_first_detect, all_total_first_detect)
  all_total_outbreak_data <- rbind(total_outbreak_data, all_total_outbreak_data)
  
}

# create new column for days since introduction
all_total_compart_data <- all_total_compart_data %>% 
  mutate(start_date = as.Date(start_date, format = "%Y_%m_%d"),
         days_since_intro = as.integer(difftime(date, start_date, units="days")))

save(all_total_compart_data, file = paste0("all_total_compart_data.RData"))
save(all_total_first_detect, file = paste0("all_total_first_detect.RData"))
save(all_total_outbreak_data, file = paste0("all_total_outbreak_data.RData"))
