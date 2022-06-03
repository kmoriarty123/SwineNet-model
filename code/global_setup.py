"""Global Setup.

Establishes initial global variables.

"""

import datetime

# Indices from simulated_data matrix
# Susceptible, exposed, infectious (symptomatic), infectious (asymptomatic), deceased (from diseaes),
# isolated, quarantined (from susceptible), quarantined (from exposed)
SU, SUS, EX, EXS, INF, ASY, REM, REC, ISO, QUA_S, QUA_E, QUA_A = 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11

width_sim_data = 12

# Indices for farm_list
TVD, TYPE, NPIGS, SOW_IND, \
IDX_WGHT_PRRS_3, IDX_WGHT_ASF_3, IDX_WGHT_APP_3, \
IDX_WGHT_PRRS_1, IDX_WGHT_ASF_1, IDX_WGHT_APP_1, \
IDX_WGHT_PRRS_2, IDX_WGHT_ASF_2, IDX_WGHT_APP_2  = 1, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16

# Indices for transports
# Source, destination, data of transport, num of pigs transported, contact_type (d, t, i, p, f)
SRC, DEST, DATE, T_NPIGS, CNTCT = 0, 1, 2, 3, 4
column_names_direct = ['source_idx', 'dest_idx', 'event_date', 'n_pigs']
column_names_tour = ['source_idx', 'dest_idx', 'event_date', 'n_pigs', 'contact_type']

# Indices for tour with surveillance
# INSPCT: indicator to show that the transport will be inspected at the slaughterhouse
INSPCT, N_DIS = 4, 5 #TODO - confirm that theses are the correct indices!
column_names_direct_inspect = ['source_idx', 'dest_idx', 'event_date', 'n_pigs', 'inspect_ind']

# Indices for geo
G_SRC, G_DEST, DIST = 0, 1, 2
column_names_geo = ['source_idx', 'dest_idx', 'dist']

# Network testing farm list
NET_TVD, NET_CNTCT, NET_IDX = 0, 1, 2
# Years of data
beg_yr = 2014
end_yr = 2020  # only until 2019 for AGIS data & Tour data

# Tau-leap time step
TAU = 1

# Surveillance Variables

# Evidence for surveillance design: 9 slaughterhouses chosen at random. Roughly 7,200 pigs tested. 6 pigs at least
# from the same farm. Then, roughly 134 farms from each slaughter house. Inspection occured from Jan 1 - August 31 in
# 2020
# Changed from date to string because the year is not fixed
#inspection_start_date = datetime.date.fromisoformat('2014-01-01')
#inspection_end_date = datetime.date.fromisoformat('2014-08-30')
inspection_start_date = '01-01'
inspection_end_date = '08-30'

# NUM_SH = 9 # now passed as a parameter
MAX_FARMS_PER_SH = 134
MAX_PIGS_PER_FARM = 6
INIT_FARM_MORT = 0.026
FARM_SURV_DAY_DELAY = 10
