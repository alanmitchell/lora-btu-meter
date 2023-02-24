"""Holds configuration information and also stores/retrieves some settings
from non-volatile memory.
"""
from microcontroller import nvm        # non-volatile memory
import struct

class Configuration:

    # --- Settings related to Average Power Reader
    # If not changed by a downlink, this is the default number seconds between
    # transmission of an average power value.
    SECS_BETWEEN_XMIT_DEFAULT = 600

    def __init__(self):
        # for the few settings that are changeable via downlink, check non-volatile 
        # memory to see what value to use.  NVM bytes will be 255 if they have never
        # been written before.

        # read values from non-volatile storage. Had problems using one
        # struct.unpack statement (treated the H as 4 bytes long).
        self._secs_between_xmit = struct.unpack('H', nvm[0:2])[0]
        self._start_heat_count = struct.unpack('I', nvm[2:6])[0]
        self._start_flow_count = struct.unpack('I', nvm[6:10])[0]

        # set to defaults, if values haven't been initialized
        if self._secs_between_xmit == 2**16 - 1:
            self._secs_between_xmit = SECS_BETWEEN_XMIT_DEFAULT
        if self._start_heat_count >= 2**24 - 1:
            self._start_heat_count = 0
        if self._start_flow_count >= 2**24 - 1:
            self._start_flow_count = 0

    def save_to_nvm(self):
        """Saves the key config variables to non-volatile storage. Had
        trouble with one pack statement as it treated the H as 4 bytes long.
        """
        nvm[0:2] = struct.pack('H', self._secs_between_xmit)
        nvm[2:6] = struct.pack('I', self._start_heat_count)
        nvm[6:10] = struct.pack('I', self._start_flow_count)

    @property
    def secs_between_xmit(self):
        """With the Averaging Reader, seconds between transmission
        of average values."""
        return self._secs_between_xmit

    @secs_between_xmit.setter
    def secs_between_xmit(self, val):
        if val < (2**16 - 1):
            self._secs_between_xmit = val
            self.save_to_nvm()

    @property
    def starting_counts(self):
        """Returns the starting count heat and flow counts.
        """
        return self._start_heat_count, self._start_flow_count

    @starting_counts.setter
    def starting_counts(self, counts):
        if counts[0] < (2**24 - 1):
            self._start_heat_count = counts[0]
        if counts[1] < (2**24 - 1):
            self._start_flow_count = counts[1]
        self.save_to_nvm()

# Instantiate a Config object that will be imported by modules that need access
# to the configuration information.  So, those modules will execute:
#    from config import config
# to get this object.
config = Configuration()
