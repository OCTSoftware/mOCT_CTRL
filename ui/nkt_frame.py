import customtkinter as ctk

from utils.image_loader import load_image


class NktFrame(ctk.CTkFrame):
    def __init__(self, parent, ctrl, config):

        super().__init__(parent)

        self.ctrl = ctrl
        self.config = config

        self.nkt_power = 100
        self.interlock_ok = False
        self.laser_enabled = False

        # ----------------------------------------------------------
        # exact old UI structure preserved
        # ----------------------------------------------------------

        self.nkt_f0 = ctk.CTkFrame(self, fg_color="transparent")

        self.nkt_f0.grid(row=0, column=2, padx=(2.5, 5), pady=(5, 5), sticky="nw")

        self.nkt_f01 = ctk.CTkFrame(self.nkt_f0, fg_color="transparent")

        self.nkt_f01.grid(row=0, column=0, padx=(5, 2.5), pady=(5, 5), sticky="nw")

        self.nkt_lb = ctk.CTkLabel(
            self.nkt_f01,
            width=75,
            height=20,
            font=("Cosmic Sans MS", 18, "normal"),
            text="NKT",
        )

        self.nkt_lb.grid(row=0, column=0, padx=(5, 5), pady=(5, 5))

        img = load_image("laser.png")

        self.ctk_image = ctk.CTkImage(light_image=img, dark_image=img, size=(40, 40))

        self.icon = ctk.CTkLabel(self.nkt_f01, image=self.ctk_image, text="")

        self.icon.grid(row=0, column=1, padx=(0, 0), pady=(0, 0))

        self.nkt_f1 = ctk.CTkFrame(self.nkt_f0, border_width=1, fg_color="transparent")

        self.nkt_f1.grid(row=1, column=0, padx=(5, 5), pady=(5, 5), sticky="nw")

        # ----------------------------------------------------------
        # buttons
        # ----------------------------------------------------------

        self.nkt_bt_power = ctk.CTkButton(
            self.nkt_f1,
            width=75,
            height=20,
            text="Interlock",
            command=self.nkt_interlock,
        )

        self.nkt_bt_power.grid(row=0, column=0, padx=(5, 5), pady=(20, 5))

        self.nkt_bt_laser = ctk.CTkButton(
            self.nkt_f1, width=75, height=20, text="On/Off", command=self.nkt_laser
        )

        self.nkt_bt_laser.grid(row=1, column=0, padx=(5, 5), pady=(5, 20))

        # ----------------------------------------------------------
        # power slider
        # ----------------------------------------------------------

        self.nkt_sldr = ctk.CTkSlider(
            self.nkt_f1, orientation=ctk.HORIZONTAL, width=80, from_=25, to=100
        )

        self.nkt_sldr.set(100)
        self.ctrl.set_current(100)

        self.nkt_sldr.grid(row=2, column=0, padx=(5, 5), pady=(0, 0))

        self.nkt_sldr.bind("<ButtonPress-1>", self.nkt_on_mouse_down)

        self.nkt_sldr.bind("<ButtonRelease-1>", self.nkt_on_mouse_up)

        self.nkt_sldr.bind("<B1-Motion>", self.nkt_on_slider_move)

        self.nkt_tf_power = ctk.CTkLabel(self.nkt_f1, width=75, height=20, text="100")

        self.nkt_tf_power.grid(row=3, column=0, padx=(5, 40), pady=(5, 5))

    # ----------------------------------------------------------
    # migrated callbacks
    # ----------------------------------------------------------

    def nkt_interlock(self):

        self.ctrl.reset_interlock()

        self.interlock_ok = not self.interlock_ok

        if self.interlock_ok:
            self.nkt_bt_power.configure(fg_color="green")
        else:
            self.nkt_bt_power.configure(fg_color="gray")

    def nkt_laser(self):

        if not self.interlock_ok:
            return

        self.laser_enabled = not self.laser_enabled

        self.ctrl.toggle()

        if self.laser_enabled:
            self.nkt_bt_laser.configure(fg_color="red")
        else:
            self.nkt_bt_laser.configure(fg_color="green")

    def nkt_on_mouse_down(self, event):
        pass

    def nkt_on_slider_move(self, event):
        value = int(self.nkt_sldr.get())

        self.nkt_tf_power.configure(text=str(value))

    def nkt_on_mouse_up(self, event):
        value = int(self.nkt_sldr.get())

        self.nkt_power = value

        self.ctrl.set_current(value)

        self.nkt_tf_power.configure(text=str(value))
