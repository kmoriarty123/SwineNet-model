# Functions for summarize_data_per_disease

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
  
  prop_farm_count_under_10 <- tmp_compart_df %>% 
    group_by(num_run) %>% 
    slice_max(farm_count) %>% 
    slice_min(date) %>% 
    ungroup() %>%
    mutate(all_n = n()) %>% 
    filter(farm_count < 10) %>%
    mutate(prop_under_10 = n()/all_n) %>%
    distinct(prop_under_10)
  
  # Determine the proportion of runs for which disease "died out" 
  # meaning no new infections for the last 20 days
  
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
            prop_under_10 = prop_farm_count_under_10$prop_under_10,
            prop_no_new_inf_20 = prop_no_new_inf_20$prop_no_20)
  
  print(surv_type)
  print(surv_pgrm_name)
  print(nrow(all_outbreak_data))
  return(all_outbreak_data)
}

