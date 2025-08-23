# Data folder

This folder should contain all **preprocessed input files** needed to run the SwineNet simulations.  
The files are **ignored by Git** (see `.gitignore`) so that large datasets don’t clutter the repository.  

## Required files per simulation year

For each simulation year `<YEAR>` (e.g., `2019`), ensure the following files are present:

- `farm_dict_<YEAR>.pkl` — Preprocessed farm dictionary mapping TVD IDs to farm indices.  
- `farm_list_<YEAR>.pkl` — List of farms and their attributes.  
- `sim_data_<YEAR>.npy` — Initial state matrix of compartments per farm.  
- `geo_arr_<YEAR>.npy` — Geographic adjacency/connection array.  
- `direct_trans_<YEAR>.pkl` — Direct pig transport dataframe.  
- `other_trans_<YEAR>.pkl` — Indirect/other contact dataframe (e.g., truck-sharing, fomites).  

## Optional / special-case files

- `slaughter_surv_9.csv`, `slaughter_surv_18.csv`, `slaughter_surv_36.csv` — Predefined slaughterhouse lists for slaughter surveillance.  
- `top_deg_list_all_<N>.csv` — Farm rankings by network metrics for network surveillance, where `<N>` is the threshold number (e.g., `250`).  

## Notes

- File paths are resolved relative to the `cli.py` script (expects `../data`).  
- Ensure that **start_date.year** matches the year of the data files (e.g., a 2019 simulation needs `*_2019.*`).  
- Data files are typically generated in preprocessing steps outside this repo (R scripts or other pipelines).  

---