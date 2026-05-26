"""
PI Stage Control
"""

import customtkinter as ctk
from driver.nidaq import NidaqHandle
from driver.pi_gcs_devices import PIGCSHandle as pi_gcs
from driver.pi_stage_logic import StageLogic as logic


class StageCtrl(ctk.CTk):
    """
    PI Stage Control
    """

    def __init__(self):
        super().__init__()

        self.device_status_pi_gcs = False

        self.device_status_nidaq = False
        self.ni_dev = None
        self.move_pos_rel: float = 0.0

        self.move_rel_servo: float = 0.0

        self.position_prb: float = 0.0
        self.position_ref: float = 0.0

        self.old_val_prb: float = 0.0
        self.old_val_ref: float = 0.0

        self._setup_gui()
        self._disable_controls()

    # --------------------------------------------------------------------------
    def piezo_move_rel(self, value) -> float:
        """
        Piezo class accepts only fix position -> here the method calculates the
        new absolut position
        """

        return value

    # --------------------------------------------------------------------------
    def connect(self) -> int:
        """
        Connect
        """
        pi_gcs_port = "9"

        pi_gcs.connect(pi_gcs, pi_gcs_port)
        self.device_status_pi_gcs = True

        nidaq_device = "Dev2"
        nidaq_ao_port = "ao0"
        nidaq_ai_port = "ai0"

        self.ni_dev = NidaqHandle(nidaq_device, nidaq_ao_port, nidaq_ai_port)
        self.device_status_nidaq = True

        self._enable_controls()

        self.pos_ref_lb.configure(
            text=f"PRB Position {self.ni_dev.get_position():.5f} mm"
        )
        self.pos_ref_lb.configure(text=f"REF Position {pi_gcs.get_pos(pi_gcs):.5f} µm")

    # --------------------------------------------------------------------------
    def home_ref(self) -> None:
        """
        Homeing the reference (servo) stage
        """
        pi_gcs.move_fnl(pi_gcs)

    # --------------------------------------------------------------------------
    def move_abs(self) -> int:
        """
        Move to absolute position
        """

        move_abs_servo = self.pos_entry.get()
        move_abs_piezo = logic.ni_piezo_position_to_voltage(move_abs_servo)

        if (self.old_val_prb != move_abs_piezo) and (self.toggle_move_dev.get()):

            self.position_prb = float(move_abs_piezo)

        if (self.old_val_ref != move_abs_servo) and (not self.toggle_move_dev.get()):

            self.position_ref = float(move_abs_servo)

        if self.sync_dev.get() == 0:

            # Piezo-Stage - Probe
            if self.toggle_move_dev.get() == 1:

                self.ni_dev.set_position(move_abs_piezo)

            # Servo-Stage - Reference
            if self.toggle_move_dev.get() == 0:

                pi_gcs.move_abs(pi_gcs, move_abs_servo)

        else:

            # Both, Piezo- and Servo-Stage
            self.ni_dev.set_position(move_abs_servo)
            pi_gcs.move_abs(pi_gcs, move_abs_servo)

        self.old_val_prb = move_abs_piezo
        self.old_val_ref = move_abs_servo

        # print(f'PRB Position {self.position_prb:.5f}')
        # print(f'REF Position {self.position_ref:.5f}')
        self.pos_ref_lb.configure(text=f"REF Position {self.position_ref:.2f} mm")
        self.pos_prb_lb.configure(
            text=f"PRB Position {logic.ni_piezo_volatage_to_position(self.position_prb):.2f} µm"
        )

    # --------------------------------------------------------------------------
    def move_rel(self, direction) -> int:
        """
        Move a relative distance
        """

        move_rel_servo = float(self.stepsize_entry.get())
        move_rel_servo = (
            (-1 * float(move_rel_servo)) if direction == 1 else float(move_rel_servo)
        )

        move_rel_piezo = (
            (-1 * float(move_rel_servo)) if direction == 1 else float(move_rel_servo)
        )
        move_rel_piezo = (
            self.move_pos_rel + logic.ni_piezo_position_to_voltage(move_rel_servo)
        ) * 1000

        if self.sync_dev.get() == 0:

            # Pizo-Stage - Probe
            if self.toggle_move_dev.get() == 1:

                self.position_prb = float(self.old_val_prb) + float(move_rel_piezo)
                self.ni_dev.set_position(self.position_prb)

            # Servo-Stage - Reference
            if self.toggle_move_dev.get() == 0:

                self.position_ref = float(self.old_val_ref) + float(move_rel_servo)
                pi_gcs.move_rel(pi_gcs, move_rel_servo)

        else:

            # Both, Piezo- and Servo-Stage
            self.position_prb = float(self.old_val_prb) + float(move_rel_piezo)
            self.position_ref = float(self.old_val_ref) + float(move_rel_servo)

            self.ni_dev.set_position(self.position_prb)
            pi_gcs.move_rel(pi_gcs, move_rel_servo)

        self.old_val_prb = self.position_prb
        self.old_val_ref = self.position_ref

        # print(f'PRB Position {self.position_prb:.5f}, Stepsize {move_rel_piezo:.5f} / V')
        # print(f'REF Position {self.position_ref:.5f}, Stepsize {float(move_rel_servo):.5f} / mm')
        self.pos_ref_lb.configure(text=f"REF Position {self.position_ref:.2f} mm")
        self.pos_prb_lb.configure(
            text=f"PRB Position {logic.ni_piezo_volatage_to_position(self.position_prb):.2f} µm"
        )

    # --------------------------------------------------------------------------
    def _setup_gui(self):
        """GUI Setup"""

        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")

        self.title("PI STage CTRL")
        self.geometry("400x350")

        self.grid_columnconfigure(0, weight=0)
        self.grid_rowconfigure(0, weight=0)

        self.frame = ctk.CTkFrame(self, fg_color="transparent")
        self.frame.grid(
            row=0, column=0, columnspan=2, padx=(5, 5), pady=(25, 5), sticky="nw"
        )

        self.connect_btn = ctk.CTkButton(
            self.frame, text="Connect", command=self.connect, width=150
        )
        self.connect_btn.grid(row=1, column=0, padx=(5, 5), pady=(5, 25), sticky="nw")

        self.info_lb = ctk.CTkLabel(
            self.frame, text="Stepsize in mm !!", font=("Arial", 16, "bold"), width=150
        )
        self.info_lb.grid(row=1, column=1, padx=(5, 5), pady=(5, 5), sticky="nw")

        self.pos_entry = ctk.CTkEntry(
            self.frame, placeholder_text="Absolute position", width=150
        )
        self.pos_entry.grid(row=2, column=0, padx=(5, 5), pady=(5, 5), sticky="nw")
        self.pos_entry.bind("<KeyRelease>", self._normalize_decimal)
        self.pos_entry.bind("<Return>", self._on_enter)

        self.stepsize_entry = ctk.CTkEntry(
            self.frame, placeholder_text="Step size in µm", width=150
        )
        self.stepsize_entry.grid(row=2, column=1, padx=(5, 5), pady=(5, 5), sticky="nw")
        self.stepsize_entry.bind("<KeyRelease>", self._normalize_decimal)

        self.pos_ref_lb = ctk.CTkLabel(self.frame, text="Ref = 0.0 mm", width=150)
        self.pos_ref_lb.grid(row=3, column=0, padx=(5, 5), pady=(5, 5), sticky="nw")

        self.pos_prb_lb = ctk.CTkLabel(self.frame, text="Prb = 0.0 µm", width=150)
        self.pos_prb_lb.grid(row=3, column=1, padx=(5, 5), pady=(5, 5), sticky="nw")

        self.toggle_move_dev = ctk.CTkSwitch(
            self.frame,
            text="REF/mm | PROBE/µm",
            command=self._dimension_info,
            width=150,
        )
        self.toggle_move_dev.grid(
            row=4, column=0, padx=(5, 5), pady=(5, 5), sticky="nw"
        )

        self.sync_dev = ctk.CTkCheckBox(
            self.frame, text="SYNC REF & PROB", command=self._toggle_ui, width=150
        )
        self.sync_dev.grid(row=4, column=1, padx=(5, 5), pady=(5, 5), sticky="nw")

        self.run_btn = ctk.CTkButton(
            self.frame, text="Run", command=self.move_abs, width=150
        )
        self.run_btn.grid(row=5, column=0, padx=(5, 5), pady=(5, 5), sticky="nw")

        self.up_btn = ctk.CTkButton(
            self.frame, text="up", width=150, command=lambda: self.move_rel(0)
        )
        self.up_btn.grid(row=5, column=1, padx=(5, 5), pady=(5, 5), sticky="nw")

        self.home_ref_btn = ctk.CTkButton(
            self.frame, text="Home REF", command=self.home_ref, width=150
        )
        self.home_ref_btn.grid(row=6, column=0, padx=(5, 5), pady=(5, 5), sticky="nw")

        self.down_btn = ctk.CTkButton(
            self.frame, text="down", width=150, command=lambda: self.move_rel(1)
        )
        self.down_btn.grid(row=6, column=1, padx=(5, 5), pady=(5, 5), sticky="nw")

        self.exit_btn = ctk.CTkButton(
            self.frame, text="Exit", command=self.exit, width=150
        )
        self.exit_btn.grid(row=7, column=0, padx=(5, 5), pady=(25, 5), sticky="nw")

    # --------------------------------------------------------------------------
    def _disable_controls(self) -> None:
        """Disable UI elements until connection is established."""
        self.pos_entry.configure(state="disabled")
        self.stepsize_entry.configure(state="disabled")
        self.toggle_move_dev.configure(state="disabled")
        self.sync_dev.configure(state="disabled")
        self.run_btn.configure(state="disabled")
        self.up_btn.configure(state="disabled")
        self.down_btn.configure(state="disabled")
        self.home_ref_btn.configure(state="disabled")

    # --------------------------------------------------------------------------
    def _enable_controls(self) -> None:
        """Enable UI elements after successful connection."""
        self.pos_entry.configure(state="normal")
        self.stepsize_entry.configure(state="normal")
        self.toggle_move_dev.configure(state="normal")
        self.sync_dev.configure(state="normal")
        self.run_btn.configure(state="normal")
        self.up_btn.configure(state="normal")
        self.down_btn.configure(state="normal")
        self.home_ref_btn.configure(state="normal")
        self.connect_btn.configure(state="disabled")

    # --------------------------------------------------------------------------
    def _normalize_decimal(self, event=None) -> None:
        """
        Normalize ',' value entries to '.' value entries
        """
        widget = event.widget
        value = widget.get()
        if "," in value:
            widget.delete(0, "end")
            widget.insert(0, value.replace(",", "."))

    # --------------------------------------------------------------------------
    def _on_enter(self, event) -> None:
        """
        Runs when hit enter in the position field
        """
        _ = event
        self.move_abs()

    # --------------------------------------------------------------------------
    def _toggle_ui(self) -> None:
        """
        Toggle the etry filed for abs movent on and of
        """
        if self.sync_dev.get() == 1:
            self.pos_entry.configure(fg_color="gray", state="disabled")
        else:
            self.pos_entry.configure(fg_color="#F8F9FA", state="normal")

    # --------------------------------------------------------------------------
    def _dimension_info(self) -> None:
        """
        Show information if unit is in mm or µm
        """
        if self.toggle_move_dev.get() == 1:
            self.pos_entry.configure(placeholder_text="Value in µm")
        else:
            self.pos_entry.configure(placeholder_text="Value in mm")

        self.switch_toggeld = True

    # --------------------------------------------------------------------------
    def exit(self) -> None:
        """
        Exit
        """
        if self.device_status_pi_gcs is True:
            # pi_gcs.move_fnl(pi_gcs)
            pi_gcs.disconnect(pi_gcs)
        self.quit()


# ---------- Run ----------
if __name__ == "__main__":
    app = StageCtrl()
    app.mainloop()
