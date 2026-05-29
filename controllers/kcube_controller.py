from driver.kinesis import KcubeHandle


class KcubeController:

    def __init__(self, config, state):
        
        self.state = state
        self.config = config
        self.dev = None

        serial_value = config.get("kcube_serial_number")

        try:
            self.serial_number = str(int(serial_value))
        except (TypeError, ValueError):
            self.serial_number = None

        if config.get_bool("using_kcube") and self.serial_number is not None:
            try:
                self.dev = KcubeHandle(self.serial_number)
            except Exception as exc:
                print(f"KCube initialization failed: {exc}")
                self.dev = None

    def move_relative(self, delta):
        """

        """

        self.move_absolute(self.state.kcube_position + delta)

    def move_absolute(self, pos_mm):
        """
        
        """

        pos_mm = max(0, min(float(pos_mm), 100))

        self.state.kcube_position = pos_mm

        if self.dev:
            self.dev.set_position(pos_mm)

    def home(self):
        """
        
        """

        if self.dev:
            self.dev.home()

        self.state.kcube_position = 0
