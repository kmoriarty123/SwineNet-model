# Kathleen Moriarty
# Checking for significance in tour reductions 
# Checking for significance in the seasonality

load("total_compart_data_take_off.RData")
load("total_compart_data_take_off_sum.RData")

cbPalette <- c(#"#999999", # grey
  #"#56B4E9", # sky blue
  "#0072B2", # blue
  "#009E73", # green
  "#E69F00", # yellowy orange
  #"#D55E00", # orangey red
  #"#F0E442", # yellow
  "#CC79A7"# mauve
  #"#000000"
  #"#7570b3" 
)# purply blue

### TOUR REDUCTIONS: PRRS ###

# T-test to test if the means are different at day 242

prrs_t_test_244 <- total_compart_data_take_off %>% 
  filter(start_date == '2019-05-01',
         disease == 'PRRS',
         days_since_intro == 244) %>% 
  filter(surv_pgrm %in% c('limit_tour_contacts_0.1', 'limit_tour_contacts_0.000001')) %>% 
  mutate(tour_reduce = ifelse(surv_pgrm == 'limit_tour_contacts_0.1', '10%', '0%')) %>% 
  select(days_since_intro, tour_reduce, farm_count) 

farm_count_0.0_244 <- prrs_t_test_244[which(prrs_t_test_244$tour_reduce=='0%'), "farm_count", drop = FALSE]
farm_count_0.1_244 <- prrs_t_test_244[which(prrs_t_test_244$tour_reduce=='10%'), "farm_count", drop = FALSE]

hist(farm_count_0.1_244$farm_count)
#distribution is not normal - mann whitney test

# CANNOT do t-test (or maybe yes with 130+ samples)
t_res <- t.test(farm_count_0.0_244,
                farm_count_0.1_244,
                var.equal = TRUE)
t_res

# q-q plot
library(qqplotr)
ggplot(data = prrs_t_test_244, 
       mapping = aes(sample = farm_count, color = tour_reduce, fill = tour_reduce)) +
  stat_qq_band(alpha=0.5, conf=0.95, qtype=1, bandType = "boot") +
  stat_qq_line(identity=TRUE) +
  stat_qq_point(col="black") +
  facet_wrap(~ tour_reduce, scales = "free") +
  labs(x = "Theoretical Quantiles", y = "Sample Quantiles") + theme_bw()
#Not normally distributed

wilcox.test(farm_count ~ tour_reduce,
            data = prrs_t_test_244,
            na.rm=TRUE, paired=FALSE, 
            exact=FALSE, conf.int=TRUE)

# p-value = 0.3253


# KS-test to test if the distributions are significantly different

prrs_ks_test_0.0 <- total_compart_data_take_off_sum %>% 
  filter(start_date == '2019-05-01',
         disease == 'PRRS',
         name=='med_farm_count') %>% 
  filter(surv_pgrm %in% c('limit_tour_contacts_0.000001')) %>% 
  select(days_since_intro, value) %>% 
  mutate(prev_value = lag(value,n=1),
         new_farm_inf = value - prev_value) %>% 
  mutate(sum_infected = sum(new_farm_inf, na.rm=TRUE)) %>% 
  mutate(dens_inf = new_farm_inf/sum_infected) %>% 
  mutate(cum_sum = cumsum(replace_na(dens_inf, 0)),
         tours_reduced = '0%') 

prrs_ks_test_0.1 <- total_compart_data_take_off_sum %>% 
  filter(start_date == '2019-05-01',
         disease == 'PRRS',
         name=='med_farm_count') %>% 
  filter(surv_pgrm %in% c('limit_tour_contacts_0.1')) %>% 
  select(days_since_intro, value) %>% 
  mutate(prev_value = lag(value,n=1),
         new_farm_inf = value - prev_value) %>% 
  mutate(sum_infected = sum(new_farm_inf, na.rm=TRUE)) %>% 
  mutate(dens_inf = new_farm_inf/sum_infected) %>% 
  mutate(cum_sum = cumsum(replace_na(dens_inf, 0)),
         tours_reduced = '10%') 

prrs_ks_test <- rbind(prrs_ks_test_0.1, prrs_ks_test_0.0)

# cumulative # of farms infected
ggplot(prrs_ks_test, aes(x=days_since_intro, 
                         y=value, 
                         color=as.factor(tours_reduced))) +
  geom_point() +
  theme_bw() +
  scale_colour_manual(values=cbPalette) +
  labs(#title="Median and Maximum Infected Farm Count for No Surveillance", 
    #y='Cumulative Sum of Density \n of Median Infected Number of Farms',
    x="Days Since Introduction",
    color="Percent of Tours \nRemoved")

# density of new farms infected
ggplot(prrs_ks_test, aes(x=days_since_intro, 
                         y=dens_inf, 
                         color=as.factor(tours_reduced))) +
  geom_point() +
  theme_bw() +
  scale_colour_manual(values=cbPalette) +
  labs(#title="Median and Maximum Infected Farm Count for No Surveillance", 
    #y='Cumulative Sum of Density \n of Median Infected Number of Farms',
    x="Days Since Introduction",
    color="Percent of Tours \nRemoved")

