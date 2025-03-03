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

        self.laser = Extreme()
        print(self.laser.emission_state)
        print(self.laser.power_level)

# -----------------------------------------------------------------------------
    def set_emission(self, state: bool) -> None:
        ''' set_emission'''

        self.laser.set_emission(state)

# -----------------------------------------------------------------------------
    def get_emission(self) -> bool:
        ''' get_emission'''

        state = self.laser.emission_state
        return state

# -----------------------------------------------------------------------------
    def set_power(self, value: float) -> None:
        ''' set_emission'''

        self.laser.set_power(value)

# -----------------------------------------------------------------------------
    def get_power(self) -> float:
        ''' get_power'''

        value = self.laser.power_level
        return value

# -----------------------------------------------------------------------------
    def reset_interlock(self, state: bool) -> None:
        ''' set_interlock'''

        self.laser.set_interlock(1)
