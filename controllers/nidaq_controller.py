import logging
from driver.nidaq import NidaqHandle

logger = logging.getLogger(__name__)


class NidaqController:
    
    def __init__(self,
                 config,
                 state,
                 ao_port,
                 ai_port
    ):

        self.state = state
        
        self.dev = None

        self.min_out = float(config.get("nidaq", "output", "min_voltage",  default=0.0))

        self.max_out = float(config.get("nidaq", "output", "max_voltage",  default=5.0))
        
        self.position = float(config.get("nidaq", "position", "center", default=200))
        
        self.max_position = float(config.get("nidaq", "position", "max", default=400))

        if config.get_bool("devices", "nidaq"):

            self.dev = NidaqHandle(
                config.get("nidaq", "device"),
                ao_port,
                ai_port,
                self.min_out,
                self.max_out,
            )
            
            logger.debug(f"NIDAQ DEV = {self.dev}")
            logger.debug(f"[NIDAQ] AO={ao_port} AI={ai_port}")
                        
            self.dev.set_position(self.position * self.max_out / self.max_position)

    def move_absolute(self, pos):

        pos = max(0, min(float(pos), self.max_position))
        
        logger.debug(f"[NIDAQ_FRAME] move_absolute({pos})")

        self.position = pos
        self.state.nidaq_position = pos

        if self.dev:
            voltage = pos * self.max_out / self.max_position

            self.dev.set_position(voltage)
        
            logger.debug(f"[NIDAQ_FRAME] [move_absolute] self.dev.set_position({voltage})")

    def move_relative(self, delta):

        logger.debug(f"[NIDAQ CTRL] relative {delta}")

        self.move_absolute(self.position + delta)
