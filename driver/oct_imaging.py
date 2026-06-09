import os
import shutil
import time
import threading
import logging
logger = logging.getLogger(__name__)


class OctImaging:
    def __init__(self):

        self.stop_requested = False
        self.worker = None
        self.last_error = None

    def start_recording(
        self, dest_dir, nbr_of_records, delay_between_rec, nbr_of_bscans
    ):

        if self.worker is not None and self.worker.is_alive():
            raise RuntimeError("Recording already in progress")

        self.stop_requested = False

        self.worker = threading.Thread(
            target=self._record_worker,
            args=(dest_dir, nbr_of_records, delay_between_rec, nbr_of_bscans),
            daemon=True,
        )

        self.worker.start()

    def stop_recording(self):

        self.stop_requested = True

        if self.worker is not None and self.worker.is_alive():
            self.worker.join(timeout=5)

        self.worker = None

    def _record_worker(
        self, dest_dir, nbr_of_records, delay_between_rec, nbr_of_bscans
    ):
        try:
            logger.debug("[OCT_IMAGING] Starting OCT recording")

            os.makedirs(dest_dir, exist_ok=True)

            for i in range(nbr_of_records):
                if self.stop_requested:
                    logger.debug("[OCT_IMAGING] Recording stopped.")
                    return

                logger.debug(f"[OCT_IMAGING] Recording {i + 1}/{nbr_of_records}")

                elapsed = 0
                while elapsed < delay_between_rec:
                    if self.stop_requested:
                        logger.debug("[OCT_IMAGING] Recording stopped.")
                        return

                    time.sleep(0.1)
                    elapsed += 0.1

            logger.debug("[OCT_IMAGING] Recording finished.")

        except Exception as e:
            self.last_error = e
            logger.debug(f"[OCT_IMAGING] OCT recording failed -> {e}")

        finally:
            self.worker = None