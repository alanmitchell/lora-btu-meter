"""Module that converts thermistor readings into temperature.
"""
import math

# Steinhart coeficients for Tekmar 071 thermistors
c1, c2, c3 = (0.001124476, 0.00023482, 8.54409E-08)

def t_from_adc(adc_val, divider_r, max_val=65535):
    """Returns the temperature of the thermistor in degrees F
    given the count read by and Analog-to-Digital converter.
    'divider_r' is the divider resitor value in ohms. 'max_val' is
    the maximum read value of the ADC.
    """
    # determine resistance of thermistor
    t_resis = adc_val / (max_val - adc_val) * divider_r
    lnR = math.log(t_resis) if t_resis>0.0 else -9.99e99
    tempF = (1.8 / (c1 + c2 * lnR + c3 * lnR ** 3)) - 459.67
    return tempF