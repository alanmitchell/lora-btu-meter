"""Module that converts thermistor readings into temperature.
"""
import math

def t_from_adc(adc_val, divider_r, steinhart_coeff, max_val=65535):
    """Returns the temperature of the thermistor in degrees F
    given the count read by and Analog-to-Digital converter.
    'divider_r' is the divider resitor value in ohms. 'steinhart_coeff'
    are a three-tuple of the Steinhart coefficients used to convert
    thermistor resistance into absolute temperature measured in Rankine.
    'max_val' is the maximum read value of the ADC.
    """
    c1, c2, c3 = steinhart_coeff     # unpack the three Steinhart coefficients

    # determine resistance of thermistor
    t_resis = adc_val / (max_val - adc_val) * divider_r
    lnR = math.log(t_resis) if t_resis>0.0 else -9.99e99
    tempF = (1.8 / (c1 + c2 * lnR + c3 * lnR ** 3)) - 459.67

    return tempF
