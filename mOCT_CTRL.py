"""
moct_ctrl.py

Created on Feb 20, 2025 by Martin Ahrens
m.ahrens@uni-luebeck.de

Modified on April 29, 2026 by Martin Ahrens

"""

import os
import time
from pathlib import Path
import tkinter as tk
import customtkinter as ctk
import numpy as np

from scipy.interpolate import interp1d
from PIL import Image

from driver.kinesis import KcubeHandle
from driver.nidaq import NidaqHandle
from driver.nkt import NktHandle

from utils.fileIO import FILEIO
from utils.pluginmanager import PluginManager
from utils.check_config import CheckConfig
from utils.version import __version__


class App(ctk.CTk):
    """
    Main app

    """
    def __init__(self) -> None:
        """__init__"""

        super().__init__()

        self.config_path = Path(__file__).resolve().parent / "resources" / "config.txt"

        self.using_kcube = CheckConfig.load_variables(self.config_path, 'using_kcube')
        self.using_nidaq = CheckConfig.load_variables(self.config_path, 'using_nidaq')
        self.using_nkt = CheckConfig.load_variables(self.config_path, 'using_nkt')

        self.checkbutton_checkmark = tk.BooleanVar(value=False)
        self.plugin_manager = PluginManager(self.config_path)

        self.kcube_position = float(0.0)
        self.nidaq_position = float(0.0)

        self.nkt_emission_state = False
        self.nkt_interlock_state = False

        self.sync_kinesis_mipos = False
        self.hysteresis_compensation = False

        # ---------------------------------------------------------------------

        self.title("mOCT CTRL / " + __version__)

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.appearance_mode = "light"

        if self.using_nidaq is True:
            self.set_nidaq_ui_parts()

        if self.using_kcube is True:
            self.set_kinesis_ui_parts()

        if self.using_nkt is True:
            self.set_nkt_ui_parts()

        self.set_sync_ui_parts()
        self.f4 = ctk.CTkFrame(self, fg_color="transparent")
        self.f4.grid(row=2, column=1, padx=(5, 5), pady=(0, 5), sticky="sw")

        self.f41 = ctk.CTkFrame(self.f4, fg_color="transparent")
        self.f41.grid(row=0, column=0, padx=(5, 5), pady=(0, 0))

        self.f4_switch = ctk.CTkSwitch(self.f41, text="Dark/Light",
                                       command=self.set_appearance_mode,
                                       onvalue="dark",
                                       offvalue="light")
        self.f4_switch.grid(row=0, column=0, padx=(5, 20), pady=(5, 5))

        self.f4_bt_2 = ctk.CTkButton(self.f41, width=75, height=20, text="Exit", command=self.exit)
        self.f4_bt_2.grid(row=0, column=1, padx=(20, 5), pady=(5, 5))

