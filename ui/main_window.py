
import customtkinter as ctk
from ui.nidaq_frame import NidaqFrame
from ui.kcube_frame import KcubeFrame
from ui.nkt_frame import NktFrame
from ui.stepper_frame import StepperFrame
from ui.sync_frame import SyncFrame
from ui.recording_frame import RecordingFrame
from ui.footer_frame import FooterFrame

class MainWindow(ctk.CTk):
    def __init__(self, config, state, nidaq_controllers, kcube, nkt, sync, stepper, record):
        super().__init__()
        self.title("mOCT CTRL Refactored")
        self.grid_columnconfigure((0,1,2), weight=1)
        
        if nidaq_controllers:
            NidaqFrame(
                self,
                nidaq_controllers,
                config
            ).grid(
                row=0,
                column=0,
                padx=5,
                pady=5,
                sticky="nw"
            )
            
            # NidaqFrame(self, nidaq, config).grid(row=0, column=0, padx=5, pady=5, sticky='nw')
        if stepper:
            StepperFrame(self, stepper, config).grid(row=0, column=1, padx=5, pady=5, sticky='nw')
        if kcube:
            KcubeFrame(self, kcube, config).grid(row=0, column=2, padx=5, pady=5, sticky='nw')
        if nkt:
            NktFrame(self, nkt, config).grid(row=0, column=3, padx=5, pady=5, sticky='nw')
        if sync:
            SyncFrame(self, sync, config).grid(row=1, column=0, columnspan=1, padx=5, pady=5, sticky='nw')
        if record:
            RecordingFrame(self, record, config).grid(row=1, column=1, padx=5, pady=5, sticky='nw')
        
        FooterFrame(self).grid(row=2, column=1, padx=5, pady=5, sticky='sw')
        
        self.protocol(
            "WM_DELETE_WINDOW",
            self.on_closing
        )
        
    def on_closing(self):

        for ctrl in self.nidaq_controllers:

            try:
                ctrl.close()
            except Exception as e:
                print(e)

        self.destroy()
