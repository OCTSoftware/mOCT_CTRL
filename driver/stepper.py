"""
stepper_controller.py

Controller wrapper for the serial stepper driver.
"""

from driver.stepper import StepperDriver


class StepperController:
    """High-level controller for the stepper driver."""

    def __init__(self, config=None, state=None):

        self.config = config
        self.state = state

        self.driver = StepperDriver(
            callbacks={
                "log": self._log,
                "status_update": self._status_update,
                "error": self._error,
            }
        )

    # -------------------------------------------------------------------------
    def connect(self, port: str, baud: int = 115200) -> bool:
        """Connect to the stepper controller."""

        return self.driver.connect(port, baud)

    # -------------------------------------------------------------------------
    def disconnect(self):
        """Disconnect from the stepper controller."""

        self.driver.disconnect()

    # -------------------------------------------------------------------------
    def send_command(self, command: str, wait_response: bool = False):
        """Send a raw command."""

        self.driver.send_cmd(command, wait_response=wait_response)

    # -------------------------------------------------------------------------
    def jog(self, axis: str, speed: float, wait_response: bool = False):
        """Send jog command."""

        self.driver.send_jog_speed(axis, speed, wait_response=wait_response)

    # -------------------------------------------------------------------------
    def _log(self, message: str, level: str = "info"):
        """Internal log callback."""

        print(f"[STEPPER][{level.upper()}] {message}")

    # -------------------------------------------------------------------------
    def _status_update(self, data):
        """Handle status updates from the driver."""

        if self.state is not None:
            self.state.stepper_status = data

        print(f"[STEPPER][STATUS] {data}")

    # -------------------------------------------------------------------------
    def _error(self, message: str):
        """Handle driver errors."""

        print(f"[STEPPER][ERROR] {message}")