# region SYNC related comnmands

    def sync_move(self, kcube_value: float, nidaq_value: float) -> None:
        """
        Run togeather
        """

        self.kcube_move_rel(kcube_value * float(self.syncfactor_tf.get()))

        step = nidaq_value
        if self.hysteresis_compensation:
            step = self.calc_hysteresis_compensation(step, False)

        val = self.refractive_index_compensation(step)
        self.nidaq_step(val)

    def init_hysteresis_compensation(self) -> None:
        """
        Init hysteresis compensation
        """

        self.nidaq_step(0.0)
        compensated_value = self.calc_hysteresis_compensation(200, True)
        self.nidaq_step(compensated_value)

    def calc_hysteresis_compensation(self, value, direction) -> float:
        """
        Calculate the hysteresis compensation of the MIPOS stage

        Args:
            value (float): Position value µm
            direction (bool): Direction of movement

        Returns:
            Calculated corrected value in volt
        """

        x        = np.array([0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0])
        y_corr_p = np.array([0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0])
        y_corr_n = np.array([0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0])

        if direction is True:
            y_corr = y_corr_p
        else:
            y_corr = y_corr_n

        f = interp1d(x, y_corr, kind='cubic', fill_value='extrapolate')
        y_new = float(f(value))

        return y_new

    def refractive_index_compensation(self, val_n1) -> float:
        """
        Refractive index compensation. KCube stage runs in air -> n = 1.00
        Mipos stage guides the microscopic objectiv lens through water -> n = 1.33

        Args:
            val_n1 (float): Stepsize with n = 1.00

        Returns:
            val_n2 (float): Stepsize with in UI given n (e.g. 1.33)
        """

        val_n2 = val_n1 * 1.00 / float(self.refractiveindex_tf.get())

        return val_n2

    def synchronize_kinesis_mipos(self) -> None:
        """
        Sync the KINESIS stage with the MIPOS stage including of the compensation
        of the refractive index (opitcal pathlength) and hysteresis compensation
        (of the MIPOS stage)
        """

        if self.sync_kinesis_mipos is True:
            self.sync_kinesis_mipos = False
            self.unhide_elements()
        else:
            self.sync_kinesis_mipos = True
            self.hide_elements()

    def set_tree_state(self, widget, state) -> None:
        """
        Set UI element states
        """

        for child in widget.winfo_children():
            try:
                child.configure(state=state)
            except Exception:
                pass

            self.set_tree_state(child, state)

    def hide_elements(self) -> None:
        """
        Hide KINESIS and MIPOS related elements
        """

        for frame in (self.kcube_f0, self.nidaq_f0):
            self.set_tree_state(frame, "disabled")

        self.hyst_switch_bt.configure(state="normal")
        self.refractiveindex_tf.configure(state="normal")
        self.move_bt_p1.configure(state="normal")
        self.move_bt_m1.configure(state="normal")
        self.move_bt_p10.configure(state="normal")
        self.move_bt_m10.configure(state="normal")

    def unhide_elements(self) -> None:
        """
        Unhide KINESIS and MIPOS related elements
        """

        for frame in (self.kcube_f0, self.nidaq_f0):
            self.set_tree_state(frame, "normal")

        self.hyst_switch_bt.configure(state="disabled")
        self.refractiveindex_tf.configure(state="disabled")
        self.move_bt_p1.configure(state="disabled")
        self.move_bt_m1.configure(state="disabled")
        self.move_bt_p10.configure(state="disabled")
        self.move_bt_m10.configure(state="disabled")

# endregion

# region MIPOS related commands

    def nidaq_init_position(self) -> None:
        """
        NI-DAQ go to initial position
        """

        self.nidaq_position = self._nidaq_check_limit(self.nidaq_position)

        analog_out_value = self._value_to_analog_out_value(self.nidaq_position)

        self.nidaq.set_position(analog_out_value)

        self.nidaq_lb.configure(text=f"{self.nidaq_position:.2f}")
        self.nidaq_sldr.set(float(self.nidaq_position))

    def nidaq_center(self) -> None:
        """
        NI-DAQ go to center position
        """

        self.nidaq_position = 200
        self.nidaq_position = self._nidaq_check_limit(self.nidaq_position)

        analog_out_value = self._value_to_analog_out_value(self.nidaq_position)

        self.nidaq.set_position(analog_out_value)
        self.nidaq_lb.configure(text=f"{self.nidaq_position:.2f}")
        self.nidaq_sldr.set(self.nidaq_position)

    def nidaq_go(self) -> None:
        """
        NI-DAQ go to a specific position
        """

        self.nidaq_position = float(self.nidaq_tf.get())
        self.nidaq_position = self._nidaq_check_limit(self.nidaq_position)

        analog_out_value = self._value_to_analog_out_value(self.nidaq_position)

        self.nidaq.set_position(analog_out_value)
        self.nidaq_lb.configure(text=f"{self.nidaq_position:.2f}")
        self.nidaq_sldr.set(self.nidaq_position)

    def nidaq_step(self, step_in_um: float) -> None:
        """
        NI-DAQ go a specific step

        Args:
            step_in_um (float): Position in µm

        Returns:
            nidaq_position (float): Position in µm

        """

        self.nidaq_position = float(self.nidaq_position) + step_in_um
        self.nidaq_position = self._nidaq_check_limit(value=self.nidaq_position)

        analog_out_value = self._value_to_analog_out_value(self.nidaq_position)

        self.nidaq.set_position(analog_out_value)
        self.nidaq_lb.configure(text=f"{self.nidaq_position:.2f}")
        self.nidaq_sldr.set(self.nidaq_position)

    def nidaq_on_slider_move(self, event) -> None:
        """
        NI-DAQ on slider move

        Args:
            event (event): GUI event
        """

        self.nidaq_position = self.nidaq_sldr.get()
        self.nidaq_update_stage_position_label()

    def nidaq_on_mouse_released(self, event) -> None:
        """
        NI-DAQ slider changes position with the mouse

        Args:
            event (event): GUI event
        """

        self.nidaq_position = self.nidaq_sldr.get()
        self.nidaq_update_stage_position_label()

        value = self._nidaq_check_limit(self.nidaq_position)
        analog_out_value = self._value_to_analog_out_value(value)
        self.nidaq.set_position(analog_out_value)

        self.nidaq_update_stage_position_label()
        self.nidaq_sldr.set(value)

    def nidaq_move(self, value) -> None:
        """
        NI-DAQ move +/- x µm
        Triggert by the six buttons
        """

        self.nidaq_step(value)

    def nidaq_update_stage_position_label(self) -> None:
        """
         NI-DAQ update stage from position label
        """

        self.nidaq_lb.configure(text=f"{self.nidaq_position:.2f}")
        self.nidaq_sldr.set(self.nidaq_position)

    def _value_to_analog_out_value(self, position_um: float) -> float:
        """
        Calculates the corret voltage from the position in µm

        Range of the Stage:  0 ... 400 µm
        Range of the DAQ  :  0 ... +10 V

        Args:
            position_um (float): Position in µm

        Return:
            position_volt (float) : Position in volt

        """

        position_volt = position_um * 10 / 400

        return position_volt

    def _nidaq_check_limit(self, value) -> float:
        """
        Checks the min and max limit of the postion in µm
        """

        value = max(value, 0)
        value = min(value, 400)

        return value

