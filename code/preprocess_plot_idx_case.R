#############################################################
## title: "Preprocess Index Case Summary"
## author : Kathleen Moriarty
## date_created : 05.06.2022
## desc: Determine the characteristics of the index cases
## output: 

#############################################################

rm(list=ls()) 
library(dplyr)
library(ggplot2)
library(data.table)
library(tidyr)
setwd("Z:/Datasets/NetworkMaterial/SwineNet-model/output/")

############ results_by_compart_grp_all.txt  ############

list_disease = c("APP", "ASF", "PRRS")
list_start_date = c('2019_5_1')
#list_start_date = c() # for additional exploration with ASF
#list_disease = c('ASF') # only for additional start dates of ASF
########
start_date = '2019_5_1'
disease = 'APP'
# to store datasets
all_index_case_data <- data.frame() 

j=1
k=1
i=1
for (j in 1:(length(list_disease))){
  for (k in 1:(length(list_start_date))){
    
    disease <- list_disease[j]
    start_date <- list_start_date[k]
    print(disease)
    print(start_date)
    # to find files
    folder = paste0(disease, '/', start_date, "/no_surv")
    idx_filename <- '/index_case_all.txt'
    
    # to store records
    idx_case_data <- data.frame()
    
    # grab list of results_by_compart_all.txt files
    list_of_idx_files <- list.files(path = folder, 
                                        recursive = TRUE,
                                        pattern = "index_case_all.txt", 
                                        full.names = TRUE)
    
    # Preparing compartment txt files
    idx_colnames <- c('year', 'tvd_id', 
                          'plz', 'gemeinde', 'n1',
                          'farm_type', 'n_pigs',
                          'num_run')
  
    for (i in 1:(length(list_of_idx_files))){
      print(i)
      # read in file
      tmp_idx_case_df <- fread(list_of_idx_files[i], 
                                   header = FALSE, 
                                   sep = ",",
                                   encoding = "Latin-1")
      
      # select only necessary columns
      tmp_idx_case_df <- tmp_idx_case_df %>% 
        select(V1:V7, last_col())
      print('here')
      # set name of surveillance type and phi/psi factors
      file_name_strings <- stringr::str_split(list_of_compart_files[i], "/")
      #disease <- file_name_strings[[1]][1]
      surv_type <- file_name_strings[[1]][3]
      surv_pgrm_name <- file_name_strings[[1]][4]
      #start_date <- file_name_strings[[1]][2]
      # set col names
      colnames(tmp_idx_case_df) <- idx_colnames
      
      # Add distinguishing variables
      tmp_idx_case_df$disease <- disease
      tmp_idx_case_df$surv_pgrm <- surv_pgrm_name
      tmp_idx_case_df$start_date <- as.Date(start_date, "%Y_%m_%d")
      
      idx_case_data <- rbind(idx_case_data, tmp_idx_case_df)
      
    }
    
    all_index_case_data <- rbind(all_index_case_data, idx_case_data)
  }
}

all_index_case_data <- all_index_case_data %>% 
  mutate(surv_pgrm_name = case_when(surv_pgrm == 'phi_factor_1.0_psi_factor_1.0_idx_case_factor_1' ~ "I.W. Factor 1",
                                                               surv_pgrm == 'phi_factor_1.0_psi_factor_1.0_idx_case_factor_2' ~ "I.W. Factor 2",
                                                               surv_pgrm == 'phi_factor_1.0_psi_factor_1.0' ~ "I.W. Factor 3"))
                                    

# save the raw disease + start_date no surveillance data to record
save(all_index_case_data, file=paste0("all_index_case_data.RData"))

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


ggplot(all_index_case_data, aes(x=farm_type, fill=surv_pgrm_name)) +
  geom_bar(position='dodge') +
  coord_flip() +
  scale_fill_manual(values=cbPalette) +
  theme_bw() +
  facet_grid(disease~start_date)

ggplot(all_index_case_data, aes(x=n_pigs, fill=surv_pgrm_name)) +
  geom_histogram(position = 'dodge')+
  #coord_flip() +
  scale_fill_manual(values=cbPalette) +
  theme_bw() +
  facet_grid(disease~start_date)

ggplot(all_index_case_data, aes(x=gemeinde, fill=surv_pgrm_name)) +
  geom_bar(position='dodge') +
  coord_flip() +
  scale_fill_manual(values=cbPalette) +
  theme_bw() +
  facet_grid(disease~start_date)

tmp <- all_index_case_data %>% 
  group_by(disease, start_date, surv_pgrm) %>% 
  summarize(n_dist = n_distinct(tvd_id))
