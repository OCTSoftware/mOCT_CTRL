"""
LED Widget
"""
import customtkinter as ctk


class led(ctk.CTkCanvas):
    """
    LED Widget
    """
    def __init__(self, master, size=20, color_off="gray", color_on="green"):
        super().__init__(
            master,
            width=size,
            height=size,
            highlightthickness=0,
            bg="#333333"
        )

        self.size = size
        self.color_off = color_off
        self.color_on = color_on
        self.state = False

        self.led = self.create_oval(
            2, 2, size-2, size-2,
            fill=self.color_off,
            outline=""
        )

    def on(self):
        self.itemconfig(self.led, fill=self.color_on)
        self.state = True

    def off(self):
        self.itemconfig(self.led, fill=self.color_off)
        self.state = False

    def toggle(self):
        if self.state:
            self.off()
        else:
            self.on()

