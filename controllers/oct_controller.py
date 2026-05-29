from driver.oct_imaging import OctImaging


class OctController:
    def __init__(self):
        self.dev = OctImaging()

    def start_recording(self, **kwargs):
        if self.dev:
            self.dev.start_recording(**kwargs)

    def stop_recording(self):
        if self.dev:
            self.dev.stop_recording()
