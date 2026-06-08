import customtkinter as ctk

import logging
logger = logging.getLogger(__name__)


class NidaqChannelFrame(ctk.CTkFrame):

    def __init__(self, parent, ctrl, config, title):

        super().__init__(parent)

        self.ctrl = ctrl

        self.ctrl.position_callback = self.on_position_changed

        self.position = getattr(ctrl, "position", 0.0)

        self.min_position = float(config.get("nidaq", "position", "min"))
        self.max_position = float(config.get("nidaq", "position", "max"))
        self.center_position = float(config.get("nidaq", "position", "center"))

        large = int(config.get("nidaq", "jog", "large"))
        medium = int(config.get("nidaq", "jog", "medium"))
        small = int(config.get("nidaq", "jog", "small"))

        self.jog_steps = [large, medium, small]

        # Title

        ctk.CTkLabel(self, text=title, font=("Arial", 16, "bold")).grid(
            row=0, column=0, columnspan=3, pady=(5, 10)
        )

        self.position_label = ctk.CTkLabel(self, text=f"Position: {self.position:.1f}")

        self.position_label.grid(row=1, column=0, columnspan=3, pady=(0, 10))

        # Positive buttons

        ctk.CTkButton(
            self, text=f"+{large}", width=50, command=lambda: self.move_relative(large)
        ).grid(row=2, column=0, padx=2, pady=2)

        ctk.CTkButton(
            self, text=f"+{medium}", width=50, command=lambda: self.move_relative(medium)
        ).grid(row=2, column=1, padx=2, pady=2)

        ctk.CTkButton(
            self, text=f"+{small}", width=50, command=lambda: self.move_relative(small)
        ).grid(row=2, column=2, padx=2, pady=2)

        # Slider

        self.slider = ctk.CTkSlider(
            self,
            orientation="vertical",
            from_=self.min_position,
            to=self.max_position,
            height=150,
        )

        self.slider.grid(row=3, column=0, columnspan=3, pady=5)

        self.slider.set(self.position)

        self.slider.bind("<ButtonRelease-1>", self.slider_released)

        self.slider.configure(command=self.slider_changed)

        # Negative buttons

        ctk.CTkButton(
            self, text=f"-{small}", width=50, command=lambda: self.move_relative(-small)
        ).grid(row=4, column=0, padx=2, pady=2)

        ctk.CTkButton(
            self, text=f"-{medium}", width=50, command=lambda: self.move_relative(-medium)
        ).grid(row=4, column=1, padx=2, pady=2)

        ctk.CTkButton(
            self, text=f"-{large}", width=50, command=lambda: self.move_relative(-large)
        ).grid(row=4, column=2, padx=2, pady=2)

        # Go to position

        self.position_entry = ctk.CTkEntry(self, width=80)

        self.position_entry.grid(
            row=5, column=0, columnspan=2, padx=2, pady=5, sticky="nsew"
        )

        self.position_entry.insert(0, str(int(self.position)))

        ctk.CTkButton(self, text="Go", width=50, command=self.goto_position).grid(
            row=5, column=2, padx=2, pady=5
        )

        # Center

        ctk.CTkButton(self, text="Center", command=self.center).grid(
            row=6, column=0, columnspan=3, padx=2, pady=(5, 10), sticky="nsew"
        )

        # Does not need be here for the actual hardware settings

        # self.refindex_lb = ctk.CTkLabel(
        #     self, width=50, height=20, text="Refractive Index"
        # )

        # self.refindex_lb.grid(row=7, column=0, padx=(5, 5), pady=(5, 5))

        # self.refractiveindex_tf = ctk.CTkEntry(
        #     self, width=50, height=20, justify="center"
        # )

        # self.refractiveindex_tf.grid(row=7, column=1, padx=(5, 5), pady=(5, 5))

        # self.refractiveindex_tf.insert(0, "1.33")
        # self.refractiveindex_tf.configure(state="disabled")

    def update_display(self):

        self.position_label.configure(text=f"Position: {self.position:.1f}")

        self.slider.set(self.position)

        self.position_entry.delete(0, "end")
        self.position_entry.insert(0, f"{self.position:.1f}")

    def move_absolute(self, position):

        position = max(self.min_position, min(self.max_position, position))

        try:
            self.ctrl.move_absolute(position)

            self.position = self.ctrl.position

            self.update_display()

        except Exception as e:
            logger.debug(f"[NIDAQ_FRAME] [NIDAQ][ERROR] -> {e}")

    def move_relative(self, delta):

        self.move_absolute(self.position + delta)

    def goto_position(self):

        try:
            self.move_absolute(float(self.position_entry.get()))

        except ValueError:
            pass

    def center(self):

        self.move_absolute(self.center_position)

    def slider_released(self, event):

        self.move_absolute(self.slider.get())

    def slider_changed(self, value):

        self.position_label.configure(text=f"Position: {float(value):.1f}")

    def on_position_changed(self, position):

        self.position = position

        self.after(0, self.update_display)

class NidaqFrame(ctk.CTkFrame):

    def __init__(self, parent, controllers, config):

        super().__init__(parent)

        ctk.CTkLabel(self, text="NIDAQ", font=("Arial", 18, "bold")).grid(
            row=0, column=0, columnspan=max(1, len(controllers)), pady=(10, 10)
        )

        for idx, ctrl in enumerate(controllers):
            NidaqChannelFrame(self, ctrl, config, title=f"NIDAQ {idx + 1}").grid(
                row=1, column=idx, padx=5, pady=5, sticky="nsew"
            )