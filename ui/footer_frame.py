import customtkinter as ctk


class FooterFrame(ctk.CTkFrame):

    def __init__(self, parent):

        super().__init__(parent, fg_color="transparent")

        self.parent = parent

        self.f4 = ctk.CTkFrame(self,fg_color="transparent")

        self.f4.grid(row=3,column=1,padx=(5, 5),pady=(0, 5),sticky="sw")

        self.f41 = ctk.CTkFrame(self.f4,fg_color="transparent")

        self.f41.grid(row=0,column=0,padx=(5, 5),pady=(0, 0))

        self.f4_switch = ctk.CTkSwitch(self.f41,text="Dark/Light",command=self.set_appearance_mode,onvalue="dark",offvalue="light")

        self.f4_switch.grid(row=0,column=0,padx=(5, 20),pady=(5, 5))

        self.f4_switch.select()

        self.f4_bt_2 = ctk.CTkButton(self.f41,width=75,height=20,text="Exit",command=self.parent.destroy)

        self.f4_bt_2.grid(row=0,column=1,padx=(5, 5),pady=(5, 5))

    def set_appearance_mode(self):

        mode = self.f4_switch.get()

        ctk.set_appearance_mode(mode)