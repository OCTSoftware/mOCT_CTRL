"""
main.py

Class to control the config file

Created on Feb 20, 2025 by Martin Ahrens
m.ahrens@uni-luebeck.de
"""

from version import __version__
from PIL import Image, ImageTk
from pathlib import Path
import customtkinter as ctk
import math

from fileIO import FILEIO

from nidaq import NidaqHandle
from kinesis import KcubeHandle


class App(ctk.CTk):
    """ Main app """

    config_path = str(Path.cwd()) + "\\_internal\\" + "config.txt"

    using_kcube = bool(FILEIO.read_value(config_path, 'using_kcube'))
    using_nidaq = bool(FILEIO.read_value(config_path, 'using_nidaq'))
    using_gui_control = bool(FILEIO.read_value(config_path, 'using_gui_control'))

    nidaq_DRV_MODE = str(FILEIO.read_value(config_path, 'nidaq_DRV_MODE'))

    def __init__(self):
        super().__init__()

        self.title("mOCT CTRL / " + __version__)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.kcube_position = float(0.0)
        self.nidaq_position = float(0.0)

        self.appearance_mode = "light"

        if self.using_nidaq is True:

            nidaq_device = FILEIO.read_value(self.config_path, 'nidaq_device')
            nidaq_ao_port = FILEIO.read_value(self.config_path, 'nidaq_ao_port')
            nidaq_ai_port = FILEIO.read_value(self.config_path, 'nidaq_ai_port')

            self.nidaq_position = float(FILEIO.read_value(self.config_path, 'nidaq_position'))

        if self.using_kcube is True:

            kcube_serial_number = FILEIO.read_value(self.config_path, 'kcube_serial_number')
            last_selected = FILEIO.read_value(self.config_path, 'last_selected')

# region GUI

