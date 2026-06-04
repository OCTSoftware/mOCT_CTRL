import customtkinter as ctk
import tkinter as tk
import serial.tools.list_ports
import logging

from utils.led import led

logger = logging.getLogger(__name__)


class StepperChannelFrame(ctk.CTkFrame):
    
    def __init__(self, parent, stepper, axis):
        
        super().__init__(parent)

        self.stepper = stepper
        self.axis = axis
        self.speed_var = tk.StringVar(value="100")

        ctk.CTkLabel(
            self,
            text=axis,
            font=("Arial", 16, "bold"),
        ).pack(padx=5, pady=(5, 10))

        self.state_label = ctk.CTkLabel(self, text="State: ---")
        self.state_label.pack(padx=5, pady=2)

        self.position_label = ctk.CTkLabel(self, text="Pos: ---")
        self.position_label.pack(padx=5, pady=2)

        limit_frame = ctk.CTkFrame(self, fg_color="transparent")
        limit_frame.pack(padx=5, pady=2)

        ctk.CTkLabel(limit_frame, text="Home").grid(row=0, column=0, padx=2)

        self.home_led = led(limit_frame, size=14, color_on="green")
        self.home_led.grid(row=0, column=1, padx=2)

        ctk.CTkLabel(limit_frame, text="End").grid(row=0, column=2, padx=(10, 2))

        self.end_led = led(limit_frame, size=14, color_on="red")
        self.end_led.grid(row=0, column=3, padx=2)

        ctk.CTkEntry(
            self,
            textvariable=self.speed_var,
            width=120,
        ).pack(padx=5, pady=2)

        ctk.CTkButton(
            self,
            text="Jog +",
            command=self.jog_positive,
        ).pack(padx=5, pady=2)

        ctk.CTkButton(
            self,
            text="Jog -",
            command=self.jog_negative,
        ).pack(padx=5, pady=2)

    def update_status(self, axis_status, state_map):

        self.position_label.configure(text=f"Pos: {axis_status.position}")

        self.state_label.configure(
            text=f"State: {state_map.get(axis_status.state, '?')}"
        )

        self.home_led.on() if axis_status.home else self.home_led.off()
        self.end_led.on() if axis_status.end else self.end_led.off()

    def jog_positive(self):

        speed = float(self.speed_var.get())

        logger.debug(
            f"[StepperChannelFrame] [jog_positive] Axis={self.axis} Speed={speed}"
        )

        self.stepper.send_jog_speed(self.axis, speed)

    def jog_negative(self):

        speed = float(self.speed_var.get())

        logger.debug(
            f"[StepperChannelFrame] [jog_negative] Axis={self.axis} Speed={speed}"
        )

        self.stepper.send_jog_speed(self.axis, -speed)