# endregion

# region KCUBE related commands

    def kcube_enable(self) -> None:
        """
        KCube enable
        """

        if self.kcube.stage_enabled is True:
            self.kcube.enable()
            self.kcube.stage_enabled = False
            self.kcube_bt_enable.configure(fg_color='red', text='disabled')

        else:
            self.kcube.enable()
            self.kcube.stage_enabled = True
            self.kcube_bt_enable.configure(fg_color='green', text='enabled')

    def kcube_home(self) -> None:
        """
        KCube home
        """

        self.kcube_bt_home.configure(fg_color='darkred', text='homing')
        self.kcube.home()
        self.kcube_bt_home.configure(fg_color='green', text='homed')
        self.kcube_position = float(self.kcube.get_position())
        self.kcube_lb_position.configure(text=f"{self.kcube_position:.2f}")

    def kcube_move_abs(self) -> None:
        """
        KCube move to a specific position, gets the position from a textfield
        """

        self.kcube_position = float(self.kcube_tf_position.get())
        self.kcube_position = self._kcube_check_limit(self.kcube_position)
        self.kcube.set_position(float(self.kcube_position))
        self.kcube_lb_position.configure(text=f"{self.kcube_position:.2f}")
        self.kcube_sldr.set(self.kcube_position)

    def kcube_move_rel(self, stepsize) -> None:
        """
        KCube move a given stepsize, gets the stepsize from the stepsize-buttons

        Args:
            stepsize
        """

        self.kcube_position = float(self.kcube_position) + float(stepsize)
        self.kcube_position = self._kcube_check_limit(self.kcube_position)
        self.kcube.set_position(float(self.kcube_position))
        self.kcube_lb_position.configure(text=f"{self.kcube_position:.2f}")
        self.kcube_sldr.set(self.kcube_position)

    def kcube_velocity_parameter(self, selected_value) -> None:
        """kcube_velocity_parameter"""

        self.kcube.set_velocity_params(velocity_key=selected_value)

    def kcube_on_mouse_down(self, event) -> None:
        """on_mouse_down"""

        self.kcube_position = self.kcube_sldr.get()

    def kcube_on_slider_move(self, event) -> None:
        """on_slider_move"""

        self.nidaq_position = self.kcube_sldr.get()
        self.kcube_lb_position.configure(text=f"{self.kcube_position:.2f}")

    def kcube_on_mouse_up(self, event) -> None:
        """kcube slider mouse up event"""

        self.kcube_position = self.kcube_sldr.get()
        self.kcube.set_position(float(self.kcube_position))
        self.kcube_lb_position.configure(text=f"{self.kcube_position:.2f}")

    def kcube_objective(self, selected_value) -> None:
        """kcube_objective"""

        self.kcube_position = FILEIO.read_value(self.config_path, selected_value)
        self.kcube_lb_position.configure(text=float(self.kcube_position))
        self.kcube.set_position(float(self.kcube_position))
        self.kcube_sldr.set(float(self.kcube_position))
        self.kcube_tf_position.configure(placeholder_text="{self.kcube_position:.2f}")

    def _kcube_check_limit(self, position: float) -> float:
        """
        KCube check upper and lower limit
        If the position is lower as the limit, set it to 0 (min value)
        If the position is heighter as the limit, set it to 400 (max value)

        Args:
            position (float):
        """

        position = max(position, 0)
        position = min(position, 100)

        return position