# region NIDAQ

        if self.using_nidaq is True:

            self.nidaq_f0 = ctk.CTkFrame(self, fg_color="transparent")
            self.nidaq_f0.grid(row=0, column=0, padx=(5, 2.5), pady=(5, 5), sticky="nw")

            self.nidaq_f01 = ctk.CTkFrame(self.nidaq_f0, fg_color="transparent")
            self.nidaq_f01.grid(row=0, column=0, padx=(5, 2.5), pady=(5, 5), sticky="nw")

            self.nidaq_lb = ctk.CTkLabel(self.nidaq_f01, width=75, height=20, font=("Cosmic Sans MS", 18, "normal"), text="MIPOS")
            self.nidaq_lb.grid(row=0, column=0, padx=(5, 5), pady=(5, 5))

            image = Image.open("_internal/focus.png")
            ctk_image = ctk.CTkImage(light_image=image, dark_image=image, size=(40, 40))
            self.label = ctk.CTkLabel(self.nidaq_f01, image=ctk_image, text="")
            self.label.grid(row=0, column=1, padx=(0, 0), pady=(0, 0))

            self.nidaq_f1 = ctk.CTkFrame(self.nidaq_f0, border_width=1, fg_color="transparent")
            self.nidaq_f1.grid(row=1, column=0, padx=(5, 5), pady=(5, 5))

            self.nidaq_f2 = ctk.CTkFrame(self.nidaq_f1, fg_color="transparent")
            self.nidaq_f2.grid(row=3, column=0, padx=(5, 5), pady=(15, 15))

            self.nidaq_bt_p50 = ctk.CTkButton(self.nidaq_f2, width=75, height=20, text="+50", command=self.nidaq_move_up_50)
            self.nidaq_bt_p50.grid(row=0, column=0, padx=(5, 5), pady=(5, 5))

            self.nidaq_bt_p10 = ctk.CTkButton(self.nidaq_f2, width=75, height=20, text="+10", command=self.nidaq_move_up_10)
            self.nidaq_bt_p10.grid(row=1, column=0, padx=(5, 5), pady=(5, 5))

            self.nidaq_bt_p1 = ctk.CTkButton(self.nidaq_f2, width=75, height=20, text="+ 1", command=self.nidaq_move_up_1)
            self.nidaq_bt_p1.grid(row=2, column=0, padx=(5, 5), pady=(5, 5))

            self.nidaq_sldr = ctk.CTkSlider(self.nidaq_f2, orientation=ctk.VERTICAL, height=120, from_=0, to=400)
            self.nidaq_sldr.grid(row=4, column=0, padx=(5, 5), pady=(0, 0))
            self.nidaq_sldr.bind("<ButtonPress-1>", self.nidaq_on_mouse_down)
            self.nidaq_sldr.bind("<ButtonRelease-1>", self.nidaq_on_mouse_up)
            self.nidaq_sldr.bind("<B1-Motion>", self.nidaq_on_slider_move)

            self.nidaq_bt_m1 = ctk.CTkButton(self.nidaq_f2, width=75, height=20, text="- 1", command=self.nidaq_move_down_1)
            self.nidaq_bt_m1.grid(row=5, column=0, padx=(5, 5), pady=(5, 5))

            self.nidaq_bt_m10 = ctk.CTkButton(self.nidaq_f2, width=75, height=20, text="-10", command=self.nidaq_move_down_10)
            self.nidaq_bt_m10.grid(row=6, column=0, padx=(5, 5), pady=(5, 5))

            self.nidaq_bt_m50 = ctk.CTkButton(self.nidaq_f2, width=75, height=20, text="-50", command=self.nidaq_move_down_50)
            self.nidaq_bt_m50.grid(row=7, column=0, padx=(5, 5), pady=(5, 5))

            self.nidaq_f3 = ctk.CTkFrame(self.nidaq_f1, fg_color="transparent")
            self.nidaq_f3.grid(row=3, column=1, padx=(5, 5), pady=(0, 0))

            self.nidaq_lb = ctk.CTkLabel(self.nidaq_f3, width=75, height=20)
            self.nidaq_lb.grid(row=0, column=0, padx=(5, 5), pady=(5, 5))

            self.nidaq_tf = ctk.CTkEntry(self.nidaq_f3, width=75, height=20, justify="center")
            self.nidaq_tf.grid(row=1, column=0, padx=(5, 5), pady=(5, 5))
            self.nidaq_tf.insert(0, "0")

            self.nidaq_bt_go = ctk.CTkButton(self.nidaq_f3, width=75, height=20, text="Go", command=self.nidaq_go)
            self.nidaq_bt_go.grid(row=2, column=0, padx=(5, 5), pady=(5, 5))

            self.nidaq_bt_center = ctk.CTkButton(self.nidaq_f3, width=75, height=20, text="Center", command=self.nidaq_center)
            self.nidaq_bt_center.grid(row=3, column=0, padx=(5, 5), pady=(5, 5))

# endregion