class StepperFrame(ctk.CTkFrame):
    
    def __init__(self, parent, stepper, config, sync_controller=None):

        super().__init__(parent)

        self.stepper = stepper
        self.config = config
        self.sync_controller = sync_controller
        
        saved_port = config.get("stepper", "port")
        saved_baud = config.get("stepper", "baudrate")
        
        self.stepper_connected = False

        self.stepper.status_callback = self.update_status

        self.stepper_names = ["X", "Y"]

        logger.debug(
            f"[StepperFrame] [__init__] Callback={self.stepper.status_callback}"
        )

        self.configure(fg_color="#2b2b2b")

        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)

        self.stepper_frame = ctk.CTkFrame(self)
        self.stepper_frame.grid(row=0, column=0, padx=5, pady=(5, 10), sticky="nsew")

        ctk.CTkLabel(
            self.stepper_frame,
            text="STEPPER",
            font=("Arial", 18, "bold"),
        ).grid(row=0, column=0, padx=5, pady=(5, 10), sticky="ns")

        self.comm_frame = ctk.CTkFrame(self.stepper_frame)
        self.comm_frame.grid(row=1, column=0, padx=5, pady=5, sticky="ns")

        ctk.CTkLabel(
            self.comm_frame,
            text="Communication",
            font=("Arial", 16, "bold"),
        ).pack(padx=5, pady=(5, 10))
                
        self.selected_port = tk.StringVar(value=saved_port)

        self.port_combo = ctk.CTkComboBox(
            self.comm_frame,
            variable=self.selected_port,
            values=self.get_ports(),
            width=140,
        )
        self.port_combo.pack(padx=5, pady=2)


        self.baudrate_var = tk.StringVar(value=str(saved_baud))

        self.baud_combo = ctk.CTkComboBox(
            self.comm_frame,
            variable=self.baudrate_var,
            values=["9600", "57600", "115200"],
            width=140,
        )
        self.baud_combo.pack(padx=5, pady=2)
        
        self.connect_button = ctk.CTkButton(
            self.comm_frame,
            text="Connect",
            command=self.toggle_connection,
            fg_color="green",
            hover_color="dark green",
        )        
        self.connect_button.pack(padx=5, pady=2)
                
        ctk.CTkButton(
            self.comm_frame,
            text="HOME",
            command=lambda: self.send_command_home(),
        ).pack(padx=5, pady=2)

        ctk.CTkLabel(
            self.comm_frame,
            text="Command",
        ).pack(padx=5, pady=(10, 2))

        self.command_var = tk.StringVar()

        self.command_entry = ctk.CTkEntry(
            self.comm_frame,
            textvariable=self.command_var,
            width=140,
        )
        self.command_entry.pack(padx=5, pady=2)
        self.command_entry.bind("<Return>", lambda event: self.send_command())

        ctk.CTkButton(
            self.comm_frame,
            text="Send",
            command=self.send_command,
        ).pack(padx=5, pady=2)

        self.status_box = ctk.CTkTextbox(
            self.comm_frame,
            width=140,
            height=100,
        )
        self.status_box.pack(padx=5, pady=(10, 5))

        self.sync_var = ctk.BooleanVar(
            value=(sync_controller.enabled if sync_controller else False)
        )

        sync_frame = ctk.CTkFrame(
            self,
            fg_color="transparent"
        )

        sync_frame.grid(
            row=1,
            column=0,
            columnspan=2,
            padx=5,
            pady=5,
            sticky="ew"
        )

        self.sync_switch = ctk.CTkSwitch(
            sync_frame,
            text="NIDAQ Sync",
            variable=self.sync_var,
            command=self.toggle_sync,
        )

        self.sync_switch.pack(
            side="left",
            padx=(0, 10)
        )
        
        self.stepper_container = ctk.CTkFrame(self.stepper_frame)
        
        self.stepper_container.grid(
            row=1,
            column=1,
            padx=5,
            pady=5,
            sticky="nsew",
        )

        self.channels = {}

        for idx, axis in enumerate(self.stepper_names):
            channel = StepperChannelFrame(
                self.stepper_container,
                self.stepper,
                axis,
            )

            channel.grid(
                row=idx,
                column=0,
                padx=5,
                pady=5,
                sticky="n",
            )

            self.channels[axis] = channel

    def update_status(self, status):
        
        self.after(0, lambda: self._update_widgets(status))
        
    def toggle_connection(self):

        if self.stepper_connected:
            self.disconnect_stepper()
        else:
            self.connect_stepper()
            
    def update_connection_button(self):

        if self.stepper_connected:
            self.connect_button.configure(
                text="Disconnect",
                fg_color="red",
                hover_color="#aa0000",
            )
        else:
            self.connect_button.configure(
                text="Connect",
                fg_color="green",
                hover_color="#006600",
            )

    def _update_widgets(self, status):

        self.channels["X"].update_status(status.x, status.STATE_MAP)
        self.channels["Y"].update_status(status.y, status.STATE_MAP)

    def toggle_sync(self):

        logger.debug(f"[SYNC UI] -> {self.sync_var.get()}")

        if self.sync_controller:
            self.sync_controller.set_enabled(
                self.sync_var.get()
            )

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
        
        self.stepper_connected = True
        self.update_connection_button()

        self.log(f"Connected: {port}")

    def disconnect_stepper(self):

        self.stepper.disconnect()
        
        self.stepper_connected = False
        self.update_connection_button()
    
        self.log("Disconnected")

    def send_command(self):

        cmd = self.command_var.get()

        self.stepper.send_cmd(cmd)

        self.log(f"CMD: {cmd}")
            
    def send_command_home(self):

        cmd = "HOMEALL"

        self.stepper.send_cmd(cmd)

        self.log(f"CMD: {cmd}")

    def log(self, message):

        self.status_box.insert("end", f"{message}\n")
        self.status_box.see("end")
