# frames/stepper_frame.py

import customtkinter as ctk
import tkinter as tk
import serial.tools.list_ports

from utils.led import led
import logging
logger = logging.getLogger(__name__)


class StepperFrame(ctk.CTkFrame):
    def __init__(self, parent, stepper, config, sync_controller=None):

        super().__init__(parent)

        self.stepper = stepper
        logger.debug("[STEPPER_FRAME] type(self.stepper)")
        self.stepper.status_callback = self.update_status
        logger.debug(f"[STEPPER_FRAME] CALLBACK SET: {self.stepper.status_callback}")
        self.config = config

        self.stepper_names = ["X", "Y"]

        self.configure(fg_color="#2b2b2b")

        self.sync_controller = sync_controller

        # ==============================================================
        # LAYOUT
        # ==============================================================

        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)

        # ==============================================================
        # MAIN FRAME
        # ==============================================================

        self.stepper_frame = ctk.CTkFrame(self)
        self.stepper_frame.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")

        # ==============================================================
        # COMMUNICATION
        # ==============================================================

        self.comm_frame = ctk.CTkFrame(self.stepper_frame)
        self.comm_frame.grid(row=0, column=0, padx=5, pady=5, sticky="ns")

        ctk.CTkLabel(
            self.comm_frame, text="Communication", font=("Arial", 16, "bold")
        ).pack(padx=5, pady=(5, 10))

        saved_port = config.get("stepper_port", "")
        self.selected_port = tk.StringVar(value=saved_port)
        self.port_combo = ctk.CTkComboBox(
            self.comm_frame,
            variable=self.selected_port,
            values=self.get_ports(),
            width=140,
        )
        self.port_combo.pack(padx=5, pady=2)

        saved_baud = config.get("stepper_baudrate", "115200")

        self.baudrate_var = tk.StringVar(value=str(saved_baud))
        self.baud_combo = ctk.CTkComboBox(
            self.comm_frame,
            variable=self.baudrate_var,
            values=["9600", "57600", "115200"],
            width=140,
        )
        self.baud_combo.pack(padx=5, pady=2)

        self.connect_btn = ctk.CTkButton(
            self.comm_frame, text="Connect", command=self.connect_stepper
        )
        self.connect_btn.pack(padx=5, pady=2)

        self.disconnect_btn = ctk.CTkButton(
            self.comm_frame, text="Disconnect", command=self.disconnect_stepper
        )
        self.disconnect_btn.pack(padx=5, pady=2)

        ctk.CTkLabel(self.comm_frame, text="Command").pack(padx=5, pady=(10, 2))

        self.command_var = tk.StringVar()
        self.command_entry = ctk.CTkEntry(
            self.comm_frame, textvariable=self.command_var, width=140
        )
        self.command_entry.pack(padx=5, pady=2)
        self.command_entry.bind("<Return>", lambda event: self.send_command())

        self.send_btn = ctk.CTkButton(
            self.comm_frame, text="Send", command=self.send_command
        )
        self.send_btn.pack(padx=5, pady=2)

        self.status_box = ctk.CTkTextbox(self.comm_frame, width=140, height=100)
        self.status_box.pack(padx=5, pady=(10, 5))

        # ==============================================================
        # SYNC
        # ==============================================================
        self.sync_var = ctk.BooleanVar(
            value=(sync_controller.enabled if sync_controller else False)
        )
        self.sync_switch = ctk.CTkSwitch(
            self, text="NIDAQ Sync", variable=self.sync_var, command=self.toggle_sync
        )
        self.sync_switch.deselect()
        self.sync_switch.grid(row=1, column=0, padx=5, pady=5, sticky="w")

        # ==============================================================
        # STEPPERS
        # ==============================================================

        self.stepper_container = ctk.CTkFrame(self.stepper_frame)
        self.stepper_container.grid(row=0, column=1, padx=5, pady=5, sticky="nsew")

        self.stepper_widgets = {}

        for idx, name in enumerate(self.stepper_names):
            frame = ctk.CTkFrame(self.stepper_container)
            frame.grid(row=idx, column=0, padx=5, pady=5, sticky="n")

            ctk.CTkLabel(frame, text=name, font=("Arial", 16, "bold")).pack(
                padx=5, pady=(5, 10)
            )

            state_label = ctk.CTkLabel(frame, text="State: ---")
            state_label.pack(padx=5, pady=2)

            position_label = ctk.CTkLabel(frame, text="Pos: ---")
            position_label.pack(padx=5, pady=2)

            limit_frame = ctk.CTkFrame(frame, fg_color="transparent")
            limit_frame.pack(padx=5, pady=2)

            ctk.CTkLabel(limit_frame, text="Home").grid(row=0, column=0, padx=2)

            home_led = led(limit_frame, size=14, color_on="green")
            home_led.grid(row=0, column=1, padx=2)

            ctk.CTkLabel(limit_frame, text="End").grid(row=0, column=2, padx=(10, 2))

            end_led = led(limit_frame, size=14, color_on="red")
            end_led.grid(row=0, column=3, padx=2)

            speed_var = tk.StringVar(value="100")
            speed_entry = ctk.CTkEntry(frame, textvariable=speed_var, width=120)
            speed_entry.pack(padx=5, pady=2)
            speed_entry.bind("<Return>", lambda event: self.send_command())

            jog_pos_btn = ctk.CTkButton(
                frame, text="Jog +", command=lambda n=name: self.jog_positive(n)
            )
            jog_pos_btn.pack(padx=5, pady=2)

            jog_neg_btn = ctk.CTkButton(
                frame, text="Jog -", command=lambda n=name: self.jog_negative(n)
            )
            jog_neg_btn.pack(padx=5, pady=2)

            self.stepper_widgets[name] = {
                "frame": frame,
                "state_label": state_label,
                "position_label": position_label,
                "home_led": home_led,
                "end_led": end_led,
                "speed_var": speed_var,
            }

    def update_status(self, status):

        self.after(0, lambda: self._update_widgets(status))

    def _update_widgets(self, status):

        self.stepper_widgets["X"]["position_label"].configure(
            text=f"Pos: {status.x.position}"
        )

        self.stepper_widgets["Y"]["position_label"].configure(
            text=f"Pos: {status.y.position}"
        )

        self.stepper_widgets["X"]["state_label"].configure(
            text=f"State: {status.STATE_MAP.get(status.x.state, '?')}"
        )

        self.stepper_widgets["Y"]["state_label"].configure(
            text=f"State: {status.STATE_MAP.get(status.y.state, '?')}"
        )

        if status.x.home:
            self.stepper_widgets["X"]["home_led"].on()
        else:
            self.stepper_widgets["X"]["home_led"].off()

        if status.x.end:
            self.stepper_widgets["X"]["end_led"].on()
        else:
            self.stepper_widgets["X"]["end_led"].off()

        if status.y.home:
            self.stepper_widgets["Y"]["home_led"].on()
        else:
            self.stepper_widgets["Y"]["home_led"].off()

        if status.y.end:
            self.stepper_widgets["Y"]["end_led"].on()
        else:
            self.stepper_widgets["Y"]["end_led"].off()

    def toggle_sync(self):

        if self.sync_controller:
            self.sync_controller.set_enabled(self.sync_var.get())

    def get_ports(self):

        ports = serial.tools.list_ports.comports()

        self.port_map = {}
        labels = []

        for p in ports:
            device = p.device
            desc = p.description or ""
            manu = p.manufacturer or ""

            if desc.lower() in ["n/a", "unknown", ""]:
                desc = "Unknown device"

            if manu and manu.lower() not in ["n/a", "unknown"]:
                label = f"{device} - {desc} ({manu})"
            else:
                label = f"{device} - {desc}"

            labels.append(label)
            self.port_map[label] = device

        return labels

    def connect_stepper(self):

        selected = self.selected_port.get()

        port = self.port_map.get(selected, selected.split(" - ")[0])
        baud = int(self.baudrate_var.get())

        self.stepper.connect(port, baud)

        self.log(f"Connected: {port}")

    def disconnect_stepper(self):

        self.stepper.disconnect()

        self.log("Disconnected")

    def jog_positive(self, axis):

        speed = float(self.stepper_widgets[axis]["speed_var"].get())

        self.stepper.send_jog_speed(axis, speed)

        self.log(f"Jog + {axis} {speed}")

    def jog_negative(self, axis):

        speed = float(self.stepper_widgets[axis]["speed_var"].get())

        self.stepper.send_jog_speed(axis, -speed)

        self.log(f"Jog - {axis} {speed}")

    def send_command(self):

        cmd = self.command_var.get()

        self.stepper.send_cmd(cmd)

        self.log(f"CMD: {cmd}")

    def log(self, message):

        self.status_box.insert("end", f"{message}\n")
        self.status_box.see("end")