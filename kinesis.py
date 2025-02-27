"""
KINESIS.py

Class to control the Thorlabs Piezo stage

Created on Oct 6, 2023 by Maron Dolling
m.dolling@uni-luebeck.de
"""

import time
import clr

clr.AddReference("C:\\Program Files\\Thorlabs\\Kinesis\\Thorlabs.MotionControl.DeviceManagerCLI.dll.")
clr.AddReference("C:\\Program Files\\Thorlabs\\Kinesis\\Thorlabs.MotionControl.GenericMotorCLI.dll.")
clr.AddReference("C:\\Program Files\\Thorlabs\\Kinesis\\Thorlabs.MotionControl.KCube.BrushlessMotorCLI.dll.")

from Thorlabs.MotionControl.DeviceManagerCLI import *
from Thorlabs.MotionControl.GenericMotorCLI import *
from Thorlabs.MotionControl.KCube.BrushlessMotorCLI import *
from System import Decimal

__DEBUG__ = False


class KcubeHandle:
    ''' Class KcubeHandle '''

    stage_enabled = False
    stage_homed = False

# -----------------------------------------------------------------------------
    def __init__(self, serial_no: str) -> None:
        '''
        Initialize instance: load DLLs and connect to KCube
        '''

        DeviceManagerCLI.BuildDeviceList()
        self.serial_no = serial_no

        # create device
        self.kcube = KCubeBrushlessMotor.CreateKCubeBrushlessMotor(self.serial_no)

        # Connect, begin polling, and enable
        self.kcube.Connect(self.serial_no)
        time.sleep(0.25)
        self.kcube.StartPolling(250)
        time.sleep(0.25)
        self.kcube.EnableDevice()

        # Get Device information
        self.device_info = self.kcube.GetDeviceInfo()

        # Wait for Settings to Initialise
        if not self.kcube.IsSettingsInitialized():
            self.kcube.WaitForSettingsInitialized(10000)  # 10 second timeout
            assert self.kcube.IsSettingsInitialized() is True

        # Before homing or moving device, ensure the motors configuration is loaded
        m_config = self.kcube.LoadMotorConfiguration(self.serial_no, DeviceConfiguration.DeviceSettingsUseOptionType.UseDeviceSettings)

        time.sleep(1)
        self.set_velocity_params()
        self.stage_enabled = True
        if __DEBUG__:
            print("KCube connected")

# -----------------------------------------------------------------------------
    def home(self) -> None:
        '''
        Set home position.
        '''

        self.kcube.Home(60000)  # 60 second timeout
        if __DEBUG__:
            print("KCube homed")

# -----------------------------------------------------------------------------
    def set_position(self, value: float) -> None:
        '''
        Move the stage to a certain position.
        '''

        value = Decimal(value)
        self.kcube.MoveTo(value, 60000)
        if __DEBUG__:
            print(f"KCube position is {value:.2f}")

# -----------------------------------------------------------------------------
    def get_position(self) -> float:
        '''
        Move the stage to a certain position.
        '''

        value = self.kcube.get_Position()
        if __DEBUG__:
            print(f"KCube position is {value:.2f}")

        return float(value)

# -----------------------------------------------------------------------------
    def set_velocity_params(self, velocity_key: str = "medium") -> None:
        '''
        Change the preset Kcube velocity parameters.
        '''

        match velocity_key:
            case "slow":            # for small and slow movement
                velocity = 1
            case "medium":          # default
                velocity = 50
            case "fast":            # faster
                velocity = 500
            case "slider_control":  # for slider control, faster response is necessary
                velocity = 1000
            case _:
                print("Invalid velocity param command given")

        # set the desired velocity params
        self.kcube.SetVelocityParams(Decimal(velocity), Decimal(velocity))

# -----------------------------------------------------------------------------
    def enable(self) -> None:
        '''
        Enable / disable  KCube
        '''

        if self.stage_enabled is True:
            self.kcube.DisableDevice()
            if __DEBUG__:
                print("KCube disabled")

        else:
            self.kcube.EnableDevice()
            if __DEBUG__:
                print("KCube enabled")

# -----------------------------------------------------------------------------
    def disconnect(self) -> None:
        '''
        Stop polling, disable and disconnect the device.
        '''

        self.kcube.StopPolling()
        self.kcube.DisableDevice()
        self.stage_enabled = False
        self.kcube.Disconnect(True)
        if __DEBUG__:
            print("KCube disconnected")
