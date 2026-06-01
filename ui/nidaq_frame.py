
import customtkinter as ctk

from utils.image_loader import load_image


class NidaqFrame(ctk.CTkFrame):

    def __init__(self, parent, ctrl, config):

        super().__init__(parent)

        self.ctrl = ctrl
        self.config = config

        self.nidaq_position = self.ctrl.position

        # ----------------------------------------------------------
        # exact old UI structure preserved
        # ----------------------------------------------------------

        self.nidaq_f0 = ctk.CTkFrame(self, fg_color="transparent")

        self.nidaq_f0.grid(row=0, column=0, padx=(5, 2.5), pady=(5, 5), sticky="nw")

        self.nidaq_f01 = ctk.CTkFrame(self.nidaq_f0, fg_color="transparent")

        self.nidaq_f01.grid(row=0, column=0, padx=(5, 2.5), pady=(5, 5), sticky="nw")

        self.nidaq_title = ctk.CTkLabel(self.nidaq_f01, width=75, height=20, font=("Cosmic Sans MS", 18, "normal"), text="MIPOS")

        self.nidaq_title.grid(row=0, column=0, padx=(5, 5), pady=(5, 5))

        img = load_image("focus.png")

        self.ctk_image = ctk.CTkImage(light_image=img, dark_image=img, size=(40, 40))

        self.icon = ctk.CTkLabel(self.nidaq_f01, image=self.ctk_image, text="")

        self.icon.grid(row=0, column=1, padx=(0, 0), pady=(0, 0))

        self.nidaq_f1 = ctk.CTkFrame(self.nidaq_f0, border_width=1, fg_color="transparent")

        self.nidaq_f1.grid(row=1, column=0, padx=(5, 5), pady=(5, 5))

        self.nidaq_f2 = ctk.CTkFrame(self.nidaq_f1, fg_color="transparent")

        self.nidaq_f2.grid(row=3, column=0, padx=(5, 5), pady=(15, 15))

        # ----------------------------------------------------------
        # buttons
        # ----------------------------------------------------------

        self.nidaq_bt_p50 = ctk.CTkButton(self.nidaq_f2, width=75, height=20, text="+50", command=lambda: self.nidaq_move(50))

        self.nidaq_bt_p50.grid(row=0, column=0, padx=5, pady=5)

        self.nidaq_bt_p10 = ctk.CTkButton(self.nidaq_f2, width=75, height=20, text="+10", command=lambda: self.nidaq_move(10))

        self.nidaq_bt_p10.grid(row=1, column=0, padx=5, pady=5)

        self.nidaq_bt_p1 = ctk.CTkButton(self.nidaq_f2, width=75, height=20, text="+1", command=lambda: self.nidaq_move(1))

        self.nidaq_bt_p1.grid(row=2, column=0, padx=5, pady=5)

        # ----------------------------------------------------------
        # slider
        # ----------------------------------------------------------

        self.nidaq_sldr = ctk.CTkSlider(self.nidaq_f2, orientation=ctk.VERTICAL, height=120, from_=0, to=400)

        self.nidaq_sldr.grid(row=4, column=0, padx=(5, 5), pady=(0, 0))

        self.nidaq_sldr.set(int(self.ctrl.position))

        self.nidaq_sldr.bind("<ButtonPress-1>", self.nidaq_on_mouse_released)

        self.nidaq_sldr.bind("<ButtonRelease-1>", self.nidaq_on_mouse_released)

        self.nidaq_sldr.bind("<B1-Motion>", self.nidaq_on_slider_move)

        self.nidaq_bt_m1 = ctk.CTkButton(self.nidaq_f2, width=75, height=20, text="-1", command=lambda: self.nidaq_move(-1))

        self.nidaq_bt_m1.grid(row=5, column=0, padx=5, pady=5)

        self.nidaq_bt_m10 = ctk.CTkButton(self.nidaq_f2, width=75, height=20, text="-10", command=lambda: self.nidaq_move(-10))

        self.nidaq_bt_m10.grid(row=6, column=0, padx=5, pady=5)

        self.nidaq_bt_m50 = ctk.CTkButton(self.nidaq_f2, width=75, height=20, text="-50", command=lambda: self.nidaq_move(-50))

        self.nidaq_bt_m50.grid(row=7, column=0, padx=5, pady=5)

        # ----------------------------------------------------------
        # right panel
        # ----------------------------------------------------------

        self.nidaq_f3 = ctk.CTkFrame(self.nidaq_f1, fg_color="transparent")

        self.nidaq_f3.grid(row=3, column=1, padx=(5, 5), pady=(0, 0))

        self.nidaq_lb = ctk.CTkLabel(self.nidaq_f3, width=75, height=20)

        self.nidaq_lb.grid(row=0, column=0, padx=5, pady=5)

        self.nidaq_tf = ctk.CTkEntry(self.nidaq_f3, width=75, height=20, justify="center")

        self.nidaq_tf.grid(row=1, column=0, padx=5, pady=5)
        self.nidaq_tf.insert(0, "0")

        self.nidaq_bt_go = ctk.CTkButton(self.nidaq_f3, width=75, height=20, text="Go", command=self.nidaq_go)

        self.nidaq_bt_go.grid(row=2, column=0, padx=5, pady=5)

        self.nidaq_bt_center = ctk.CTkButton(self.nidaq_f3, width=75, height=20, text="Center", command=self.nidaq_center)

        self.nidaq_bt_center.grid(row=3, column=0, padx=5, pady=5)

        self.nidaq_init_position()

    # ----------------------------------------------------------
    # migrated callbacks
    # ----------------------------------------------------------

    def nidaq_move(self, delta):
        self.nidaq_position += delta
        self.nidaq_position = max(0, min(400, self.nidaq_position))

        try:
            self.ctrl.move_absolute(self.nidaq_position)
            self.nidaq_lb.configure(text=f"{self.nidaq_position:.1f}")
            self.nidaq_sldr.set(self.nidaq_position)
        except:
            print(f"self.ctrl.move_absolute -> {e}")

    def nidaq_go(self):
        value = float(self.nidaq_tf.get())

        self.nidaq_position = value

        try:
            self.ctrl.move_absolute(value)
            self.nidaq_lb.configure(text=f"{value:.1f}")
            self.nidaq_sldr.set(value)
        except:
            print(f"self.ctrl.move_absolute -> {e}")        

    def nidaq_center(self):
        self.nidaq_position = 200.0

        try:
            self.ctrl.move_absolute(200)
            self.nidaq_lb.configure(text="200.0")
            self.nidaq_sldr.set(200)
        except:
            print(f"self.ctrl.move_absolute -> {e}")    

    def nidaq_on_slider_move(self, event):
        value = self.nidaq_sldr.get()

        self.nidaq_lb.configure(text=f"{value:.1f}")

    def nidaq_on_mouse_released(self, event):
        value = self.nidaq_sldr.get()

        self.nidaq_position = value

        try:
            self.ctrl.move_absolute(value)
            self.nidaq_lb.configure(text=f"{value:.1f}")
        except:
            print(f"self.ctrl.move_absolute -> {e}")  

    def nidaq_init_position(self):
        self.nidaq_lb.configure(text=f"{self.nidaq_position:.1f}")

        self.nidaq_sldr.set(self.nidaq_position)