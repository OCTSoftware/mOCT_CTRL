import atexit
import sys
import traceback

from pathlib import Path

from core.config_manager import ConfigManager
from core.app_state import AppState

from utils.config_io import CONFIG_IO

from controllers.nidaq_controller import NidaqController
from controllers.kcube_controller import KcubeController
from controllers.nkt_controller import NktController
from controllers.sync_controller import SyncController
from controllers.stepper_controller import StepperDriver
from controllers.record_manager import RecordManager

from ui.main_window import MainWindow


def create_app():

    config = ConfigManager(
        Path(__file__).resolve().parent / "resources" / "config.txt"
    )

    state = AppState()

    nidaq = NidaqController(config, state) if config.get_bool("using_nidaq") else None
    kcube = KcubeController(config, state) if config.get_bool("using_kcube") else None
    nkt = NktController(config, state) if config.get_bool("using_nkt") else None
    stepper = StepperDriver(config, state) if config.get_bool("using_stepper") else None
    sync = SyncManager(state, nidaq, kcube) if config.get_bool("using_sync") else None
    record = RecordManager(config, state) if config.get_bool("using_record") else None

    shutdown_done = False

    def safe_shutdown():

        nonlocal shutdown_done

        if shutdown_done:
            return

        shutdown_done = True

        if nkt is not None and getattr(nkt, "dev", None):
            print("Emergency shutdown")
            nkt.emergency_shutdown()

    atexit.register(safe_shutdown)

    def handle_exception(exc_type, exc_value, exc_traceback):

        traceback.print_exception(
            exc_type,
            exc_value,
            exc_traceback
        )

        safe_shutdown()

    sys.excepthook = handle_exception

    app = MainWindow(
        config,
        state,
        nidaq,
        kcube,
        nkt,
        sync,
        stepper,
        record
    )

    if nkt is not None:
        nkt.attach_app(app)

    def on_close():

        CONFIG_IO.save_runtime_config(app, config)

        safe_shutdown()

        app.destroy()

    app.protocol("WM_DELETE_WINDOW", on_close)

    return app