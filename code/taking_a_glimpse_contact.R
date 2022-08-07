rm(list=ls())
setwd("Z:/Datasets/NetworkMaterial/SwineNet-model/output/glimpse")
cntD_all <- NULL
# used to subset the directory name for the surv_pgrm_title
date <- '2019-05-01'
contact_filename <- '/results_by_contact_grp_all.txt'
disease = c('APP', 'ASF', 'PRRS')
contact_coln <- c('date', 'type', 'num', 'run_id', 'disease')

for(dise in disease) {

  cntD <- read.table(paste0(date, "/", dise, "/" , contact_filename),
                               header = FALSE, 
                               sep = ",")
  cntD <- cntD %>% 
    mutate(disease = dise)
  
  cntD_all <- rbind(cntD_all, cntD)
}

#add col names
colnames(cntD_all) <- contact_coln
# make date field date
cntD_all <- cntD_all %>% 
  mutate(date = as.Date(date, format = "%Y-%m-%d"))

#create dataframe with all fields and dates
date <- seq(as.Date("2019-05-01"), as.Date("2019-12-31"), 'days')
run_id <- seq(1,1000)
type <- c('f', 'd', 'g', 't', 'i', 'e')
template_cnt <- expand_grid(
  date = date,
  disease = disease,
  run_id = run_id,
  type = type
)

template_cnt$num = 0

# join with other dataframe to fill the missing info
missing <- template_cnt %>% 
  anti_join(cntD_all, by = c('date', 'disease', 'run_id', 'type'))

cnt_all <- rbind(cntD_all, missing) 

cntD_all_sum <- cnt_all %>% 
  group_by(disease, run_id, type) %>% 
  mutate(sum_inf = cumsum(num)) %>% 
  ungroup()

# median, max, 95% farm count
cntD_all_sum %>% 
  filter(type == 'f') %>% 
  ggplot(., 
         aes(x=date, 
             y=sum_inf, 
             color=as.factor(run_id))) +
  geom_point() +
  theme(legend.position = 'none') +
  facet_wrap(~disease, scales = 'free_y')

# find medians
cntD_all_sum_med <- cntD_all_sum %>% 
  group_by(disease, type, date) %>% 
  summarize(med = median(sum_inf),
            max = max(sum_inf),
            quantile_0.95 = quantile(sum_inf, 0.95)) %>% 
  ungroup() %>% 
  pivot_longer(med:quantile_0.95)
  
# median, max, 95% farm count
ggplot(cntD_all_sum_med, 
         aes(x=date, 
             y=value, 
             color=type)) +
  geom_point() +
  facet_wrap(~disease + name, scales = 'free_y')


