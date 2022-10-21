"""APP Setup.

Establishes APP transmission variables.

"""

# Within Farm Spread
# BET: Contact transmission rate
# KAP: Factor by which asymptomatic transmit disease
# SIG: Exposed to infected rate
# RHO: Proportion of the ones moving from exposed to infected that are asymptomatic
# DEL: Disease causing death rate
# GAM: Rate at which asym recover (and develop immunity)

# Between Farm Spread
# Other contact transmission rates
# PHI: DIRECT_TRUCK_TRANS_RATE
# PSI: INDIRECT_TRUCK_TRANS_RATE
# ETA: EXT_TRUCK_TRANS_RATE
# OME: GEO_TRANS_RATE


class Parameters:
    BET = 0.27
    KAP = 0.37
    SIG = 1
    RHO = 0.5
    DEL = 0.02
    THE = 0.05
    GAM = 0.02

    RHO_S = 0

    PHI = 0.1
    PSI = 0.01
    ETA = 0
    OME = 0
