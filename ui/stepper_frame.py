# frames/stepper_frame.py

import customtkinter as ctk
import tkinter as tk
import serial.tools.list_ports


class StepperFrame(ctk.CTkFrame):

    # ------------------------------------------------------------------
    def __init__(self, parent, stepper, config):

        super().__init__(parent)

        self.stepper = stepper
        self.config = config
        
        self.stepper_names = ["X", "Y"]

        self.configure(fg_color="#2b2b2b")

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

        ctk.CTkLabel(self.comm_frame, text="Communication", font=("Arial", 16, "bold")).pack(padx=5, pady=(5, 10))

        saved_port = config.get("stepper_port", "")
        self.selected_port = tk.StringVar(value=saved_port)
        self.port_combo = ctk.CTkComboBox(self.comm_frame, variable=self.selected_port, values=self.get_ports(), width=140)
        self.port_combo.pack(padx=5, pady=2)

        saved_baud = config.get("stepper_baudrate", "115200")

        self.baudrate_var = tk.StringVar(value=str(saved_baud))
        self.baud_combo = ctk.CTkComboBox(self.comm_frame, variable=self.baudrate_var, values=["9600", "57600", "115200"], width=140)
        self.baud_combo.pack(padx=5, pady=2)

        self.connect_btn = ctk.CTkButton(self.comm_frame, text="Connect", command=self.connect_stepper)
        self.connect_btn.pack(padx=5, pady=2)

        self.disconnect_btn = ctk.CTkButton(self.comm_frame, text="Disconnect", command=self.disconnect_stepper)
        self.disconnect_btn.pack(padx=5, pady=2)

        ctk.CTkLabel(self.comm_frame, text="Command").pack(padx=5, pady=(10, 2))

        self.command_var = tk.StringVar()
        self.command_entry = ctk.CTkEntry(self.comm_frame, textvariable=self.command_var, width=140)
        self.command_entry.pack(padx=5, pady=2)
        self.command_entry.bind("<Return>", lambda event: self.send_command())

        self.send_btn = ctk.CTkButton(self.comm_frame, text="Send", command=self.send_command)
        self.send_btn.pack(padx=5, pady=2)

        self.status_box = ctk.CTkTextbox(self.comm_frame, width=140, height=100)
        self.status_box.pack(padx=5, pady=(10, 5))

        # ==============================================================
        # STEPPERS
        # ==============================================================

        self.stepper_container = ctk.CTkFrame(self.stepper_frame)
        self.stepper_container.grid(row=0, column=1, padx=5, pady=5, sticky="nsew")

        self.stepper_widgets = {}

        for idx, name in enumerate(self.stepper_names):

            frame = ctk.CTkFrame(self.stepper_container)
            frame.grid(row=idx, column=0, padx=5, pady=5, sticky="n")

            ctk.CTkLabel(frame, text=name, font=("Arial", 16, "bold")).pack(padx=5, pady=(5, 10))

            info_label = ctk.CTkLabel(frame, text="Ready")
            info_label.pack(padx=5, pady=2)

            position_label = ctk.CTkLabel(frame, text="Position: 0")
            position_label.pack(padx=5, pady=2)

            speed_var = tk.StringVar(value="100")
            speed_entry = ctk.CTkEntry(frame, textvariable=speed_var, width=120)
            speed_entry.pack(padx=5, pady=2)
            speed_entry.bind("<Return>", lambda event: self.send_command())

            jog_pos_btn = ctk.CTkButton(frame, text="Jog +", command=lambda n=name: self.jog_positive(n))
            jog_pos_btn.pack(padx=5, pady=2)

            jog_neg_btn = ctk.CTkButton(frame, text="Jog -", command=lambda n=name: self.jog_negative(n))
            jog_neg_btn.pack(padx=5, pady=2)

            limit_label = ctk.CTkLabel(frame, text="Limits: ---")
            limit_label.pack(padx=5, pady=2)

            self.stepper_widgets[name] = {
                "frame": frame,
                "position_label": position_label,
                "speed_var": speed_var,
                "limit_label": limit_label,
                "info_label": info_label,
            }

    # ------------------------------------------------------------------
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

    # ------------------------------------------------------------------
    def connect_stepper(self):

        selected = self.selected_port.get()

        port = self.port_map.get(selected, selected.split(" - ")[0])
        baud = int(self.baudrate_var.get())

        self.stepper.connect(port, baud)

        self.log(f"Connected: {port}")

    # ------------------------------------------------------------------
    def disconnect_stepper(self):

        self.stepper.disconnect()

        self.log("Disconnected")

    # ------------------------------------------------------------------
    def jog_positive(self):

        axis = self.axis_var.get()
        speed = float(self.speed_var.get())

        self.stepper.send_jog_speed(axis, speed)

        self.log(f"Jog + {axis} {speed}")

    # ------------------------------------------------------------------
    def jog_negative(self):

        axis = self.axis_var.get()
        speed = -float(self.speed_var.get())

        self.stepper.send_jog_speed(axis, speed)

        self.log(f"Jog - {axis} {speed}")

    # ------------------------------------------------------------------
    def send_command(self):

        cmd = self.command_var.get()

        self.stepper.send_cmd(cmd)

        self.log(f"CMD: {cmd}")

    # ------------------------------------------------------------------
    def log(self, message):

        self.status_box.insert("end", f"{message}\n")
        self.status_box.see("end")