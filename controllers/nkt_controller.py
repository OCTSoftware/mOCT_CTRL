from driver.nkt import NktHandle


class NktController:
    def __init__(self, config, state):
        self.state = state
        self.state.nkt_power = 100

        self.dev = None
        self.app = None
        self.watchdog_job = None

        if config.get_bool("using_nkt"):
            try:
                self.dev = NktHandle(config.get("nkt_device"))
            except Exception as e:
                print("NKT initialization failed:", e)
                self.dev = None

    def attach_app(self, app):
        self.app = app

    def _refresh_watchdog(self):
        if not self.dev:
            return

        if not self.state.laser_enabled:
            return

        self.dev._kick_watchdog()

        if self.app:
            self.watchdog_job = self.app.after(2000, self._refresh_watchdog)

    def toggle(self):
        self.state.laser_enabled = not self.state.laser_enabled

        if self.dev:
            self.dev.set_emission(self.state.laser_enabled)

        if self.state.laser_enabled:
            self._refresh_watchdog()
        else:
            if self.watchdog_job and self.app:
                self.app.after_cancel(self.watchdog_job)
                self.watchdog_job = None

    def set_current(self, current):
        self.state.nkt_power = current

        if self.dev:
            self.dev.set_current(current)

    def reset_interlock(self):
        if self.dev:
            self.dev.reset_interlock()

    def emergency_shutdown(self):
        if self.dev:
            self.dev.emergency_shutdown()