# region KINESIS

        if self.using_kcube is True:

            self.kcube_f0 = ctk.CTkFrame(self, fg_color="transparent")
            self.kcube_f0.grid(row=0, column=1, padx=(2.5, 5), pady=(5, 5), sticky="nw")

            self.kcube_f01 = ctk.CTkFrame(self.kcube_f0, fg_color="transparent")
            self.kcube_f01.grid(row=0, column=0, padx=(5, 2.5), pady=(5, 5), sticky="nw")

            self.kcube_lb = ctk.CTkLabel(self.kcube_f01, width=75, height=20, font=("Cosmic Sans MS", 18, "normal"), text="KINESIS")
            self.kcube_lb.grid(row=0, column=0, padx=(5, 5), pady=(5, 5))

            image = Image.open("_internal/zref.png")
            ctk_image = ctk.CTkImage(light_image=image, dark_image=image, size=(40, 40))
            self.label = ctk.CTkLabel(self.kcube_f01, image=ctk_image, text="")
            self.label.grid(row=0, column=1, padx=(0, 40), pady=(0, 0))

            self.kcube_f1 = ctk.CTkFrame(self.kcube_f0, border_width=1, fg_color="transparent")
            self.kcube_f1.grid(row=1, column=0, padx=(5, 5), pady=(5, 5), sticky="nw")

            self.kcube_f2 = ctk.CTkFrame(self.kcube_f1, fg_color="transparent")
            self.kcube_f2.grid(row=0, column=0, padx=(5, 5), pady=(10, 10))

            self.kcube_f3 = ctk.CTkFrame(self.kcube_f2, fg_color="transparent")
            self.kcube_f3.grid(row=1, column=0, padx=(5, 5), pady=(0, 0))

            self.kcube_bt_p100 = ctk.CTkButton(self.kcube_f3, width=75, height=20, text="+100 µm", command=self.kcube_move_up_100)
            self.kcube_bt_p100.grid(row=0, column=0, padx=(5, 5), pady=(5, 5))

            self.kcube_bt_p50 = ctk.CTkButton(self.kcube_f3, width=75, height=20, text="+50 µm", command=self.kcube_move_up_50)
            self.kcube_bt_p50.grid(row=1, column=0, padx=(5, 5), pady=(5, 5))

            self.kcube_bt_p10 = ctk.CTkButton(self.kcube_f3, width=75, height=20, text="+10 µm", command=self.kcube_move_up_10)
            self.kcube_bt_p10.grid(row=2, column=0, padx=(5, 5), pady=(5, 5))

            self.kcube_sldr = ctk.CTkSlider(self.kcube_f3, orientation=ctk.VERTICAL, height=120, from_=0, to=100)
            self.kcube_sldr.grid(row=3, column=0, padx=(5, 5), pady=(0, 0))
            self.kcube_sldr.bind("<ButtonPress-1>", self.kcube_on_mouse_down)
            self.kcube_sldr.bind("<ButtonRelease-1>", self.kcube_on_mouse_up)
            self.kcube_sldr.bind("<B1-Motion>", self.kcube_on_slider_move)

            self.kcube_bt_m10 = ctk.CTkButton(self.kcube_f3, width=75, height=20, text="-10 µm", command=self.kcube_move_down_10)
            self.kcube_bt_m10.grid(row=4, column=0, padx=(5, 5), pady=(5, 5))

            self.kcube_bt_m50 = ctk.CTkButton(self.kcube_f3, width=75, height=20, text="-50 µm", command=self.kcube_move_down_50)
            self.kcube_bt_m50.grid(row=5, column=0, padx=(5, 5), pady=(5, 5))

            self.kcube_bt_m100 = ctk.CTkButton(self.kcube_f3, width=75, height=20, text="-100 µm", command=self.kcube_move_down_100)
            self.kcube_bt_m100.grid(row=7, column=0, padx=(5, 5), pady=(5, 5))

            self.kcube_f4 = ctk.CTkFrame(self.kcube_f2, fg_color="transparent")
            self.kcube_f4.grid(row=1, column=1, padx=(5, 5), pady=(0, 0))

            self.kcube_lb_position = ctk.CTkLabel(self.kcube_f4, width=75, height=20, text="")
            self.kcube_lb_position.grid(row=0, column=0, padx=(5, 5), pady=(5, 5))

            self.kcube_tf_position = ctk.CTkEntry(self.kcube_f4, width=75, height=20, justify="center", placeholder_text="pos / mm")
            self.kcube_tf_position.grid(row=1, column=0, padx=(5, 5), pady=(5, 5))
            self.kcube_tf_position.insert(0, "0")

            self.kcube_bt_go = ctk.CTkButton(self.kcube_f4, width=75, height=20, text="Go", command=self.kcube_go)
            self.kcube_bt_go.grid(row=2, column=0, padx=(5, 5), pady=(5, 5))

            self.kcube_lb_void = ctk.CTkLabel(self.kcube_f4, width=75, height=20, text="")
            self.kcube_lb_void.grid(row=4, column=0, padx=(5, 5), pady=(5, 5))

            self.kcube_f5 = ctk.CTkFrame(self.kcube_f2, fg_color="transparent")
            self.kcube_f5.grid(row=1, column=2, padx=(5, 5), pady=(0, 0))

            self.kcube_cb_speed = ctk.CTkComboBox(self.kcube_f5, width=75, height=20, values=["slow", "medium", "fast"], command=self.kcube_velocity_parameter)
            self.kcube_cb_speed.grid(row=0, column=0, padx=(5, 5), pady=(100, 5))

            self.kcube_bt_enable = ctk.CTkButton(self.kcube_f5, width=75, height=20, text="Enable", command=self.kcube_enable)
            self.kcube_bt_enable.grid(row=1, column=0, padx=(5, 5), pady=(5, 5))

            self.kcube_bt_home = ctk.CTkButton(self.kcube_f5, width=75, height=20, text="Home", command=self.kcube_home)
            self.kcube_bt_home.grid(row=2, column=0, padx=(5, 5), pady=(5, 5))

            self.kcube_cb_objective = ctk.CTkComboBox(self.kcube_f5, width=75, height=20, values=["home", "05x16", "10x03", "20x05", "40x08"], command=self.kcube_objective)
            self.kcube_cb_objective.grid(row=3, column=0, padx=(5, 5), pady=(5, 5))

            kcube_sn_info = "SN: " + kcube_serial_number
            self.kcube_lb_vers = ctk.CTkLabel(self.kcube_f5, width=75, height=20, font=("Cosmic Sans MS", 10, "normal"), text=kcube_sn_info)
            self.kcube_lb_vers.grid(row=4, column=0, padx=(5, 5), pady=(70, 5))
