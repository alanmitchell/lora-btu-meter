# pyright: reportShadowedImports=false
"""CircuitPython code used to calibrate the Hot and Cold thermistors used in a
the lora-btu-meter. Use the 'deploy' script to copy this code to the board.
The code prints the current hot temperature and the hot - cold delta-T, factoring
in the current calibration coefficient. The goal is for a zero delta-T when both 
sensors are immersed in a water bath approximating the temperature that will be 
present when the sensors are installed in the final system.

The 'deploy' script assumes that the main LORA BTU meter deploy script has been
run once, so that settings, thermistor and other files are present on the board.
"""
import time
import board
from analogio import AnalogIn
from digitalio import DigitalInOut, Direction, Pull
import sys

from thermistor import t_from_adc
import settings

# Set up the pins used by the BTU meter. Temperature sensors are 
# thermistors, and the flow sensor is a dry switch closure.
pin_thot = AnalogIn(board.A3)
pin_tcold = AnalogIn(board.A1)

# Buffers to hold the most recent temperature readings. Ultimately averaged
# to determine BTUs.
buf_len = 100
arr_hot = [0] * buf_len
arr_cold = [0] * buf_len
# index tracking where in the buffer we are storing the current temperature
# reading.
ix_buf = 0

def current_temps():
    """Return the current hot, cold, and delta temperatures, adjusted
    for the calibration coefficient.
    """
    calib = settings.DELTA_T_CALIB
    t_hot = t_from_adc(sum(arr_hot) / buf_len, 4990.0, settings.STEINHART)
    t_hot += calib / 2.0
    t_cold = t_from_adc(sum(arr_cold) / buf_len, 4990.0, settings.STEINHART)
    t_cold -= calib / 2.0
    delta_t = t_hot - t_cold
    return t_hot, t_cold, delta_t

while True:

    try:

        arr_hot[ix_buf] = pin_thot.value
        arr_cold[ix_buf] = pin_tcold.value
        ix_buf = (ix_buf + 1) % buf_len
        time.sleep(0.01)
        if ix_buf == 0:
            t_hot, t_cold, delta_t = current_temps()
            print(t_hot, delta_t)

    except KeyboardInterrupt:
        sys.exit()
    
    except:
        print('Unknown error.')
        time.sleep(1)
