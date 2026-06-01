from driver.nidaq import NidaqHandle


class NidaqController:

    def __init__(
        self,
        config,
        state,
        ao_port
    ):

        self.state = state
        self.dev = None

        self.max_position = float(
            config.get("nidaq_max_position", 400)
        )

        self.max_out = float(
            config.get("nidaq_max_out", 5.0)
        )

        self.position = float(
            config.get("nidaq_position", 200)
        )

        if config.get_bool("using_nidaq"):

            self.dev = NidaqHandle(
                config.get("nidaq_device"),
                ao_port,
                config.get("nidaq_ai_port"),
                float(config.get("nidaq_min_out", 0.0)),
                float(config.get("nidaq_max_out", 5.0))
            )

            self.dev.set_position(
                self.position * self.max_out / self.max_position
            )

    def move_absolute(self, pos):

        pos = max(
            0,
            min(
                float(pos),
                self.max_position
            )
        )

        self.position = pos
        self.state.nidaq_position = pos

        if self.dev:

            voltage = (
                pos * self.max_out /
                self.max_position
            )

            self.dev.set_position(voltage)

    def move_relative(self, delta):

        self.move_absolute(
            self.position + delta
        )

