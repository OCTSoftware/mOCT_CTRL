from dataclasses import dataclass


@dataclass
class AxisStatus:

    position: int = 0
    distance: int = 0

    state: int = 0
    jog: bool = False

    home: bool = False
    end: bool = False


class StepperStatus:

    STATE_MAP = {
        0: "Idle",
        1: "Seek",
        2: "Backoff",
        3: "Done",
        4: "Fault",
    }

    def __init__(self):

        self.system_state = 0

        self.x = AxisStatus()
        self.y = AxisStatus()

    # ------------------------------------------------------------
    def parse(self, line):

        if line.startswith("SYS"):
            self._parse_sys(line)

        elif line.startswith("LIM"):
            self._parse_lim(line)

    # ------------------------------------------------------------
    def _parse_sys(self, line):

        parts = line.split()

        if len(parts) < 2:
            return

        self.system_state = int(parts[1])

        data = {}

        i = 2

        while i < len(parts) - 1:

            data[parts[i]] = parts[i + 1]
            i += 2

        self.x.state = int(data.get("A1", self.x.state))
        self.x.position = int(data.get("P1", self.x.position))
        self.x.distance = int(data.get("D1", self.x.distance))
        self.x.jog = bool(int(data.get("S1", 0)))

        self.y.state = int(data.get("A2", self.y.state))
        self.y.position = int(data.get("P2", self.y.position))
        self.y.distance = int(data.get("D2", self.y.distance))
        self.y.jog = bool(int(data.get("S2", 0)))

    # ------------------------------------------------------------
    def _parse_lim(self, line):

        parts = line.split()

        if len(parts) < 2:
            return

        self.system_state = int(parts[1])

        data = {}

        i = 2

        while i < len(parts) - 1:

            data[parts[i]] = parts[i + 1]
            i += 2

        self.x.home = bool(int(data.get("H1", 0)))
        self.x.end = bool(int(data.get("E1", 0)))

        self.y.home = bool(int(data.get("H2", 0)))
        self.y.end = bool(int(data.get("E2", 0)))
