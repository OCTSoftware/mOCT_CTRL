"""
stepper.py

Serial communication driver for the TMC2209 stepper controller.
Adapted from StepperGUI.
"""

import queue
import threading
import time
from typing import Callable, Dict, Optional

import serial


class StepperDriver:
    """
    Serial communication driver for TMC2209 stepper controller.

    Handles:
    - Serial connection
    - Command queue
    - Response parsing
    - Async reader thread
    - Callback-based status reporting
    """

    # -------------------------------------------------------------------------
    def __init__(self, config, state):
        """Initialize driver."""
        
        self.config = config
        self.state = state

        self.ser: Optional[serial.Serial] = None
        self.is_connected = False

        self.sys_state = "-"
        self.limits = ""

        self.reader_thread: Optional[threading.Thread] = None

        # Queue for serialized command handling
        self._cmd_queue = queue.Queue()

        self._queue_thread = threading.Thread(
            target=self._process_queue,
            daemon=True,
        )
        self._queue_thread.start()

        self._wait_event = threading.Event()

    # -------------------------------------------------------------------------
    def connect(self, port: str, baud: int = 115200) -> bool:
        """Connect to serial port."""

        try:
            real_port = port.split(" - ")[0]

            self.ser = serial.Serial(
                real_port,
                baudrate=baud,
                timeout=0.1,
                write_timeout=0.1,
            )

            # Allow MCU reset
            time.sleep(2)

            self.is_connected = True

            self._log(
                f"Connected to {port} @ {baud} baud",
                "ok",
            )

            self._start_reader()

            self.send_cmd("STATUS")
            self.send_cmd("LIMITS")

            return True

        except (serial.SerialException, OSError) as exc:
            self._error["error"](f"Connect error: {exc}")
            return False

    # -------------------------------------------------------------------------
    def disconnect(self):
        """Disconnect serial port."""

        self.is_connected = False

        if self.reader_thread and self.reader_thread.is_alive():
            self.reader_thread.join(timeout=1.0)

        if self.ser and self.ser.is_open:
            self.ser.close()

        self.ser = None

        print("[STEPPER] Disconnected")

    # -------------------------------------------------------------------------
    def send_cmd(self, cmd: str, wait_response: bool = False):
        """Queue command for sending."""

        sent_event = threading.Event()
        done_event = threading.Event()

        self._cmd_queue.put(
            (cmd, wait_response, sent_event, done_event)
        )

        if wait_response:
            done_event.wait(timeout=5.0)
        else:
            sent_event.wait(timeout=1.0)

    # -------------------------------------------------------------------------
    def send_jog_speed(self, axis: str, speed: float, wait_response: bool = False):
        """Send jog speed command."""

        cmd = f"JOG {axis} {speed:.1f}"
        self.send_cmd(cmd, wait_response=wait_response)

    # -------------------------------------------------------------------------
    def process_response(self, line: str):
        """Public response parser wrapper."""

        return self._process_response(line)

    # -------------------------------------------------------------------------
    def _send_line(self, line: str):
        """Send raw line over serial."""

        if not self.is_connected or not self.ser or not self.ser.is_open:
            self._log(
                f"Skipped (not connected): {line.strip()}",
                "warn",
            )
            return

        try:
            self.ser.write((line + "\n").encode("ascii"))

            self._log(
                f"TX: {line.strip()}",
                "tx",
            )

        except (
            serial.SerialTimeoutException,
            serial.SerialException,
            OSError,
        ) as exc:
            self._error["error"](f"Serial write error: {exc}")

    # -------------------------------------------------------------------------
    def _process_queue(self):
        """Background queue worker."""

        while True:
            try:
                (
                    cmd,
                    wait_response,
                    sent_event,
                    done_event,
                ) = self._cmd_queue.get(timeout=0.1)

            except queue.Empty:
                continue

            if not self.is_connected or not self.ser or not self.ser.is_open:
                self._log(
                    f"Skipped (not connected): {cmd}",
                    "warn",
                )

                sent_event.set()
                done_event.set()
                self._cmd_queue.task_done()
                continue

            if wait_response:
                self._wait_event.clear()

            self._send_line(cmd)
            sent_event.set()

            if wait_response:
                self._wait_event.wait(timeout=5.0)

            done_event.set()
            self._cmd_queue.task_done()

    # -------------------------------------------------------------------------
    def _start_reader(self):
        """Start serial reader thread."""

        self.reader_thread = threading.Thread(
            target=self._reader_loop,
            daemon=True,
        )

        self.reader_thread.start()

    # -------------------------------------------------------------------------
    def _reader_loop(self):
        """Continuously read serial responses."""

        while self.is_connected and self.ser:
            
            try:
                if self.ser is None:
                    break

                if not self.ser.is_open:
                    break

                line = (
                    self.ser.readline()
                    .decode("ascii", errors="ignore")
                    .strip()
                )

                if line:
                    self._status_update(line)
                    self._process_response(line)

            except (
                serial.SerialException,
                OSError,
                AttributeError,
                TypeError,
            ) as exc:

                if self.is_connected:
                    self._error(
                        f"Serial read error: {exc}"
                    )

                break

    # -------------------------------------------------------------------------
    def _process_response(self, line: str):
        """Parse device responses."""

        parts = line.split()

        if not parts:
            return

        if parts[0] == "OK":
            self._log("Command OK", "ok")
            self._wait_event.set()

        elif parts[0] == "ERR":
            self._log(
                f"Error: {' '.join(parts[1:])}",
                "error",
            )

            self._wait_event.set()

        elif parts[0] == "LIM":
            self.limits = line
            self._status_update(line)

        elif parts[0] == "STATUS":
            self.sys_state = line
            self._status_update(line)

        else:
            self._log(
                f"RX: {line}",
                "rx",
            )

    # ------------------------------------------------------------------
    def _log(self, message, level="info"):

        print(f"[STEPPER][{level.upper()}] {message}")

    # ------------------------------------------------------------------
    def _error(self, message):

        print(f"[STEPPER][ERROR] {message}")

    # ------------------------------------------------------------------
    def _status_update(self, data):

        if hasattr(self, "state") and self.state is not None:
            self.state.stepper_status = data

        print(f"[STEPPER][STATUS] {data}")
