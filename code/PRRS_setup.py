"""PRRS Setup.

Establishes PRRS transmission variables.

"""

# Within Farm Spread
# BET: Contact transmission rate
# KAP: Factor by which asymptomatic transmit disease
# SIG: Exposed to infected rate
# RHO: Proportion of the ones moving from exposed to infected that are asymptomatic
# DEL: Disease causing death rate
# GAM: Rate at which asym recover (and develop immunity)

# For PRRS, there is a distinction between RHO on farms with sows and without sows.
# This is the proportion for farms with sows:
# RHO_S = 0

# Between Farm Spread
# Other contact transmission rates
# PHI: DIRECT_TRUCK_TRANS_RATE
# PSI: INDIRECT_TRUCK_TRANS_RATE
# ETA: EXT_TRUCK_TRANS_RATE
# OME: GEO_TRANS_RATE

class Parameters:
    BET = 0.054
    KAP = 0.25
    SIG = 1
    RHO = 1
    DEL = 0.018
    THE = 0.2
    GAM = 0.018

    RHO_S = 0

    PHI = 0.000037
    PSI = 0.000028
    ETA = 0.000009
    OME = 0.00000083
