"""
pi_gcs_devices.py

from pi_gcs_devices import PIGCSHandle as pi_gcs

pi_gcs.connect(pi_gcs, '9')
pi_gcs.move_abs(pi_gcs, 2)
pi_gcs.move_rel(pi_gcs,-1,1)
pi_gcs.move_rel(pi_gcs,1,1)
pi_gcs.move_fnl(pi_gcs)
pi_gcs.disconnect(pi_gcs)

"""

from time import sleep
from typing import NamedTuple
from pipython import GCSDevice, pitools
from pipython import GCSError, gcserror
import logging
logger = logging.getLogger(__name__)


class StageStatus(NamedTuple):
    """Return values from moving def's"""

    status: int
    position: float


class PIGCSHandle:
    """PIGCSHandle"""

    def __init__(self, comport: str) -> None:
        """__init__"""

        self.pidevice = None
        self.axes = ""
        logger.debug("[PI_GCS_DEVICES]")

    def connect(self, comport: str) -> int:
        """Connect device"""

        status = 0
        self.pidevice = GCSDevice("C-863.11")

        try:
            port = int(comport)
            logger.debug(f"[PI_GCS_DEVICES] Connecting to COM{port}")
            self.pidevice.OpenRS232DaisyChain(comport=port, baudrate=115200)
            dcid = self.pidevice.dcid
            self.pidevice.ConnectDaisyChainDevice(1, dcid)

            idn = self.pidevice.qIDN()
            logger.debug(f"[PI_GCS_DEVICES] Device {idn} connected")

            self.axes = ["1"]  # Setup  axis 1
            pitools.enableaxes(self.pidevice, "1")  # Enable axis 1
            pitools.setservo(self.pidevice, "1", True)  # Turn servo ON for axis 1

            logger.debug("[PI_GCS_DEVICES] Axes 1 connected")
            status = 1

        except GCSError as exc:
            logger.debug(f"[PI_GCS_DEVICES] COM9 GCS failed -> {e}")
            status = -1
            return status

        except OSError as exc:
            logger.debug(f"[PI_GCS_DEVICES] COM9 port failed -> {e}")
            status = -2
            return status
        status = 2

        return status

    def move_fnl(self) -> None:
        """Go to negative limit"""

        self.pidevice.gcscommands.FNL(self.axes)
        while not all(pitools.ontarget(self.pidevice, self.axes).values()):
            sleep(0.05)
        logger.debug("[PI_GCS_DEVICES] Servo reached negative limit")

    def move_abs(self, absolut_position) -> StageStatus[int, float]:
        """
        Move to absolute position
        """
        status = 0
        try:
            axis = self.axes[0]  # '1'
            val = absolut_position

            self.pidevice.send(f"MOV {axis} {val}")

            while not all(pitools.ontarget(self.pidevice, self.axes).values()):
                sleep(0.05)

            current_pos = self.pidevice.gcscommands.qPOS(self.axes)
            position = next(iter(current_pos.values()))
            # print(f'position = {position}')

            status = 1

        except GCSError as exc:
            # Motion / limit error
            if exc == gcserror.E_1024_PI_MOTION_ERROR:
                # Clear controller
                self.pidevice.gcscommands.CLR()
                # Axis-level reset
                for ax in self.axes:
                    self.pidevice.gcscommands.RES(ax)
                status = -1
                return status

        return status, position

    def move_rel(self, relative_position) -> StageStatus[int, float]:
        """
        Move a relative distance
        """
        status = 0
        try:
            axis = self.axes[0]  # '1'

            self.pidevice.send(f"MVR {axis} {relative_position}")

            while not all(pitools.ontarget(self.pidevice, self.axes).values()):
                sleep(0.05)

            current_pos = self.pidevice.gcscommands.qPOS(self.axes)
            position = next(iter(current_pos.values()))
            # print(f'position = {position}')

            status = 1

        except GCSError as exc:
            if exc == gcserror.E_1024_PI_MOTION_ERROR:
                # Clear controller
                self.pidevice.gcscommands.CLR()
                # Axis-level reset
                for ax in self.axes:
                    self.pidevice.gcscommands.RES(ax)
                status = -1
                return status

        return StageStatus(status, position)

    def get_pos(self) -> float:
        """
        Query the position
        """
        current_pos = self.pidevice.gcscommands.qPOS(self.axes)
        position = next(iter(current_pos.values()))
        return position

    def disconnect(self) -> None:
        """
        Disconnect device
        """
        self.pidevice.gcscommands.CloseConnection()
        logger.debug("[PI_GCS_DEVICES] Device disconnected")