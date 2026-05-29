
from driver.nidaq import NidaqHandle

class NidaqController:

    def __init__(self, config, state):

        self.state = state
        self.dev = None
        self.position = float(config.get('nidaq_position', 200))

        if config.get_bool('using_nidaq'):
            self.dev = NidaqHandle(
                config.get('nidaq_device'),
                config.get('nidaq_ao_port'),
                config.get('nidaq_ai_port'),
                float(config.get('nidaq_min_out')),
                float(config.get('nidaq_max_out'))
            )

            self.position = float(config.get('nidaq_position', 200))
            self.dev.set_position(self.position * 10 / 400)


    def move_absolute(self, pos):

        pos = max(0, min(float(pos), 400))
        self.state.nidaq_position = pos
        if self.dev:
            self.dev.set_position(pos * 10 / 400)

    def move_relative(self, delta):

        self.move_absolute(self.state.nidaq_position + delta)
