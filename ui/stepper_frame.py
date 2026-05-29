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

        self.configure(fg_color="#2b2b2b")

        # ==============================================================
        # layout
        # ==============================================================
        self.grid_columnconfigure((0, 1, 2), weight=1)

        # ==============================================================
        # FRAME 1 : CONNECTION
        # ==============================================================
        self.connection_frame = ctk.CTkFrame(self)
        self.connection_frame.grid(
            row=0,
            column=0,
            padx=5,
            pady=5,
            sticky="nw"
        )

        ctk.CTkLabel(
            self.connection_frame,
            text="Stepper Connection",
            font=("Arial", 16, "bold")
        ).pack(padx=5, pady=(5, 10))

        self.selected_port = tk.StringVar()

        self.port_combo = ctk.CTkComboBox(
            self.connection_frame,
            variable=self.selected_port,
            values=self.get_ports(),
            width=180
        )

        self.port_combo.pack(padx=5, pady=5)

        self.baudrate_var = tk.StringVar(value="115200")

        self.baud_combo = ctk.CTkComboBox(
            self.connection_frame,
            variable=self.baudrate_var,
            values=["9600", "57600", "115200"],
            width=180
        )

        self.baud_combo.pack(padx=5, pady=5)

        self.connect_btn = ctk.CTkButton(
            self.connection_frame,
            text="Connect",
            command=self.connect_stepper
        )

        self.connect_btn.pack(padx=5, pady=5)

        self.disconnect_btn = ctk.CTkButton(
            self.connection_frame,
            text="Disconnect",
            command=self.disconnect_stepper
        )

        self.disconnect_btn.pack(padx=5, pady=5)

        # ==============================================================
        # FRAME 2A : MOTION
        # ==============================================================
        self.motion_frame = ctk.CTkFrame(self)
        self.motion_frame.grid(
            row=0,
            column=1,
            padx=5,
            pady=5,
            sticky="nw"
        )

        ctk.CTkLabel(
            self.motion_frame,
            text="Motion",
            font=("Arial", 16, "bold")
        ).pack(padx=5, pady=(5, 10))

        self.axis_var = tk.StringVar(value="X")

        self.axis_combo = ctk.CTkComboBox(
            self.motion_frame,
            variable=self.axis_var,
            values=["X", "Y", "Z"]
        )

        self.axis_combo.pack(padx=5, pady=5)

        self.speed_var = tk.StringVar(value="100")

        self.speed_entry = ctk.CTkEntry(
            self.motion_frame,
            textvariable=self.speed_var
        )

        self.speed_entry.pack(padx=5, pady=5)

        self.jog_pos_btn = ctk.CTkButton(
            self.motion_frame,
            text="Jog +",
            command=self.jog_positive
        )

        self.jog_pos_btn.pack(padx=5, pady=5)

        self.jog_neg_btn = ctk.CTkButton(
            self.motion_frame,
            text="Jog -",
            command=self.jog_negative
        )

        self.jog_neg_btn.pack(padx=5, pady=5)

        # ==============================================================
        # FRAME 2B : STATUS
        # ==============================================================
        self.status_frame = ctk.CTkFrame(self)
        self.status_frame.grid(
            row=0,
            column=2,
            padx=5,
            pady=5,
            sticky="nw"
        )

        ctk.CTkLabel(
            self.status_frame,
            text="Status",
            font=("Arial", 16, "bold")
        ).pack(padx=5, pady=(5, 10))

        self.status_box = ctk.CTkTextbox(
            self.status_frame,
            width=300,
            height=200
        )

        self.status_box.pack(padx=5, pady=5)

        # ==============================================================
        # FRAME 2C : LIMITS
        # ==============================================================
        self.limit_frame = ctk.CTkFrame(self)
        self.limit_frame.grid(
            row=1,
            column=0,
            padx=5,
            pady=5,
            sticky="nw"
        )

        ctk.CTkLabel(
            self.limit_frame,
            text="Limits",
            font=("Arial", 16, "bold")
        ).pack(padx=5, pady=(5, 10))

        self.limit_label = ctk.CTkLabel(
            self.limit_frame,
            text="---"
        )

        self.limit_label.pack(padx=5, pady=5)

        # ==============================================================
        # FRAME 3A : RAW COMMANDS
        # ==============================================================
        self.command_frame = ctk.CTkFrame(self)
        self.command_frame.grid(
            row=1,
            column=1,
            padx=5,
            pady=5,
            sticky="nw"
        )

        ctk.CTkLabel(
            self.command_frame,
            text="Commands",
            font=("Arial", 16, "bold")
        ).pack(padx=5, pady=(5, 10))

        self.command_var = tk.StringVar()

        self.command_entry = ctk.CTkEntry(
            self.command_frame,
            textvariable=self.command_var,
            width=200
        )

        self.command_entry.pack(padx=5, pady=5)

        self.send_btn = ctk.CTkButton(
            self.command_frame,
            text="Send",
            command=self.send_command
        )

        self.send_btn.pack(padx=5, pady=5)

        # ==============================================================
        # FRAME 4A : INFO
        # ==============================================================
        self.info_frame = ctk.CTkFrame(self)
        self.info_frame.grid(
            row=1,
            column=2,
            padx=5,
            pady=5,
            sticky="nw"
        )

        ctk.CTkLabel(
            self.info_frame,
            text="Info",
            font=("Arial", 16, "bold")
        ).pack(padx=5, pady=(5, 10))

        self.info_label = ctk.CTkLabel(
            self.info_frame,
            text="Stepper Ready"
        )

        self.info_label.pack(padx=5, pady=5)

    # ------------------------------------------------------------------
    def get_ports(self):

        ports = serial.tools.list_ports.comports()

        return [p.device for p in ports]

    # ------------------------------------------------------------------
    def connect_stepper(self):

        port = self.selected_port.get()
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