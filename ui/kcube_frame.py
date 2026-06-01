import customtkinter as ctk

from utils.image_loader import load_image
from utils.fileIO import FILEIO


class KcubeFrame(ctk.CTkFrame):

    def __init__(self, parent, ctrl, config):

        super().__init__(parent)

        self.ctrl = ctrl
        self.config = config

        serial = self.config.get("kcube_serial_number", "unknown")
        self.kcube_sn_info = f"SN: {serial}"

        self.last_selected = self.config.get("last_selected", "home")

        # ------------------------------------------------------------------
        # original layout preserved
        # ------------------------------------------------------------------

        self.kcube_f0 = ctk.CTkFrame(self, fg_color="transparent")
        self.kcube_f0.grid(row=0,column=1,padx=(2.5, 5),pady=(5, 5),sticky="nw")

        self.kcube_f01 = ctk.CTkFrame(self.kcube_f0,fg_color="transparent")

        self.kcube_f01.grid(row=0,column=0,padx=(5, 2.5),pady=(5, 5),sticky="nw")

        self.kcube_lb = ctk.CTkLabel(self.kcube_f01, width=75, height=20,font=("Cosmic Sans MS", 18, "normal"), text="KINESIS")

        self.kcube_lb.grid(row=0,column=0,padx=(5, 5),pady=(5, 5))

        img = load_image("zref.png")

        self.ctk_image = ctk.CTkImage(light_image=img,dark_image=img,size=(40, 40))

        self.icon = ctk.CTkLabel(self.kcube_f01,image=self.ctk_image, text="")

        self.icon.grid(row=0,column=1,padx=(0, 40),pady=(0, 0))

        self.kcube_f1 = ctk.CTkFrame(self.kcube_f0,border_width=1,fg_color="transparent")

        self.kcube_f1.grid(row=1,column=0,padx=(5, 5),pady=(5, 5),sticky="nw")

        self.kcube_f2 = ctk.CTkFrame(self.kcube_f1,fg_color="transparent")

        self.kcube_f2.grid(row=0,column=0,padx=(5, 5),pady=(10, 10))

        self.kcube_f3 = ctk.CTkFrame(self.kcube_f2,fg_color="transparent")

        self.kcube_f3.grid(row=1,column=0,padx=(5, 5),pady=(0, 0))

        # ------------------------------------------------------------------
        # movement buttons
        # ------------------------------------------------------------------

        self.kcube_bt_p100 = ctk.CTkButton(self.kcube_f3, width=75, height=20, text="+100 µm",command=lambda: self.move_relative_and_refresh(0.1))

        self.kcube_bt_p100.grid(row=0, column=0, padx=5, pady=5)

        self.kcube_bt_p50 = ctk.CTkButton(self.kcube_f3, width=75, height=20, text="+50 µm",command=lambda: self.move_relative_and_refresh(0.05))

        self.kcube_bt_p50.grid(row=1, column=0, padx=5, pady=5)

        self.kcube_bt_p10 = ctk.CTkButton(self.kcube_f3, width=75, height=20, text="+10 µm",command=lambda: self.move_relative_and_refresh(0.01))

        self.kcube_bt_p10.grid(row=2, column=0, padx=5, pady=5)

        # ------------------------------------------------------------------
        # slider
        # ------------------------------------------------------------------

        self.kcube_sldr = ctk.CTkSlider(self.kcube_f3,orientation=ctk.VERTICAL, height=120,from_=0, to=100)

        self.kcube_sldr.grid(row=3,column=0,padx=(5, 5),pady=(0, 0))

        self.kcube_sldr.bind("<B1-Motion>",self.kcube_on_slider_move)

        self.kcube_sldr.bind("<ButtonRelease-1>",self.kcube_on_mouse_up)

        self.kcube_bt_m10 = ctk.CTkButton(self.kcube_f3, width=75, height=20, text="-10 µm",command=lambda: self.move_relative_and_refresh(-0.01))

        self.kcube_bt_m10.grid(row=4, column=0, padx=5, pady=5)

        self.kcube_bt_m50 = ctk.CTkButton(self.kcube_f3, width=75, height=20, text="-50 µm",command=lambda: self.move_relative_and_refresh(-0.05))

        self.kcube_bt_m50.grid(row=5, column=0, padx=5, pady=5)

        self.kcube_bt_m100 = ctk.CTkButton(self.kcube_f3, width=75, height=20, text="-100 µm",command=lambda: self.move_relative_and_refresh(-0.1))

        self.kcube_bt_m100.grid(row=7, column=0, padx=5, pady=5)

        # ------------------------------------------------------------------
        # position block
        # ------------------------------------------------------------------

        self.kcube_f4 = ctk.CTkFrame(self.kcube_f2,fg_color="transparent")

        self.kcube_f4.grid(row=1,column=1,padx=(5, 5), pady=(0, 0))

        self.kcube_lb_position = ctk.CTkLabel(self.kcube_f4, width=75, height=20, text="")

        self.kcube_lb_position.grid(row=0, column=0, padx=5, pady=5)

        self.kcube_tf_position = ctk.CTkEntry(self.kcube_f4, width=75, height=20, justify="center", placeholder_text="pos / mm")

        self.kcube_tf_position.grid(row=1, column=0, padx=5, pady=5)
        self.kcube_tf_position.insert(0, "0")

        self.kcube_bt_go = ctk.CTkButton(self.kcube_f4, width=75, height=20, text="Go", command=self.move_absolute_from_entry)

        self.kcube_bt_go.grid(row=2, column=0, padx=5, pady=5)

        self.kcube_lb_void = ctk.CTkLabel(self.kcube_f4, width=75, height=20, text="")

        self.kcube_lb_void.grid(row=4, column=0, padx=5, pady=5)

        # ------------------------------------------------------------------
        # right controls
        # ------------------------------------------------------------------

        self.kcube_f5 = ctk.CTkFrame(self.kcube_f2,fg_color="transparent")

        self.kcube_f5.grid(row=1,column=2,padx=(5, 5),pady=(0, 0))

        self.kcube_cb_speed = ctk.CTkComboBox(self.kcube_f5, width=75, height=20,values=["slow", "medium", "fast"])

        self.kcube_cb_speed.grid(row=0,column=0,padx=5,pady=(100, 5))

        self.kcube_bt_enable = ctk.CTkButton(self.kcube_f5, width=75, height=20, text="Enable")

        self.kcube_bt_enable.grid(row=1, column=0, padx=5, pady=5)

        self.kcube_bt_home = ctk.CTkButton(self.kcube_f5, width=75, height=20, text="Home",command=self.home_and_refresh)

        self.kcube_bt_home.grid(row=2, column=0, padx=5, pady=5)

        self.kcube_cb_objective = ctk.CTkComboBox(self.kcube_f5, width=75, height=20,values=["home", "05x16", "10x03", "20x05", "40x08"],command=self.select_objective)

        self.kcube_cb_objective.grid(row=3, column=0, padx=5, pady=5)

        self.kcube_lb_vers = ctk.CTkLabel(self.kcube_f5, width=75, height=20,font=("Cosmic Sans MS", 10, "normal"), text=self.kcube_sn_info)

        self.kcube_lb_vers.grid(row=4,column=0,padx=5,pady=(70, 5))

        # ------------------------------------------------------------------
        # init
        # ------------------------------------------------------------------

        self.kcube_cb_objective.set(self.last_selected)

        try:
            pos = FILEIO.read_value(self.config.path,self.last_selected)

            pos = float(pos)

        except Exception:
            pos = 0.0

        self.refresh_kcube_ui()

    # ----------------------------------------------------------------------
    # callbacks
    # ----------------------------------------------------------------------

    def move_absolute_from_entry(self):
        """
        
        """

        value = float(self.kcube_tf_position.get())
        try:
            self.ctrl.move_absolute(value)
            self.refresh_kcube_ui()
        except  Exception as e:
            print(f"self.ctrl.move_absolute(value) -> {e}")

    def kcube_on_slider_move(self, event):
        """
        
        """

        value = self.kcube_sldr.get()
        self.refresh_kcube_ui()

    def kcube_on_mouse_up(self, event):
        """
        
        """

        value = self.kcube_sldr.get()
        
        try:
            self.ctrl.move_absolute(value)
            self.refresh_kcube_ui()
        except  Exception as e:
            print(f"self.ctrl.move_absolute(value) -> {e}")

    def select_objective(self, selected):
        """
        
        """

        pos = FILEIO.read_value(self.config.path, selected)
        pos = float(pos)
        
        try:
            self.ctrl.move_absolute(value)
            self.refresh_kcube_ui()
        except  Exception as e:
            print(f"self.ctrl.move_absolute(value) -> {e}")

    def refresh_kcube_ui(self):
        """
        
        """

        pos = self.ctrl.state.kcube_position
        self.kcube_lb_position.configure(text=f"{pos:.2f}")
        self.kcube_sldr.set(pos)

    def move_relative_and_refresh(self, delta):
        """
        
        """

        self.ctrl.move_relative(delta)
        self.refresh_kcube_ui()
    
    def home_and_refresh(self):
        """
        
        """

        self.ctrl.home()
        self.refresh_kcube_ui()
        self.kcube_cb_objective.set(self.kcube_cb_objective.cget("values")[0])
