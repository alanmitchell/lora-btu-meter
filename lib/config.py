"""Holds configuration information and also stores/retrieves some settings
from non-volatile memory.
"""
from microcontroller import nvm        # non-volatile memory

ADDR_SECS_BETWEEN_XMIT = 0     # Index of 2-byte integer of # of seconds between transmission

class Configuration:

    # --- Settings related to Average Power Reader
    # If not changed by a downlink, this is the default number seconds between
    # transmission of an average power value.
    SECS_BETWEEN_XMIT_DEFAULT = 600

    def __init__(self):
        # for the few settings that are changeable via downlink, check non-volatile 
        # memory to see what value to use.  NVM bytes will be 255 if they have never
        # been written before.

        # Seconds between Transmissions for Averaging mode
        nvm_val = nvm[ADDR_SECS_BETWEEN_XMIT] * 256 + nvm[ADDR_SECS_BETWEEN_XMIT + 1]
        if nvm_val != (2**16 - 1):
            self._secs_between_xmit = nvm_val
        else:
            self._secs_between_xmit = Configuration.SECS_BETWEEN_XMIT_DEFAULT

    @property
    def secs_between_xmit(self):
        """With the Averaging Reader, seconds between transmission
        of average values."""
        return self._secs_between_xmit

    @secs_between_xmit.setter
    def secs_between_xmit(self, val):
        if val < (2**16 - 1):
            self._secs_between_xmit = val
            nvm[ADDR_SECS_BETWEEN_XMIT] = (val >> 8)
            nvm[ADDR_SECS_BETWEEN_XMIT + 1] = (val & 0xFF)

# Instantiate a Config object that will be imported by modules that need access
# to the configuration information.  So, those modules will execute:
#    from config import config
# to get this object.
config = Configuration()
