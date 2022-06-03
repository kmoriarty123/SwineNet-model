#############################################################
## title: "Summarize SwineNet Model Output for all diseases"
## author : Kathleen Moriarty
## date_created : 19.05.2022
## desc: creates multiple .RData files with summary of data
## output: various summary dataframes
#############################################################

rm(list=ls()) 
library(dplyr)
setwd("Z:/Datasets/NetworkMaterial/SwineNet-model/output/")
start_date = '2014_1_1'

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
