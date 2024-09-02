# pyright: reportShadowedImports=false
"""CircuitPython code to implement a BTU meter and send the data via LoRaWAN.
Cumulative BTUs and gallons of flow are measured and transmitted.  Also, hot and
cold temperatures of the fluid are transmitted, as measured at the time of 
transmission (*not* an average over the last gallon).
"""
import time
import board
import busio
from analogio import AnalogIn
from digitalio import DigitalInOut, Direction, Pull
import supervisor
import sys

import lora
from config import config
from thermistor import t_from_adc
import settings

# Serial port talking to LoRaWAN module, SEEED Grove E5.
e5_uart = busio.UART(
    board.TX, board.RX, 
    baudrate=9600, 
    timeout=0.0,                 # need some timeout for readline() to work.
    receiver_buffer_size=128,     # when downlink is received, about 90 bytes are received.
)

# wait for join before sending reboot; join only occurs during power up.
time.sleep(8.0)
lora.send_reboot(e5_uart)
time.sleep(7.0)    # need to wait for send to continue.

# Set up the pins used by the BTU meter. Temperature sensors are 
# thermistors, and the flow sensor is a dry switch closure.
pin_thot = AnalogIn(board.A3)
pin_tcold = AnalogIn(board.A1)
pin_flow = DigitalInOut((board.A0))
pin_flow.direction = Direction.INPUT
pin_flow.pull = Pull.UP

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

# variable to accumulate characters read in from the E5 Lora module.
recv_buf = ''

# initial state of the flow switch
flow_state = pin_flow.value

# variables to accumulate flow switch pulses and accumulated heat
heat_count, flow_count = config.starting_counts

COUNT_ROLLOVER = 2**24     # only let the above counts reach 2**24

# Tracks when the last LoRa transmit occurred
_TICKS_MAX = const((1<<29) - 1)
last_xmit = supervisor.ticks_ms()

while True:

    try:

        arr_hot[ix_buf] = pin_thot.value
        arr_cold[ix_buf] = pin_tcold.value
        ix_buf = (ix_buf + 1) % buf_len

        if pin_flow.value != flow_state:
            # a possible change of state occurred
            # ride out the bounces or noise spikes
            time.sleep(0.01)
            new_state = pin_flow.value
            if new_state != flow_state:
                # a real changed occurred
                if new_state == False and flow_state == True:

                    # a switch closure occurred
                    flow_count += 1
                    flow_count = flow_count % COUNT_ROLLOVER

                    t_hot, t_cold, delta_t = current_temps()
                    heat_count += int(delta_t * 10.0)
                    heat_count = max(0, heat_count)   # don't let total go negative
                    heat_count = heat_count % COUNT_ROLLOVER

                    print(flow_count, heat_count, t_hot, t_cold)

                flow_state = new_state

        # Read a character that may have been sent by the E5 module.  Check to 
        # see if they are downlinks & process if so.
        ch = e5_uart.read(1)
        if ch is not None:
            if ch in (b'\n', b'\r'):
                if len(recv_buf):
                    print(recv_buf)
                    lora.check_for_downlink(recv_buf, e5_uart)
                    recv_buf = ''
            else:
                try:
                    recv_buf += str(ch, 'ascii')
                except:
                    print('Bad character:', ch)

        # Check to see if it is time to transmit
        cur_ticks = supervisor.ticks_ms()
        ticks_since_xmit = (cur_ticks - last_xmit) & _TICKS_MAX
        if ticks_since_xmit >= config.secs_between_xmit * 1000:
            last_xmit = cur_ticks
            t_hot, t_cold, _ = current_temps()
            t_hot_tenths = int(t_hot * 10.0 + 0.5)
            t_cold_tenths = int(t_cold * 10.0 + 0.5)
            # Note: below does not deal with negative temperatures F, which should not occur
            msg = f'05{heat_count:06X}{flow_count:06X}{t_hot_tenths:04X}{t_cold_tenths:04X}'
            print(msg)
            lora.send_data(msg, e5_uart)
            # store heat and flow counts in case reboot
            config.starting_counts = (heat_count, flow_count)

    except KeyboardInterrupt:
        sys.exit()
    
    except:
        print('Unknown error.')
        time.sleep(1)
