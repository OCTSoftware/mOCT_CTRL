
class SyncController:

    def __init__(self, state, nidaq, kcube):

        self.state = state
        self.nidaq = nidaq
        self.kcube = kcube

    def sync_move(self, kcube_delta, nidaq_delta):
        
        self.kcube.move_relative(kcube_delta)
        self.nidaq.move_relative(nidaq_delta)
