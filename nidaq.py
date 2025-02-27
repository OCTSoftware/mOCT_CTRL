"""
NIDAQCTRL.py

Class to control the NI DAQ devices

Created on Feb 15, 2025 by Martin Ahrens
m.ahrens@uni-luebeck.de
"""

import nidaqmx
import nidaqmx.task

__DEBUG__ = False


class NidaqHandle:
    ''' class NidaqHandle '''

# -----------------------------------------------------------------------------
    def __init__(self, device=str(), ao_channel=str(), ai_channel=str()) -> None:
        ''' __init__ '''

        ao = device + "/" + ao_channel
        ai = device + "/" + ai_channel

        self.upper_limit = 400
        self.lower_limit = 0

        if __DEBUG__:
            print("Analog out channel is", ao)
            print("Analog in  channel is", ai)

        try:
            self.task_out = nidaqmx.Task()
            self.task_out.ao_channels.add_ao_voltage_chan(ao, min_val=0, max_val=5.0)
            self.task_in = nidaqmx.Task()
            self.task_in.ai_channels.add_ai_voltage_chan(ai)

            if __DEBUG__:
                print("Initialize nidaq control")

        except Exception as e:
            print(f"An exception occurred {e}")

# -----------------------------------------------------------------------------
    def set_position(self, analog_out_value: float) -> None:
        ''' set_position '''

        self.task_out.write(analog_out_value, auto_start=True)
        analog_in_value = self.task_in.read()

        if __DEBUG__:
            print(f"Send data: {analog_out_value:f}")
            print(f"Acquired data: {analog_in_value:f}")

# -----------------------------------------------------------------------------
    def get_position(self) -> float:
        ''' get_position '''

        analog_in_value = self.task_in.read()

        if __DEBUG__:
            print(f"Acquired data: {analog_in_value:f}")

        return analog_in_value

# -----------------------------------------------------------------------------
    def close(self) -> None:
        ''' close '''

        self.task_in.close()
        self.task_out.close()

        if __DEBUG__:
            print("Close nidaq control")