# endregion

# region NKT related commands

    def nkt_on_mouse_down(self, event) -> None:
        """nkt_on_mouse_down"""

        val = self.nkt_sldr.get()
        self.nkt_tf_power.configure(text=f"{val:.2f}")

    def nkt_on_mouse_up(self, event) -> None:
        """nkt_on_mouse_up"""

        val = self.nkt_sldr.get()
        self.nkt.set_power(val)
        self.nkt_tf_power.configure(text=f"{val:.2f}")
        time.sleep(0.1)
        print(self.nkt.get_power())

    def nkt_on_slider_move(self, event) -> None:
        """nkt_on_slider_move"""

        val = self.nkt_sldr.get()
        self.nkt_tf_power.configure(text=f"{val:.2f}")

    def nkt_interlock(self) -> None:
        """nkt reset interlock"""

        self.nkt.reset_interlock(self)
        self.nkt_interlock_state = True
        self.nkt_bt_power.configure(fg_color='green')

    def nkt_laser(self) -> None:
        """nkt laser on/off"""

        print('State is ' + str(self.nkt_emission_state))

        if self.nkt_interlock_state is False:

            # Popup window that tells the user to reset the interlock
            popup = ctk.CTkToplevel()
            popup.title("Information")
            popup.geometry("200x100")
            popup.attributes("-topmost", True)

            info_label = ctk.CTkLabel(popup, text="Please reset the interlock",  font=("Arial", 14))
            info_label.pack(pady=10)

            # Create a button to close the popup
            close_button = ctk.CTkButton(popup, text="Close", command=popup.destroy)
            close_button.pack()

        else:

            if self.nkt_emission_state is False:
                self.nkt.set_emission(True)
                self.nkt.set_power(100)
                self.nkt_emission_state = True
                self.nkt_bt_laser.configure(fg_color='red')
                print("Set emission on")

            else:
                self.nkt.set_emission(False)
                self.nkt_emission_state = False
                self.nkt_bt_laser.configure(fg_color='#3a7ebf')
                print("Set emission off")

# endregion

