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
        kcube,
        nkt,
        stepper,
        sync_controller,
        record,
    ):
        super().__init__()
        self.title("mOCT CTRL 2.0")
        self.grid_columnconfigure((0, 1, 2), weight=1)

        self.sync_controller = sync_controller

        if nidaq_controllers:
            NidaqFrame(self, nidaq_controllers, config).grid(
                row=0, column=0, padx=(5,5), pady=(5, 5), sticky="nsew"
            )

        if stepper:
            StepperFrame(self, stepper, config, sync_controller).grid(
                row=0, column=1, padx=(5,5), pady=(5, 5), sticky="nsew"
            )
        if kcube:
            KcubeFrame(self, kcube, config).grid(
                row=0, column=2, padx=(5,5), pady=(5, 5), sticky="nsew"
            )
        if nkt:
            NktFrame(self, nkt, config).grid(
                row=0, column=3,padx=(5,5), pady=(5, 5), sticky="nsew"
            )
        if record:
            RecordingFrame(self, record).grid(
                row=0, column=4, padx=(5,5), pady=(5, 5), sticky="nsew"
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