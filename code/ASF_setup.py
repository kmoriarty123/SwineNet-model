"""ASF Setup.

Establishes ASF transmission variables.

"""

# Within Farm Spread
# BET: Contact transmission rate
# KAP: Factor by which asymptomatic transmit disease
# SIG: Exposed to infected rate
# RHO: Proportion of the ones moving from exposed to infected that are asymptomatic
# DEL: Disease causing death rate
# GAM: Rate at which asym recover (and develop immunity)
#BET, SIG, RHO, DEL, GAM = 1.75, 0.144, 0, 0.143, 0
#KAP = 0

# Between Farm Spread
# Other contact transmission rates
# PHI: DIRECT_TRUCK_TRANS_RATE
# PSI: INDIRECT_TRUCK_TRANS_RATE
# ETA: EXT_TRUCK_TRANS_RATE
# OME: GEO_TRANS_RATE


class Parameters:
    BET = 1.75
    KAP = 0.15
    SIG = 0.144
    RHO = 0.1
    DEL = 0.143
    THE = 0.95
    GAM = 0.025

    RHO_S = 0

    PHI = 0.0325
    PSI = 0.0119
    ETA = 0.00572
    OME = 0.00423