# cumulative sum of density
ggplot(prrs_ks_test, aes(x=days_since_intro, y=cum_sum, color=as.factor(tours_reduced))) +
  geom_point() +
  theme_bw() +
  scale_colour_manual(values=cbPalette) +
  labs(#title="Median and Maximum Infected Farm Count for No Surveillance", 
    y='Cumulative Sum of Density \n of Median Infected Number of Farms',
    x="Days Since Introduction",
    color="Percent of Tours \nRemoved")

ks_res <- ks.test(prrs_ks_test_0.1$cum_sum, 
                  prrs_ks_test_0.0$cum_sum,
                  var.equal = TRUE)
ks_res

# Results: p-value 0.5229

#### SEASONALITY: ASF ####

# original data
total_compart_data_take_off %>% 
  filter(surv_pgrm == 'no_surv',
         disease == 'ASF',
         days_since_intro <= 242) %>% 
  group_by(start_date, days_since_intro) %>% 
  summarize(med_farm_count = median(farm_count)) %>% 
  ungroup() %>% 
  ggplot(., aes(x=days_since_intro, y=med_farm_count, color=as.factor(start_date))) +
  geom_point()

# add a zero point a day 243
t0 <- total_compart_data_take_off %>% 
  filter(surv_pgrm == 'no_surv',
         disease == 'ASF',
         days_since_intro <= 242) %>% 
  group_by(start_date, days_since_intro) %>% 
  summarize(med_farm_count = median(farm_count)) %>% 
  ungroup() %>% 
  group_by(start_date) %>% 
  #arrange(date) %>% 
  mutate(prev_farm_count = lag(med_farm_count,n=1),
         new_farm_inf = med_farm_count - prev_farm_count) %>% 
  ungroup() %>% 
  add_row(days_since_intro = 243,
          new_farm_inf = 0,
          start_date = as.Date('2014-01-01')) %>% 
  add_row(days_since_intro = 243,
          new_farm_inf = 0,
          start_date = as.Date('2014-05-01')) %>% 
  add_row(days_since_intro = 243,
          new_farm_inf = 0,
          start_date = as.Date('2019-01-01')) %>% 
  add_row(days_since_intro = 243,
          new_farm_inf = 0,
          start_date = as.Date('2019-05-01'))

ggplot(t0, 
       aes(x=days_since_intro, y=new_farm_inf, color=as.factor(start_date))) +
  geom_point() 

# create density function
t1 <- t0 %>%
  group_by(start_date) %>% 
  mutate(sum_infected = sum(new_farm_inf, na.rm=TRUE)) %>% 
  ungroup() %>% 
  group_by(start_date, days_since_intro) %>% 
  mutate(dens_inf = new_farm_inf/sum_infected) %>%
  ungroup()

ggplot(t1, aes(x=days_since_intro, y=new_farm_inf, color=as.factor(start_date))) +
  geom_point() 

ggplot(t1, aes(x=days_since_intro, y=dens_inf, color=as.factor(start_date))) +
  geom_point() 

# create cumulative sum
t2 <- t1 %>%
  group_by(start_date) %>% 
  mutate(cum_sum = cumsum(replace_na(dens_inf, 0))) %>%
  ungroup()

ggplot(t2, aes(x=days_since_intro, y=cum_sum, color=as.factor(start_date))) +
  geom_point() +
  theme_bw() +
  scale_colour_manual(values=cbPalette) +
  labs(#title="Median and Maximum Infected Farm Count for No Surveillance", 
    y='Cumulative Probability \n of Median Infected Number of Farms',
    x="Days Since Introduction",
    color="Introduction Date")


d_2014_05 <- t2[which(t2$start_date=='2014-05-01'),'new_farm_inf']
d_2014_01 <- t2[which(t2$start_date=='2014-01-01'),'new_farm_inf']
d_2019_05 <- t2[which(t2$start_date=='2019-05-01'),'new_farm_inf']
d_2019_01 <- t2[which(t2$start_date=='2019-01-01'),'new_farm_inf']

ks_res_season1 <- ks.test(d_2019_05$new_farm_inf, 
                          d_2019_01$new_farm_inf,
                          alternative = 'two.sided',
                          exact=TRUE)
ks_res_season1
ks_res_season2 <- ks.test(d_2014_05$new_farm_inf, 
                          d_2014_01$new_farm_inf,
                          alternative = 'two.sided',
                          exact=TRUE)
ks_res_season2
ks_res_season3 <- ks.test(d_2014_01$new_farm_inf, 
                          d_2019_01$new_farm_inf,
                          alternative = 'two.sided',
                          exact=TRUE)
ks_res_season3
ks_res_season4 <- ks.test(d_2014_05$new_farm_inf, 
                          d_2019_05$new_farm_inf,
                          alternative = 'two.sided',
                          exact=TRUE)
ks_res_season4
