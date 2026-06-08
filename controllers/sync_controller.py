from driver.calibration import steps_to_um

import logging

logger = logging.getLogger(__name__)


class SyncController:

    def __init__(self, nidaq_controllers, config):

        self.nidaqs = nidaq_controllers

        self.enabled = config.get_bool("sync", "enabled")

        self.offset = float(config.get("sync", "offset"))

        self.axis_map = {}

        for mapping in config.get("sync", "mappings"):

            axis = mapping["axis"]
            nidaq_idx = mapping["nidaq"] - 1
            self.axis_map[axis] = nidaq_idx

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

            delta_steps = current - previous

            self._last_positions[axis] = current

            if delta_steps == 0:
                continue

            delta_um = steps_to_um(delta_steps)

            logger.debug(
                f"[SYNC MOVE] "
                f"axis={axis} "
                f"steps={delta_steps} "
                f"um={delta_um:.3f} "
                f"voltage={delta_um:.4f}"
            )

            self.nidaqs[idx].move_relative(delta_um)

    def set_enabled(self, enabled):

        logger.debug(f"[SYNC CTRL] enabled={enabled}")

        self.enabled = enabled

        if enabled:
            self._last_positions = None
