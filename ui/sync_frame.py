import customtkinter as ctk


class SyncFrame(ctk.CTkFrame):
    def __init__(self, parent, ctrl, config):

        super().__init__(parent)

        self.ctrl = ctrl
        self.config = config

        self.sync_enabled = False
        self.hysteresis_enabled = False
        self.sync_factor = 0.11

        self.set_sync_ui_parts()

    def set_sync_ui_parts(self):
        """
        Exact old sync UI structure
        """

        self.recording_lb = ctk.CTkLabel(
            self,
            width=75,
            height=20,
            font=("Cosmic Sans MS", 18, "normal"),
            text="Sync Stages",
        )

        self.recording_lb.grid(row=1, column=0, padx=(5, 5), pady=(5, 5))

        self.f3a = ctk.CTkFrame(self, border_width=1, fg_color="transparent")

        self.f3a.grid(row=2, column=0, padx=(5, 5), pady=(0, 25), sticky="nw")

        # ----------------------------------------------------------
        # sync switch
        # ----------------------------------------------------------

        self.sync_switch_bt = ctk.CTkSwitch(
            self.f3a,
            text="Sync MIPOS & KINESIS",
            command=self.synchronize_kinesis_mipos,
        )

        self.sync_switch_bt.grid(
            row=0, column=0, padx=(5, 20), pady=(5, 5), sticky="nw"
        )

        # ----------------------------------------------------------
        # hysteresis switch
        # ----------------------------------------------------------

        self.hyst_switch_bt = ctk.CTkSwitch(
            self.f3a,
            text="Hystersis compensation",
            command=self.init_hysteresis_compensation,
        )

        self.hyst_switch_bt.grid(
            row=1, column=0, padx=(5, 20), pady=(5, 5), sticky="nw"
        )

        self.hyst_switch_bt.configure(state="disabled")

        # ----------------------------------------------------------
        # refractive index
        # ----------------------------------------------------------

        self.refindex_lb = ctk.CTkLabel(
            self.f3a, width=50, height=20, text="Refractive Index"
        )

        self.refindex_lb.grid(row=2, column=0, padx=(5, 5), pady=(5, 5))

        self.refractiveindex_tf = ctk.CTkEntry(
            self.f3a, width=50, height=20, justify="center"
        )

        self.refractiveindex_tf.grid(row=2, column=1, padx=(5, 5), pady=(5, 5))

        self.refractiveindex_tf.insert(0, "1.33")
        self.refractiveindex_tf.configure(state="disabled")

        # ----------------------------------------------------------
        # sync move buttons
        # ----------------------------------------------------------

        self.move_bt_p1 = ctk.CTkButton(
            self.f3a,
            width=75,
            height=20,
            text="+1 µm",
            command=lambda: self.sync_move(-0.001, -1),
        )

        self.move_bt_p1.grid(row=3, column=0, padx=(5, 5), pady=(5, 5))

        self.move_bt_p1.configure(state="disabled")

        self.move_bt_m1 = ctk.CTkButton(
            self.f3a,
            width=75,
            height=20,
            text="-1 µm",
            command=lambda: self.sync_move(0.001, 1),
        )

        self.move_bt_m1.grid(row=3, column=1, padx=(5, 5), pady=(5, 5))

        self.move_bt_m1.configure(state="disabled")

        self.move_bt_p10 = ctk.CTkButton(
            self.f3a,
            width=75,
            height=20,
            text="+10 µm",
            command=lambda: self.sync_move(-0.01, -10),
        )

        self.move_bt_p10.grid(row=4, column=0, padx=(5, 5), pady=(5, 5))

        self.move_bt_p10.configure(state="disabled")

        self.move_bt_m10 = ctk.CTkButton(
            self.f3a,
            width=75,
            height=20,
            text="-10 µm",
            command=lambda: self.sync_move(0.01, 10),
        )

        self.move_bt_m10.grid(row=4, column=1, padx=(5, 5), pady=(5, 5))

        self.move_bt_m10.configure(state="disabled")

        # ----------------------------------------------------------
        # sync factor
        # ----------------------------------------------------------

        self.syncfactor_lb = ctk.CTkLabel(
            self.f3a, width=50, height=20, text="Syncfaktor"
        )

        self.syncfactor_lb.grid(row=5, column=0, padx=(5, 5), pady=(5, 5))

        self.syncfactor_tf = ctk.CTkEntry(
            self.f3a, width=50, height=20, justify="center"
        )

        self.syncfactor_tf.grid(row=5, column=1, padx=(5, 5), pady=(5, 5))

        self.syncfactor_tf.insert(0, "0.11")

    # ----------------------------------------------------------
    # migrated callbacks
    # ----------------------------------------------------------

    def synchronize_kinesis_mipos(self):

        self.sync_enabled = not self.sync_enabled

        if self.sync_enabled:
            self.hyst_switch_bt.configure(state="normal")
            self.refractiveindex_tf.configure(state="normal")

            self.move_bt_p1.configure(state="normal")
            self.move_bt_m1.configure(state="normal")
            self.move_bt_p10.configure(state="normal")
            self.move_bt_m10.configure(state="normal")

        else:
            self.hyst_switch_bt.configure(state="disabled")
            self.refractiveindex_tf.configure(state="disabled")

            self.move_bt_p1.configure(state="disabled")
            self.move_bt_m1.configure(state="disabled")
            self.move_bt_p10.configure(state="disabled")
            self.move_bt_m10.configure(state="disabled")

    def init_hysteresis_compensation(self):

        self.hysteresis_enabled = not self.hysteresis_enabled

    def sync_move(self, kcube_delta, nidaq_delta):

        try:
            refractive_index = float(self.refractiveindex_tf.get())
        except Exception:
            refractive_index = 1.33

        try:
            self.sync_factor = float(self.syncfactor_tf.get())
        except Exception:
            self.sync_factor = 0.11

        corrected_kcube = kcube_delta * refractive_index * self.sync_factor

        self.ctrl.sync_move(corrected_kcube, nidaq_delta)
