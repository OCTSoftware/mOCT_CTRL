import logging

logger = logging.getLogger(__name__)


class SyncController:
    
    def __init__(self, nidaq_controllers, config):

        self.nidaqs = nidaq_controllers

        self.enabled = config.get_bool("sync_enabled")

        self.scale = float(config.get("sync_scale", 1.0))

        self.offset = float(config.get("sync_offset", 0.0))

        self.axis_map = {}

        i = 1

        while config.get(f"sync{i}_axis"):
            axis = config.get(f"sync{i}_axis")

            nidaq_idx = int(config.get(f"sync{i}_nidaq")) - 1

            self.axis_map[axis] = nidaq_idx

            i += 1

        self.last_positions = {}

    def update_from_status(self, status):

        logger.debug("SYNC enabled=%s", self.enabled)

        
        if not self.enabled:
            return

        positions = {
            "X": status.x.position,
            "Y": status.y.position,
        }
        
        logger.debug(
            f"[SYNC] enabled={self.enabled} "
            f"X={status.x.position} "
            f"Y={status.y.position}"
        )

        if getattr(self, "_last_positions", None) is None:
            self._last_positions = positions.copy()
            return

        positions = {"X": status.x.position, "Y": status.y.position}

        if not hasattr(self, "_last_positions"):
            self._last_positions = positions.copy()
            return

        for axis, idx in self.axis_map.items():
            if idx >= len(self.nidaqs):
                continue

            current = positions[axis]
            previous = self._last_positions.get(axis, current)

            delta = current - previous

            self._last_positions[axis] = current

            if delta == 0:
                continue

            distance = delta * self.scale + self.offset

            logger.debug(f"[SYNC] {axis} delta={delta} move={distance}")
            logger.debug(f"[SYNC MOVE] axis={axis} delta={delta} distance={distance}")

            self.nidaqs[idx].move_relative(distance)

    def set_enabled(self, enabled):

        self.enabled = enabled
        
        if enabled:
            self._last_positions = None