# endregion

# region GUI controls

        if self.using_kcube is True:

            self.f3 = ctk.CTkFrame(self, fg_color="transparent")
            self.f3.grid(row=1, column=1, padx=(5, 5), pady=(0, 5), sticky="se")

            self.f31 = ctk.CTkFrame(self.f3, fg_color="transparent")
            self.f31.grid(row=0, column=0, padx=(5, 5), pady=(0, 0))

            self.f3_switch = ctk.CTkSwitch(self.f31, text="Dark/Light", command=self.set_appearance_mode, onvalue="dark", offvalue="light")
            self.f3_switch.grid(row=0, column=0, padx=(5, 5), pady=(5, 5))

            self.f3_bt_1 = ctk.CTkButton(self.f31, width=75, height=20, text="Save", fg_color='gray')
            self.f3_bt_1.grid(row=0, column=1, padx=(5, 5), pady=(5, 5))

            self.f3_bt_2 = ctk.CTkButton(self.f31, width=75, height=20, text="Exit", command=self.exit)
            self.f3_bt_2.grid(row=0, column=2, padx=(5, 5), pady=(5, 5))

# endregion

# region device setup

        if self.using_nidaq is True:

            self.nidaq = NidaqHandle(nidaq_device, nidaq_ao_port, nidaq_ai_port)
            self.nidaq_lower = self.nidaq.lower_limit
            self.nidaq_upper = self.nidaq.upper_limit
            self.nidaq_init()

        if self.using_kcube is True:

            self.kcube = KcubeHandle(str(int(kcube_serial_number)))
            self.kcube_cb_objective.set(last_selected)
            self.kcube_position = FILEIO.read_value(self.config_path, last_selected)

            self.kcube.stage_enabled = True
            self.kcube_bt_enable.configure(fg_color='green', text='enabled')
            self.kcube_lb_position.configure(text=str(self.kcube_position))
            self.kcube_sldr.set(float(self.kcube_position))


# endregion

