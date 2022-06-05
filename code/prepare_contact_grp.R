#############################################################
## title: "Preprocess Contact Type Groupings
## author : Kathleen Moriarty
## date_created : 29.05.2022
## output: .RData files:
#total_NS_contact_data
#total_NS_contact_data_sum
#total_NS_contact_data_sum_long
#############################################################

# load data
list_disease = c("APP", "ASF", "PRRS")
list_start_date = c('2014_1_1', '2019_5_1', '2014_5_1', '2019_1_1')

# for storing results
total_NS_contact_data_sum = data.frame()
total_NS_contact_data = data.frame()

for (j in 1:(length(list_disease))){
  for (k in 1:(length(list_start_date))){
    
    disease <- list_disease[j]
    start_date <- list_start_date[k]
    print(disease)
    print(start_date)
    
    folder = paste0(disease, '/', start_date, "/no_surv")
    # used to subset the directory name for the surv_pgrm_title
    #date <- '2014_1_1'
    contact_filename <- '/results_by_contact_grp_all.txt'
    
    total_contact_data <- data.frame()
    
    # grab list of results_by_compart_all.txt files
    list_of_contact_files <- list.files(path = folder, 
                                        recursive = TRUE,
                                        pattern = "results_by_contact_grp_all.txt", 
                                        full.names = TRUE)
    
    # Preparing compartment txt files
    contact_colnames <- c('date', 'contact_type', 'num_inf_pigs',
                          'num_run')
    
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
      tmp_contact_df <- tmp_contact_df %>% 
        group_by(contact_type, num_run) %>% 
        #arrange(date) %>% 
        mutate(cum_num_inf = cumsum(num_inf_pigs)) %>% 
        ungroup()
      
      tmp_contact_df$disease <- disease
      tmp_contact_df$surv_pgrm <- surv_pgrm_name
      tmp_contact_df$start_date <- as.Date(start_date, "%Y_%m_%d")
      
      # create new "day" to difference from start
      tmp_contact_df <- tmp_contact_df %>% 
        mutate(date = as.Date(date)) %>% 
        mutate(day = as.integer(difftime(date, start_date, units = "days")))
      
      total_contact_data <- rbind(tmp_contact_df, total_contact_data)
      
    }
    
    no_surv_contact_data <- total_contact_data %>% 
      mutate(contact_name = case_when(contact_type == 'f' ~ 'Within Farm',
                                      contact_type == 'd' ~ 'Direct Transfer',
                                      contact_type == 'g' ~ 'Geographic',
                                      contact_type == 't' ~ 'Direct Truck Share',
                                      contact_type == 'i' ~ 'Indirect Truck Share',
                                      contact_type == 'e' ~ 'External Truck'))
    
    # Save individual disease + start_date raw data to file
    save(no_surv_contact_data, file= paste0(disease, '/', start_date, "/no_surv_contact_data.RData"))
    
    # median/maximum of data across num_runs
    no_surv_contact_data_sum <- no_surv_contact_data %>% 
      group_by(disease, start_date, date, day, surv_pgrm, contact_name) %>% 
      summarize(med_num_inf_pigs = median(num_inf_pigs),
                max_num_inf_pigs = max(num_inf_pigs),
                med_cum_inf = median(cum_num_inf),
                mean_num_inf_pigs = mean(num_inf_pigs),
                mean_cum_inf = mean(cum_num_inf)) %>% 
      ungroup()
    
    # make data longer based on median/max values
    no_surv_contact_data_sum_long <- no_surv_contact_data_sum %>% 
      pivot_longer(med_num_inf_pigs:mean_cum_inf)
    
    # # cumulative sum of infected pigs
    # no_surv_contact_data_cum <- no_surv_contact_data_sum %>%
    #   group_by(disease, start_date, surv_pgrm, contact_name) %>% 
    #   arrange(date) %>% # or, order_by parameter in lag function
    #   mutate(cum_sum_med_inf = cumsum(med_num_inf_pigs),
    #          cum_sum_max_inf = cumsum(max_num_inf_pigs)) %>% 
    #   ungroup()
    
    # bind all diseases
    total_NS_contact_data <- rbind(total_NS_contact_data, no_surv_contact_data)
    total_NS_contact_data_sum <- rbind(total_NS_contact_data_sum, no_surv_contact_data_sum)
    
  }
}

# save combined raw data to file
save(total_NS_contact_data, file="total_NS_contact_data.RData")

# split surveillance pgrm by phi and psi factors
total_NS_contact_data_sum <- total_NS_contact_data_sum %>% 
  mutate(surv_pgrm2 = surv_pgrm) %>% 
  separate(surv_pgrm2, 
           into=c("s1","s2","phi_factor","s3", "s4","psi_factor"),
           sep="_") %>%
  select(-c(s1, s2, s3, s4))

# save summary data to file
save(total_NS_contact_data_sum, file="total_NS_contact_data_sum.RData")

# make data long on phi/psi factor
total_NS_contact_data_sum_long <- total_NS_contact_data_sum %>% 
  pivot_longer(phi_factor:psi_factor)

# remove all rows that are not necessary
total_NS_contact_data_sum_long <- total_NS_contact_data_sum_long %>% 
  filter(!(surv_pgrm != 'phi_factor_1.0_psi_factor_1.0' & 
             value == '1.0'))

save(total_NS_contact_data_sum_long, file="total_NS_contact_data_sum_long.RData")
