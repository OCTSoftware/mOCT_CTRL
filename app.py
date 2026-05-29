import atexit
import sys
import traceback

from pathlib import Path
from core.config_manager import ConfigManager
from utils.config_io import CONFIG_IO
from core.app_state import AppState
from controllers.nidaq_controller import NidaqController
from controllers.kcube_controller import KcubeController
from controllers.nkt_controller import NktController
from controllers.sync_controller import SyncController
from controllers.stepper_controller import StepperDriver
from ui.main_window import MainWindow


def create_app():
    config = ConfigManager(Path(__file__).resolve().parent / "resources" / "config.txt")
    state = AppState()

    nidaq = NidaqController(config, state)
    kcube = KcubeController(config, state)
    nkt = NktController(config, state)
    sync = SyncController(state, nidaq, kcube)
    stepper = StepperDriver(config, state)

    shutdown_done = False

    def safe_shutdown():
        nonlocal shutdown_done

        if shutdown_done:
            return

        shutdown_done = True

        if nkt and nkt.dev:
            print("Emergency shutdown")
            nkt.emergency_shutdown()

    atexit.register(safe_shutdown)

    def handle_exception(exc_type, exc_value, exc_traceback):
        traceback.print_exception(exc_type, exc_value, exc_traceback)
        safe_shutdown()

    sys.excepthook = handle_exception

    app = MainWindow(config, state, nidaq, kcube, nkt, sync, stepper)
    nkt.attach_app(app)

    def on_close():
        CONFIG_IO.save_runtime_config(app, config)
        safe_shutdown()
        app.destroy()

    app.protocol("WM_DELETE_WINDOW", on_close)

    return app