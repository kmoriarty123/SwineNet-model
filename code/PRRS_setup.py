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
#BET, KAP, SIG, RHO, DEL, THE, GAM = 0.054, 0.25, 1, 1, 0.018, 0.2, 0.018
# For PRRS, there is a distinction between RHO on farms with sows and without sows. H
# This is the proportion for farms with sows:
#RHO_S = 0

# Between Farm Spread
# Other contact transmission rates
# PHI: DIRECT_TRUCK_TRANS_RATE
# PSI: INDIRECT_TRUCK_TRANS_RATE
# ETA: EXT_TRUCK_TRANS_RATE
# OME: GEO_TRANS_RATE
#ETA, OME, PSI, PHI =0.05, 0.005, 0.001, 0.005


class Parameters:

    BET = 0.054
    KAP = 0.25
    SIG = 1
    RHO = 1
    DEL = 0.018
    THE = 0.2
    GAM = 0.018

    RHO_S = 0

    PHI = 0.01625
    PSI = 0.01425
    ETA = 0.00429
    OME = 0.002115
