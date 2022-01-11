# SwineNet Simple Network Simulation Model

### Data
- Farms
  - tvd_id, num_pigs, fencing, farm_type, gemeinde
- Basic Tour Network
  - tvd_source, tvd_dest, datetime, num_pigs
- Extended Tour Network
  - tvd_source, tvd_dest, datetime, contact_type
- Geographic Network
  - tvd_source, tvd_dest, distance (km)

### Parameters
- start_date
- end_date
- weights applied for contact type:
  - geographic distance (<1km, >1 U < 2km)
  - shared truck
  - fomite contamination (inside truck)
  - fomite contamination (outside truck)
  
### Set up the environment
1. set_index_case
2. create_farm_dict (matches tvd_id (key) to array_index (value))
    - (note: all farms are "active" farms because they will be connected geographically)
3. create_sim_data (2-D array  size: num_farms x 3) 
    - columns s:num_susceptible, i: num_infected, t: num_days_infected
    - rows: number of farms

### Simulate Spread
- For each day from start_date to end_date
  1. update_spread_within_farms
  2. update_spread_btwn_farms
