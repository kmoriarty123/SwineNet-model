# SwineNet Simple Network Simulation Model
#### last update: 07.02.2022

### Data
- Farms (agis_data_lim.csv) 
  - tvd_nr,year,holding_cat,gde_nr,gde_name,is_pig_stall,tot_pigs,other_animals,which_animals
- Tour Network (tour_network.csv)
  - tvd_source,tvd_dest,event_date,n_pigs,contact_type
- Geographic Network
  - tvd_source, tvd_dest, distance (km), contact_type

### Constants
Evidence for Choice of transmission rates
- BET = contact_rate x transmission_rate 
  - contact_rate: all pigs interact with all other pigs once a day 
  - here it is between 0.95 and 1 https://www.frontiersin.org/articles/10.3389/fvets.2019.00248/full
  - transmission_rate would be 0.45 to 3.63 per day: https://pubmed.ncbi.nlm.nih.gov/23664069/#:~:text=Different%20criteria%20were%20used%20for,0.45%20to%203.63%20per%20day. 
  - here it is between 0.6 and 1.5 https://www.frontiersin.org/articles/10.3389/fvets.2019.00248/full
  - here it is between https://bvajournals.onlinelibrary.wiley.com/doi/pdf/10.1136/vr.103593
- SIG: time from exposed to acute disease is 4-9 days after exposure. 
  - I set to 6.25 days. https://www.nature.com/articles/s41598-020-62736-y
- DEL: After disease, death usually in 10 days.  
  - https://www.efsa.europa.eu/en/topics/topic/african-swine-fever#:~:text=Sudden%20death%20may%20occur.,not%20show%20typical%20clinical%20signs.
- Others: 
  - Francesco's article: https://www.authorea.com/doi/full/10.22541/au.164271398.86217172/v1 (table 3)
  - danish model: (supplemental tables show parameter values) https://www.frontiersin.org/articles/10.3389/fvets.2018.00049/full#supplementary-material

### Parameters
- start_date
- end_date 
- curr_run 
- stochastic 
- not_stochastic
- seed
  
### Set up the environment
1. create_farm_dict (tvd_id (key) farm_idx (value))
2. set_index_case
3. create_sim_data (2-D array  size: num_farms x 4) 
    - columns: num susceptible pigs (begins at farm yearly average), num exposed, num_infected, num_deceased
    - rows: farms positioned at farm_idx
4. create tour array and dataframes
    - tour array (2-D array, shape: num_farms x num days from start to end of simulation)
    - direct transport dataframe (replaced tvd_ids for source and dest farms with farm_indices)
    - other contact transport dataframe (replaced tvd_ids for source and dest farms with farm_indices)
5. create geographic array
    - geo array (2-D array, shape: num_farms x 3, columns: source_idx, dest_idx, distance (km))

### Simulate Spread
- For each day from start_date to end_date (inclusive)
  a. update_spread_within_farms
  b. update_spread_between_farms

### Example Single Run Execution
- py cli_single_tvd.py --start_date=2014-01-01 --end_date=2014-01-10 --curr_run=2 --stochastic --index_case_tvd_id=[tvd_id] --seed=2
- py cli.py --start_date=2014-01-01 --end_date=2014-01-03 --curr_run=1 --stochastic --seed=1

### Surveillance and Control Measures
1. Surveillance
   - testing at slaughterhouse (consider sensitivity and specificity of tests)
     - to do: (currently - for some diseases, slaughterhouse testing is every few months)
     - select all slaughterhouses and random draw from them (slaughterhouses are currently chosen at random)
     - current pigs
   - testing at farms with many out-going transport (set different thresholds)
   - reduce threshold for farm mandatory testing (currently based on certain % increase of deceased pigs or 2 (?) unexplained abortions)
2. Control
  - increase biosecurity (explore which farms would make a difference)
  - build fencing
  - stop transports
  - cull herd