# region MIPOS related commands

    def init_nidaq(self, device=str(), ao_channel=str(), ai_channel=str()) -> None:
        ''' init_nidaq '''

        return NidaqHandle(device, ao_channel, ai_channel)

    def close_nidaq(self) -> None:
        ''' close_nidaq '''

        self.nidaq.close()

    def update_nidaq(self, value) -> None:
        ''' update_nidaq '''

        self.nidaq.set_position(value)
        self.nidaq_update_stage_position_label()

    def value_to_analog_out_value(self, value) -> float:
        ''' value_to_analog_out_value '''

        # Range of the Stage:  0 ... 400 µm
        # Range of the DAQ  :  0 ... +10 V

        return value * 10 / 400

    def nidaq_check_limit(self, value) -> float:
        ''' nidaq_check_limit '''

        value = max(value, 0)
        value = min(value, 400)

        return value

    def nidaq_go(self) -> None:
        ''' nidaq_go '''

        self.nidaq_position = float(self.nidaq_tf.get())
        self.nidaq_position = self.nidaq_check_limit(self.nidaq_position)

        analog_out_value = self.value_to_analog_out_value(self.nidaq_position)

        self.nidaq.set_position(analog_out_value)
        self.nidaq_lb.configure(text=f"{self.nidaq_position:.2f}")
        self.nidaq_sldr.set(self.nidaq_position)

    def nidaq_center(self) -> None:
        ''' nidaq_center '''

        self.nidaq_position = 200
        self.nidaq_position = self.nidaq_check_limit(self.nidaq_position)

        analog_out_value = self.value_to_analog_out_value(self.nidaq_position)

        self.nidaq.set_position(analog_out_value)
        self.nidaq_lb.configure(text=f"{self.nidaq_position:.2f}")
        self.nidaq_sldr.set(self.nidaq_position)

    def nidaq_on_mouse_down(self, event):
        ''' on_mouse_down '''

        self.nidaq_position = self.nidaq_sldr.get()
        self.nidaq_update_stage_position_label()

    def nidaq_on_slider_move(self, event):
        ''' on_slider_move '''

        self.nidaq_position = self.nidaq_sldr.get()
        self.nidaq_update_stage_position_label()

    def nidaq_on_mouse_up(self, event):
        ''' nidaq slider mouse up event '''

        self.nidaq_position = self.nidaq_sldr.get()
        self.nidaq_update_stage_position_label()

        value = self.nidaq_check_limit(self.nidaq_position)
        analog_out_value = self.value_to_analog_out_value(value)

        self.nidaq.set_position(analog_out_value)
        self.nidaq_update_stage_position_label()
        self.nidaq_sldr.set(value)

    def nidaq_init(self):
        ''' nidaq_init '''

        self.nidaq_position = self.nidaq_check_limit(self.nidaq_position)

        analog_out_value = self.value_to_analog_out_value(self.nidaq_position)

        self.nidaq.set_position(analog_out_value)
        self.nidaq_lb.configure(text=f"{self.nidaq_position:.2f}")
        self.nidaq_sldr.set(float(self.nidaq_position))

    def nidaq_step(self, value: float):
        ''' nidaq_step '''

        self.nidaq_position = float(self.nidaq_position) + value
        self.nidaq_position = self.nidaq_check_limit(value=self.nidaq_position)

        analog_out_value = self.value_to_analog_out_value(self.nidaq_position)

        self.nidaq.set_position(analog_out_value)
        self.nidaq_lb.configure(text=f"{self.nidaq_position:.2f}")
        self.nidaq_sldr.set(self.nidaq_position)

    def nidaq_move_up_50(self) -> None:
        ''' nidaq_move_up_50 '''

        self.nidaq_step(50)

    def nidaq_move_up_10(self) -> None:
        ''' nidaq_move_up_10 '''

        self.nidaq_step(10)

    def nidaq_move_up_1(self) -> None:
        ''' nidaq_move_up_1 '''

        self.nidaq_step(1)

    def nidaq_move_down_1(self) -> None:
        ''' nidaq_move_down_1 '''

        self.nidaq_step(-1)

    def nidaq_move_down_10(self) -> None:
        ''' nidaq_move_down_10 '''

        self.nidaq_step(-10)

    def nidaq_move_down_50(self) -> None:
        ''' nidaq_move_down_50 '''

        self.nidaq_step(-50)

    def nidaq_update_stage_from_entry_field(self) -> None:
        ''' nidaq_update_stage_from_entry_field '''

        self.nidaq.set_position(float(self.STAGE_entry_field.get()))
        self.nidaq_update_stage_position_label()

    def nidaq_update_stage_position_label(self) -> None:
        ''' nidaq_update_stage_position_label '''

        self.nidaq_lb.configure(text=f"{self.nidaq_position:.2f}")
        self.nidaq_sldr.set(self.nidaq_position)

# endregion