# region GUI related defs

    def set_nidaq_ui_parts(self) -> None:
        """
        Set up NI-DAQ related ui parts
        """

        nidaq_device = FILEIO.read_value(self.config_path, 'nidaq_device')
        nidaq_ao_port = FILEIO.read_value(self.config_path, 'nidaq_ao_port')
        nidaq_ai_port = FILEIO.read_value(self.config_path, 'nidaq_ai_port')
        nidaq_min_out = FILEIO.read_value(self.config_path, 'nidaq_min_out')
        nidaq_max_out = FILEIO.read_value(self.config_path, 'nidaq_max_out')

        self.nidaq = NidaqHandle(nidaq_device, nidaq_ao_port, nidaq_ai_port, float(nidaq_min_out), float(nidaq_max_out))

        self.nidaq_position = float(FILEIO.read_value(self.config_path, 'nidaq_position'))

        self.nidaq_f0 = ctk.CTkFrame(self, fg_color="transparent")
        self.nidaq_f0.grid(row=0, column=0, padx=(5, 2.5), pady=(5, 5), sticky="nw")

        self.nidaq_f01 = ctk.CTkFrame(self.nidaq_f0, fg_color="transparent")
        self.nidaq_f01.grid(row=0, column=0, padx=(5, 2.5), pady=(5, 5), sticky="nw")

        self.nidaq_lb = ctk.CTkLabel(self.nidaq_f01, width=75, height=20, font=("Cosmic Sans MS", 18, "normal"), text="MIPOS")
        self.nidaq_lb.grid(row=0, column=0, padx=(5, 5), pady=(5, 5))

        img = self.load_image("focus.png")
        ctk_image = ctk.CTkImage(light_image=img, dark_image=img, size=(40, 40))

        self.label = ctk.CTkLabel(self.nidaq_f01, image=ctk_image, text="")
        self.label.grid(row=0, column=1, padx=(0, 0), pady=(0, 0))

        self.nidaq_f1 = ctk.CTkFrame(self.nidaq_f0, border_width=1, fg_color="transparent")
        self.nidaq_f1.grid(row=1, column=0, padx=(5, 5), pady=(5, 5))

        self.nidaq_f2 = ctk.CTkFrame(self.nidaq_f1, fg_color="transparent")
        self.nidaq_f2.grid(row=3, column=0, padx=(5, 5), pady=(15, 15))

        self.nidaq_bt_p50 = ctk.CTkButton(self.nidaq_f2, width=75, height=20, text="+50", command=lambda: self.nidaq_move(50))
        self.nidaq_bt_p50.grid(row=0, column=0, padx=(5, 5), pady=(5, 5))

        self.nidaq_bt_p10 = ctk.CTkButton(self.nidaq_f2, width=75, height=20, text="+10", command=lambda: self.nidaq_move(10))
        self.nidaq_bt_p10.grid(row=1, column=0, padx=(5, 5), pady=(5, 5))

        self.nidaq_bt_p1 = ctk.CTkButton(self.nidaq_f2, width=75, height=20, text="+ 1", command=lambda: self.nidaq_move(1))
        self.nidaq_bt_p1.grid(row=2, column=0, padx=(5, 5), pady=(5, 5))

        self.nidaq_sldr = ctk.CTkSlider(self.nidaq_f2, orientation=ctk.VERTICAL, height=120, from_=0, to=400)
        self.nidaq_sldr.grid(row=4, column=0, padx=(5, 5), pady=(0, 0))
        self.nidaq_sldr.bind("<ButtonPress-1>", self.nidaq_on_mouse_released)
        self.nidaq_sldr.bind("<ButtonRelease-1>", self.nidaq_on_mouse_released)
        self.nidaq_sldr.bind("<B1-Motion>", self.nidaq_on_slider_move)

        self.nidaq_bt_m1 = ctk.CTkButton(self.nidaq_f2, width=75, height=20, text="- 1", command=lambda: self.nidaq_move(-1))
        self.nidaq_bt_m1.grid(row=5, column=0, padx=(5, 5), pady=(5, 5))

        self.nidaq_bt_m10 = ctk.CTkButton(self.nidaq_f2, width=75, height=20, text="-10", command=lambda: self.nidaq_move(-10))
        self.nidaq_bt_m10.grid(row=6, column=0, padx=(5, 5), pady=(5, 5))

        self.nidaq_bt_m50 = ctk.CTkButton(self.nidaq_f2, width=75, height=20, text="-50", command=lambda: self.nidaq_move(-50))
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

        self.nidaq_init_position()

    def set_kinesis_ui_parts(self) -> None:
        """
        Set up KINESIS related ui parts
        """

        kcube_serial_number = FILEIO.read_value(self.config_path, 'kcube_serial_number')
        self.kcube_sn_info = "SN: " + kcube_serial_number
        self.kcube = KcubeHandle(str(int(kcube_serial_number)))
        self.last_selected = FILEIO.read_value(self.config_path, 'last_selected')
        self.kcube.stage_enabled = True

        self.kcube_f0 = ctk.CTkFrame(self, fg_color="transparent")
        self.kcube_f0.grid(row=0, column=1, padx=(2.5, 5), pady=(5, 5), sticky="nw")

        self.kcube_f01 = ctk.CTkFrame(self.kcube_f0, fg_color="transparent")
        self.kcube_f01.grid(row=0, column=0, padx=(5, 2.5), pady=(5, 5), sticky="nw")

        self.kcube_lb = ctk.CTkLabel(self.kcube_f01, width=75, height=20, font=("Cosmic Sans MS", 18, "normal"), text="KINESIS")
        self.kcube_lb.grid(row=0, column=0, padx=(5, 5), pady=(5, 5))

        img = self.load_image("zref.png")
        ctk_image = ctk.CTkImage(light_image=img, dark_image=img, size=(40, 40))

        self.label = ctk.CTkLabel(self.kcube_f01, image=ctk_image, text="")
        self.label.grid(row=0, column=1, padx=(0, 40), pady=(0, 0))

        self.kcube_f1 = ctk.CTkFrame(self.kcube_f0, border_width=1, fg_color="transparent")
        self.kcube_f1.grid(row=1, column=0, padx=(5, 5), pady=(5, 5), sticky="nw")

        self.kcube_f2 = ctk.CTkFrame(self.kcube_f1, fg_color="transparent")
        self.kcube_f2.grid(row=0, column=0, padx=(5, 5), pady=(10, 10))

        self.kcube_f3 = ctk.CTkFrame(self.kcube_f2, fg_color="transparent")
        self.kcube_f3.grid(row=1, column=0, padx=(5, 5), pady=(0, 0))

        self.kcube_bt_p100 = ctk.CTkButton(self.kcube_f3, width=75, height=20, text="+100 µm", command=lambda: self.kcube_move_rel(0.1))
        self.kcube_bt_p100.grid(row=0, column=0, padx=(5, 5), pady=(5, 5))

        self.kcube_bt_p50 = ctk.CTkButton(self.kcube_f3, width=75, height=20, text="+50 µm", command=lambda: self.kcube_move_rel(0.05))
        self.kcube_bt_p50.grid(row=1, column=0, padx=(5, 5), pady=(5, 5))

        self.kcube_bt_p10 = ctk.CTkButton(self.kcube_f3, width=75, height=20, text="+10 µm", command=lambda: self.kcube_move_rel(0.01))
        self.kcube_bt_p10.grid(row=2, column=0, padx=(5, 5), pady=(5, 5))

        self.kcube_sldr = ctk.CTkSlider(self.kcube_f3, orientation=ctk.VERTICAL, height=120, from_=0, to=100)
        self.kcube_sldr.grid(row=3, column=0, padx=(5, 5), pady=(0, 0))
        self.kcube_sldr.bind("<ButtonPress-1>", self.kcube_on_mouse_down)
        self.kcube_sldr.bind("<ButtonRelease-1>", self.kcube_on_mouse_up)
        self.kcube_sldr.bind("<B1-Motion>", self.kcube_on_slider_move)

        self.kcube_bt_m10 = ctk.CTkButton(self.kcube_f3, width=75, height=20, text="-10 µm", command=lambda: self.kcube_move_rel(-0.01))
        self.kcube_bt_m10.grid(row=4, column=0, padx=(5, 5), pady=(5, 5))

        self.kcube_bt_m50 = ctk.CTkButton(self.kcube_f3, width=75, height=20, text="-50 µm", command=lambda: self.kcube_move_rel(-0.05))
        self.kcube_bt_m50.grid(row=5, column=0, padx=(5, 5), pady=(5, 5))

        self.kcube_bt_m100 = ctk.CTkButton(self.kcube_f3, width=75, height=20, text="-100 µm", command=lambda: self.kcube_move_rel(-0.1))
        self.kcube_bt_m100.grid(row=7, column=0, padx=(5, 5), pady=(5, 5))

        self.kcube_f4 = ctk.CTkFrame(self.kcube_f2, fg_color="transparent")
        self.kcube_f4.grid(row=1, column=1, padx=(5, 5), pady=(0, 0))

        self.kcube_lb_position = ctk.CTkLabel(self.kcube_f4, width=75, height=20, text="")
        self.kcube_lb_position.grid(row=0, column=0, padx=(5, 5), pady=(5, 5))

        self.kcube_tf_position = ctk.CTkEntry(self.kcube_f4, width=75, height=20, justify="center", placeholder_text="pos / mm")
        self.kcube_tf_position.grid(row=1, column=0, padx=(5, 5), pady=(5, 5))
        self.kcube_tf_position.insert(0, "0")

        self.kcube_bt_go = ctk.CTkButton(self.kcube_f4, width=75, height=20, text="Go", command=self.kcube_move_abs)
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

        self.kcube_lb_vers = ctk.CTkLabel(self.kcube_f5, width=75, height=20, font=("Cosmic Sans MS", 10, "normal"), text=self.kcube_sn_info)
        self.kcube_lb_vers.grid(row=4, column=0, padx=(5, 5), pady=(70, 5))

        self.kcube_cb_objective.set(self.last_selected)
        self.kcube_position = FILEIO.read_value(self.config_path, self.last_selected)

        self.kcube_bt_enable.configure(fg_color='green', text='enabled')
        self.kcube_lb_position.configure(text=str(self.kcube_position))
        self.kcube_sldr.set(float(self.kcube_position))

    def set_nkt_ui_parts(self) -> None:
        """
        Set up NKT related ui parts
        """

        nkt_device = FILEIO.read_value(self.config_path, 'nkt_device')
        self.nkt = NktHandle(nkt_device)

        self.nkt_f0 = ctk.CTkFrame(self, fg_color="transparent")
        self.nkt_f0.grid(row=0, column=2, padx=(2.5, 5), pady=(5, 5), sticky="nw")

        self.nkt_f01 = ctk.CTkFrame(self.nkt_f0, fg_color="transparent")
        self.nkt_f01.grid(row=0, column=0, padx=(5, 2.5), pady=(5, 5), sticky="nw")

        self.nkt_lb = ctk.CTkLabel(self.nkt_f01, width=75, height=20, font=("Cosmic Sans MS", 18, "normal"), text="NKT")
        self.nkt_lb.grid(row=0, column=0, padx=(5, 5), pady=(5, 5))

        img = self.load_image("laser.png")
        ctk_image = ctk.CTkImage(light_image=img, dark_image=img, size=(40, 40))

        self.label = ctk.CTkLabel(self.nkt_f01, image=ctk_image, text="")
        self.label.grid(row=0, column=1, padx=(0, 0), pady=(0, 0))

        self.nkt_f1 = ctk.CTkFrame(self.nkt_f0, border_width=1, fg_color="transparent")
        self.nkt_f1.grid(row=1, column=0, padx=(5, 5), pady=(5, 5), sticky="nw")

        self.nkt_bt_power = ctk.CTkButton(self.nkt_f1, width=75, height=20, text="Interlock", command=self.nkt_interlock)
        self.nkt_bt_power.grid(row=0, column=0, padx=(5, 5), pady=(20, 5))

        self.nkt_bt_laser = ctk.CTkButton(self.nkt_f1, width=75, height=20, text="On/Off", command=self.nkt_laser)
        self.nkt_bt_laser.grid(row=1, column=0, padx=(5, 5), pady=(5, 20))

        self.nkt_sldr = ctk.CTkSlider(self.nkt_f1, orientation=ctk.HORIZONTAL, width=80, from_=25, to=100)
        self.nkt_sldr.set(100)
        self.nkt_sldr.grid(row=2, column=0, padx=(5, 5), pady=(0, 0))
        self.nkt_sldr.bind("<ButtonPress-1>", self.nkt_on_mouse_down)
        self.nkt_sldr.bind("<ButtonRelease-1>", self.nkt_on_mouse_up)
        self.nkt_sldr.bind("<B1-Motion>", self.nkt_on_slider_move)

        self.nkt_tf_power = ctk.CTkLabel(self.nkt_f1, width=75, height=20, text="0")
        self.nkt_tf_power.configure(text='100')
        self.nkt_tf_power.grid(row=3, column=0, padx=(5, 40), pady=(5, 5))

    def load_image(self, name):
        """
        Load image from path

        Args:
            name (str) : filename.type (jpg, png)

        Returns:
            image (PIL.image) : The pillow image

        """
        with open(Path(__file__).resolve().parent / "resources" / name, "rb") as f:
            image = Image.open(f)
            image.load()
            return image

    def set_sync_ui_parts(self) -> None:
        """
        Set up stage synchronization related ui parts
        """

        self.f3 = ctk.CTkFrame(self, border_width=1, fg_color="transparent")
        self.f3.grid(row=1, column=0, padx=(5, 5), pady=(0, 25), sticky="nw")

        self.sync_switch_bt = ctk.CTkSwitch(self.f3, text="Sync MIPOS & KINESIS", command=self.synchronize_kinesis_mipos)
        self.sync_switch_bt.grid(row=0, column=0, padx=(5, 20), pady=(5, 5), sticky="nw")

        self.hyst_switch_bt = ctk.CTkSwitch(self.f3, text="Hystersis compensation", command=self.init_hysteresis_compensation)
        self.hyst_switch_bt.grid(row=1, column=0, padx=(5, 20), pady=(5, 5), sticky="nw")
        self.hyst_switch_bt.configure(state="disabled")

        self.refindex_lb = ctk.CTkLabel(self.f3, width=50, height=20, text="Refractive Index")
        self.refindex_lb.grid(row=2, column=0, padx=(5, 5), pady=(5, 5))

        self.refractiveindex_tf = ctk.CTkEntry(self.f3, width=50, height=20, justify="center")
        self.refractiveindex_tf.grid(row=2, column=1, padx=(5, 5), pady=(5, 5))
        self.refractiveindex_tf.insert(0, "1.33")
        self.refractiveindex_tf.configure(state="disabled")

        self.move_bt_p1 = ctk.CTkButton(self.f3, width=75, height=20, text="+1 µm", command=lambda: self.sync_move(-0.001, -1))
        self.move_bt_p1.grid(row=3, column=0, padx=(5, 5), pady=(5, 5))
        self.move_bt_p1.configure(state="disabled")

        self.move_bt_m1 = ctk.CTkButton(self.f3, width=75, height=20, text="-1 µm", command=lambda: self.sync_move(0.001, 1))
        self.move_bt_m1.grid(row=3, column=1, padx=(5, 5), pady=(5, 5))
        self.move_bt_m1.configure(state="disabled")

        self.move_bt_p10 = ctk.CTkButton(self.f3, width=75, height=20, text="+10 µm", command=lambda: self.sync_move(-0.01, -10))
        self.move_bt_p10.grid(row=4, column=0, padx=(5, 5), pady=(5, 5))
        self.move_bt_p10.configure(state="disabled")

        self.move_bt_m10 = ctk.CTkButton(self.f3, width=75, height=20, text="-10 µm", command=lambda: self.sync_move(0.01, 10))
        self.move_bt_m10.grid(row=4, column=1, padx=(5, 5), pady=(5, 5))
        self.move_bt_m10.configure(state="disabled")

        self.syncfactor_lb = ctk.CTkLabel(self.f3, width=50, height=20, text="Syncfaktor")
        self.syncfactor_lb.grid(row=5, column=0, padx=(5, 5), pady=(5, 5))

        self.syncfactor_tf = ctk.CTkEntry(self.f3, width=50, height=20, justify="center")
        self.syncfactor_tf.grid(row=5, column=1, padx=(5, 5), pady=(5, 5))
        self.syncfactor_tf.insert(0, "0.11")

