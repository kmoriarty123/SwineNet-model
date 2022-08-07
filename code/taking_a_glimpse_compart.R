setwd("Z:/Datasets/NetworkMaterial/SwineNet-model/output/glimpse")
compart_df <- NULL
# used to subset the directory name for the surv_pgrm_title
date <- '2019-05-01'
contact_filename <- '/results_by_contact_grp_all.txt'
disease = c('ASF', 'APP', 'PRRS')

for (dise in disease){
  tmp_compart_df <- read.table(paste0(date, "/", dise, "/results_by_compart_all.txt"),
                               header = FALSE, 
                               sep = ",")
  
  tmp_compart_df <- tmp_compart_df %>% 
    mutate(disease = dise)
  
  compart_df <- rbind(compart_df, tmp_compart_df)
}

compart_df_sum <- compart_df %>% 
  group_by(disease, V1) %>% 
  summarize(med_removed = median(V6),
            med_recoverd = median(V7),
            med_rm_rc = med_recoverd + med_recoverd,
            med_exp = median(V3),
            med_inf = median(V4),
            med_asy = median(V5),
            med_eia = med_inf + med_asy + med_exp,
            med_farm = median(V2),
            max_farm = max(V2),
            quantile_0.95 = quantile(V2, 0.95),
            ) %>% 
  pivot_longer(med_removed:quantile_0.95) %>% 
  ungroup()

compart_df_sum_basic <- compart_df %>% 
  group_by(disease, V1) %>% 
  summarize(med_farm = median(V2))

ggplot(compart_df, aes(x=V1, y=V6, color=disease)) +
  geom_point()

ggplot(compart_df_sum, aes(x=V1, y=med_rm_rc, color=disease)) +
  geom_point()

# median farm count
ggplot(compart_df, aes(x=V1, y=V2, color=disease)) +
  geom_point()

# median, max, 95% farm count
compart_df_sum %>% 
  filter(name %in% c('med_farm', 'max_farm', 'quantile_0.95')) %>% 
ggplot(., 
       aes(x=V1, 
           y=value, 
           color=name)) +
  geom_point() +
  facet_wrap(~disease, scales = 'free_y')


