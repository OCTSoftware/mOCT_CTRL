import logging
logger = logging.getLogger(__name__)
try:
    from driver.kinesis import KcubeHandle
except Exception:
    KcubeHandle = None


class KcubeController:
    def __init__(self, config, state):

        self.state = state
        self.config = config
        self.dev = None

        serial_value = config.get("kcube", "serial_number")

        try:
            self.serial_number = str(int(serial_value))
        except (TypeError, ValueError):
            self.serial_number = None

        if config.get_bool("kcube") and self.serial_number is not None:
            try:
                self.dev = KcubeHandle(self.serial_number) if KcubeHandle else None
            except Exception as e:
                logger.debug(f"[KCUBE_CONTROLLER] KCube initialization failed -> {e}")
                self.dev = None

    def move_relative(self, delta):
        """ """

        self.move_absolute(self.state.kcube_position + delta)

    def move_absolute(self, pos_mm):
        """ """

        pos_mm = max(0, min(float(pos_mm), 100))

        self.state.kcube_position = pos_mm

        if self.dev:
            self.dev.set_position(pos_mm)

    def home(self):
        """ """

        if self.dev:
            self.dev.home()

        self.state.kcube_position = 0