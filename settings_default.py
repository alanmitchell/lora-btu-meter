"""This is the initial settings file that is copied to the CircuitPython
microcontoller and placed there as "settings.py".
"""

# This calibration value (degrees F) is added to the measured Delta-T to correct for any
# inaccuracies in the temperature measurement system.
DELTA_T_CALIB = 0.0            # degrees F

# These are the three Steinhart coefficients for the thermistors used by the 
# BTU Meter. These coefficients should convert thermistor resistance to absolute
# temperature on the Rankine scale.

# Tekmar 071 thermistor
# STEINHART = (0.001124476, 0.00023482, 8.54409E-08)

# BAPI 10K-3
STEINHART = (0.00102817, 0.000239281, 1.56119e-07)
