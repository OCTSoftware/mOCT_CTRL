import customtkinter as ctk
from ui.nidaq_frame import NidaqFrame
from ui.kcube_frame import KcubeFrame
from ui.nkt_frame import NktFrame
from ui.stepper_frame import StepperFrame
from ui.recording_frame import RecordingFrame
from ui.footer_frame import FooterFrame
import logging
logger = logging.getLogger(__name__)


class MainWindow(ctk.CTk):
    def __init__(
        self,
        config,
        state,
        nidaq_controllers,
        kcube_controllers,
        nkt_controllers,
        stepper_controllers,
        sync_controller,
        record,
    ):
        super().__init__()

        self.title("mOCT CTRL 2.0")
        self.grid_columnconfigure((0, 1, 2), weight=1)
        i = -1

        self.sync_controller = sync_controller

        if nidaq_controllers:
            i += 1
            NidaqFrame(self, nidaq_controllers, config).grid(
                row=0, column=i, padx=(5,5), pady=(5, 5), sticky="nsew"
            )

        if stepper_controllers:
            i += 1
            StepperFrame(self, stepper_controllers, config, sync_controller).grid(
                row=0, column=i, padx=(5,5), pady=(5, 5), sticky="nsew"
            )
        if kcube_controllers:
            i += 1
            KcubeFrame(self, kcube_controllers, config).grid(
                row=0, column=i, padx=(5,5), pady=(5, 5), sticky="nsew"
            )
        if nkt_controllers:
            i += 1
            NktFrame(self, nkt_controllers, config).grid(
                row=0, column=i,padx=(5,5), pady=(5, 5), sticky="nsew"
            )
        if record:
            i += 1
            RecordingFrame(self, record).grid(
                row=0, column=i, padx=(5,5), pady=(5, 5), sticky="nsew"
            )

        FooterFrame(self).grid(row=2, column=1, padx=(5,5), pady=(5, 5), sticky="nsew")

        self.protocol("WM_DELETE_WINDOW", self.on_closing)

    def on_closing(self):

        for ctrl in self.nidaq_controllers:
            try:
                ctrl.close()
            except Exception as e:
                logger.debug(f"[MAIN_WINDOW] -> {e}")

        self.destroy()