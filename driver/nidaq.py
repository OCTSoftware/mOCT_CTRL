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
    """class NidaqHandle"""

    def __init__(
        self,
        device=str(),
        ao_channel=str(),
        ai_channel=str(),
        min_out=float,
        max_out=float,
    ) -> None:
        """
        Init NI-DAQ module

        Args:
            device     (str): Device name of the NI-DAQ modul, e.g. 'Dev1'
            ao_channel (str): Analog out channel, e.g. 'ao1'
            ai_channel (str): Analog in  channel, e.g. 'ai1'

        Return:
            NidaqHandle(device, ao_channel, ai_channel)
        """

        ao = device + "/" + ao_channel
        ai = device + "/" + ai_channel

        if __DEBUG__:
            print("Analog out channel is", ao)
            print("Analog in  channel is", ai)

        try:
            self.task_out = nidaqmx.Task()
            self.task_out.ao_channels.add_ao_voltage_chan(
                ao, min_val=min_out, max_val=max_out
            )
            self.task_in = nidaqmx.Task()
            self.task_in.ai_channels.add_ai_voltage_chan(ai)

            if __DEBUG__:
                print("Initialize nidaq control")

        except Exception as e:
            print(f"An exception occurred {e}\n")
            print("self.task_out = None, self.task_in = None")
            self.task_out = None
            self.task_in = None
            raise

        except Exception as e:
            print(f"An exception occurred {e}")

    def set_position(self, analog_out_value: float) -> None:
        """
        Set position

        Args:
            analog_out_value (float): Output in 0 - 10 V
        """

        self.task_out.write(analog_out_value, auto_start=True)
        analog_in_value = self.task_in.read()

        if __DEBUG__:
            print(f"Send data: {analog_out_value:f}")
            print(f"Acquired data: {analog_in_value:f}")

    def get_position(self) -> float:
        """
        Get position

        Args:
            None

        Returns:
            analog_in_value (float): Analog value: the step size in µm must be
                    calculated afterhands.
        """

        analog_in_value = self.task_in.read()

        if __DEBUG__:
            print(f"Acquired data: {analog_in_value:f}")

        return analog_in_value

    def close(self) -> None:
        """
        Close NI-DAQ module
        """

        try:
            self.task_out.close()
        except Exception:
            pass

        try:
            self.task_in.close()
        except Exception:
            pass

        if __DEBUG__:
            print("Close nidaq control")