# endregion

    def set_appearance_mode(self) -> None:
        """
        Set the appearance mode of the app
        """

        if self.appearance_mode == "light":
            ctk.set_appearance_mode("dark")
            self.appearance_mode = "dark"

        elif self.appearance_mode == "dark":
            ctk.set_appearance_mode("light")
            self.appearance_mode = "light"

    def help(self) -> None:
        ''' help'''

        pdf_path = "README.pdf"
        os.startfile(pdf_path)

    def info(self) -> None:
        """
        App information
        """

        print(__version__)    # Create a new Toplevel window
        popup = ctk.CTkToplevel()
        popup.title("Information")
        popup.geometry("300x150")

        # Create a label to display information
        info_label = ctk.CTkLabel(popup, text="mOCT-CTRL, v" + __version__,  font=("Arial", 14))
        info_label.pack(pady=20)

        # Create a button to close the popup
        close_button = ctk.CTkButton(popup, text="Close", command=popup.destroy)
        close_button.pack()

    def exit(self) -> None:
        """
        Exit of the app
        """

        if self.using_nidaq is True:

            FILEIO.write_value(self.config_path, 'nidaq_position', round(float(self.nidaq_position), 2))
            self.nidaq.close()

        if self.using_kcube is True:

            objective = self.kcube_cb_objective.get()
            FILEIO.write_value(self.config_path, 'last_selected', objective)
            FILEIO.write_value(self.config_path, objective, round(float(self.kcube_position), 2))

            self.kcube.disconnect()

        if self.using_nkt is True:

            self.nkt.set_emission(False)
            self.nkt_emission_state = False
            self.nkt_bt_laser.configure(fg_color='#3a7ebf')
            print("Set emission off")

        self.quit()


app = App()
<<<<<<< HEAD
=======

app.iconbitmap("internal\\logo.ico")
icon = tk.PhotoImage(file="internal\\logo.png")
app.wm_iconphoto(False, icon)

menu_bar = tk.Menu(app)
file_menu = tk.Menu(menu_bar, tearoff=0)

menu_bar.add_cascade(label="File", menu=file_menu)
file_menu.add_command(label="Help", command=app.help)
file_menu.add_command(label="Info", command=app.info)
file_menu.add_command(label="Exit", command=app.exit)

option_menu = tk.Menu(menu_bar, tearoff=0)

menu_bar.add_cascade(label="Options", menu=option_menu)

option_menu.add_checkbutton(label="MIPOS", command=app.using_nidaq)
option_menu.add_checkbutton(label="KINESIS", command=app.using_kcube)
option_menu.add_checkbutton(label="NKT", command=app.using_nkt)

app.config(menu=menu_bar)

app.protocol("WM_DELETE_WINDOW", app.exit)
app.resizable(False, False)

>>>>>>> e71ed402ffb4d26d6dbceb2af0512a980dcfe1ea
app.mainloop()