# #region kcube related commands

    def kcube_enable(self) -> None:
        ''' kcube_enable '''

        if self.kcube.stage_enabled is True:
            self.kcube.enable()
            self.kcube.stage_enabled = False
            self.kcube_bt_enable.configure(fg_color='red', text='disabled')

        else:
            self.kcube.enable()
            self.kcube.stage_enabled = True
            self.kcube_bt_enable.configure(fg_color='green', text='enabled')

    def kcube_home(self) -> None:
        ''' kcube_home '''

        self.kcube_bt_home.configure(fg_color='darkred', text='homing')
        self.kcube.home()
        self.kcube_bt_home.configure(fg_color='green', text='homed')
        self.kcube_position = self.kcube.get_position()
        self.kcube_lb_position.configure(text=f"{self.kcube_position:.2f}")

    def kcube_move(self, stepsize) -> None:
        ''' kcube_move '''

        self.kcube_position = float(self.kcube_position) + float(stepsize)
        self.kcube.set_position(float(self.kcube_position))
        self.kcube_lb_position.configure(text=f"{self.kcube_position:.2f}")
        self.kcube_sldr.set(self.kcube_position)

    def kcube_move_up_100(self) -> None:
        ''' nidaq_move_up_100 '''

        self.kcube_move(0.1)

    def kcube_move_up_50(self) -> None:
        ''' kcube_move_up_50 '''

        self.kcube_move(0.05)

    def kcube_move_up_10(self) -> None:
        ''' kcube_move_up_10 '''

        self.kcube_move(0.01)

    def kcube_move_down_10(self) -> None:
        ''' kcube_move_down_10 '''

        self.kcube_move(-0.01)

    def kcube_move_down_50(self) -> None:
        ''' kcube_move_down_50 '''

        self.kcube_move(-0.05)

    def kcube_move_down_100(self) -> None:
        ''' kcube_move_down_100 '''

        self.kcube_move(-0.1)

    def kcube_velocity_parameter(self, selected_value) -> None:
        ''' kcube_velocity_parameter '''

        self.kcube.set_velocity_params(velocity_key=selected_value)

    def kcube_on_mouse_down(self, event) -> None:
        ''' on_mouse_down '''

        self.kcube_position = self.kcube_sldr.get()
        #self.nidaq_update_stage_position_label()

    def kcube_on_slider_move(self, event) -> None:
        ''' on_slider_move '''

        self.nidaq_position = self.kcube_sldr.get()

    def kcube_on_mouse_up(self, event) -> None:
        ''' kcube slider mouse up event '''

        self.kcube.set_position(self.kcube_position)
        self.kcube_lb_position.configure(text=f"{self.kcube_position:.2f}")

    def kcube_go(self) -> None:
        ''' kcube_go '''

        self.kcube_position = float(self.kcube_tf_position.get())
        self.kcube.set_position(self.kcube_position)
        self.kcube_lb_position.configure(text=f"{self.kcube_position:.2f}")
        self.kcube_sldr.set(self.kcube_position)

    def kcube_objective(self, selected_value) -> None:
        ''' kcube_objective '''

        self.kcube_position = FILEIO.read_value(self.config_path, selected_value)
        self.kcube_lb_position.configure(text=float(self.kcube_position))
        self.kcube.set_position(float(self.kcube_position))
        self.kcube_sldr.set(float(self.kcube_position))
        self.kcube_tf_position.configure(placeholder_text="{self.kcube_position:.2f}")

# endregion

# region gui related defs

    def set_appearance_mode(self) -> None:
        ''' set_appearance_mode '''

        if self.appearance_mode == "light":
            ctk.set_appearance_mode("dark")
            self.appearance_mode = "dark"

        elif self.appearance_mode == "dark":
            ctk.set_appearance_mode("light")
            self.appearance_mode = "light"

    def exit(self) -> None:
        ''' exit'''

        if self.using_nidaq is True:

            FILEIO.write_value(self.config_path, 'nidaq_position', round(float(self.nidaq_position), 2))
            self.nidaq.close()

        if self.using_kcube is True:

            objective = self.kcube_cb_objective.get()
            FILEIO.write_value(self.config_path, 'last_selected', objective)
            FILEIO.write_value(self.config_path, objective, round(float(self.kcube_position), 2))

            self.kcube.disconnect()

        self.quit()

# endregion


app = App()
app.mainloop()
