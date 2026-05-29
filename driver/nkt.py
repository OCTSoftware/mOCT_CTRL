"""
nkt.py

Class to control the laser

Created on Feb 27, 2025 by Martin Ahrens
m.ahrens@uni-luebeck.de
"""

# https://nkt-tools.readthedocs.io/en/latest/examples.html

from nkt_tools.extreme import Extreme


class NktHandle:
    ''' NktHandle '''

# -----------------------------------------------------------------------------
    def __init__(self, comport: str) -> None:
        ''' __init__'''

        self.watchdog_timeout = 5
        self.default_current = 100


        self.laser = Extreme()
        print(self.laser.emission_state)
        print(self.laser.power_level)



# -----------------------------------------------------------------------------
    def _kick_watchdog(self):
        ''' refresh watchdog '''

        self.laser.set_watchdog_interval(self.watchdog_timeout)

# -----------------------------------------------------------------------------
    def set_emission(self, state: bool) -> None:
        ''' set_emission'''

        self._kick_watchdog()

        if state:
            self.laser.set_emission(True)
        else:
            self.laser.set_emission(False)

# -----------------------------------------------------------------------------
    def get_emission(self) -> bool:
        ''' get_emission'''

        state = self.laser.emission_state
        return state

# -----------------------------------------------------------------------------
    def set_current(self, value: float) -> None:
        ''' set_current'''

        self._kick_watchdog()
        self.laser.set_current(value)

# -----------------------------------------------------------------------------
    def get_power(self) -> float:
        ''' get_power'''

        value = self.laser.power_level
        return value

# -----------------------------------------------------------------------------
    def reset_interlock(self) -> None:
        ''' set_interlock'''

        self._kick_watchdog()
        self.laser.set_interlock(1)

# -----------------------------------------------------------------------------
    def emergency_shutdown(self):
        ''' emergency shutdown '''

        try:
            self.laser.set_emission(False)
            self.laser.set_current(0)
        except Exception as e:
            print("Emergency shutdown failed:", e)