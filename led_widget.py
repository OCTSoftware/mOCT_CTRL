""" Plot a LED and toggle the color """

import tkinter as tk
import customtkinter as ctk


class LEDWidget(ctk.CTkFrame):
    ''' LEDWidget '''

    def __init__(self, master=None, width=40, height=40, **kwargs):
        ''' __init__ '''

        super().__init__(master, **kwargs)
        self.width = width
        self.height = height
        self.canvas = tk.Canvas(self, width=self.width, height=self.height, highlightthickness=0, bg="gray92")
        self.canvas.pack()

        # Initialize LED state (off by default)
        self.state = False
        self.led_color = "gray"
        self.led = self.canvas.create_oval(5, 5, self.width-5, self.height-5, fill=self.led_color, outline=str(self.led_color))

    def set_state(self, state: bool):
        '''Sets the state of the LED (True for on, False for off).'''

        self.state = state
        if self.state is True:
            self.led_color = "gray"
        else:
            self.led_color = "red"
        self.canvas.itemconfig(self.led, fill=self.led_color, outline=str(self.led_color))

    def toggle(self):
        '''Toggles the LED state between on and off.'''

        self.set_state(not self.state)
