""" GUI """

from pathlib import Path
import tkinter as tk
import customtkinter as ctk

from utils.pluginmanager import PluginManager
from utils.check_config import CheckConfig

class App(ctk.CTk):
    """ __APP__ """

    plugin = False

    config_path = Path(__file__).resolve().parent / "resources" / "config.txt"
    using_kcube = CheckConfig.load_variables(config_path, 'using_kcube')

    def __init__(self):
        """ __init__ """

        super().__init__()
        self.title("Test GUI")
        self.geometry("500x300")

        lbl = ctk.CTkLabel(self, text="Plugin Manager")
        lbl.pack(expand=True, fill="both", padx=40, pady=40)

        self.checkbutton_checkmark = tk.BooleanVar(value=False)
        self.create_menu()
        self.plugin_manager = PluginManager(self.config_path)

    def create_menu(self) -> None:
        """ Create and configure menu bar with checkbutton """

        menu_bar = tk.Menu(self)
        file_menu = tk.Menu(menu_bar, tearoff=0)
        menu_bar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Exit", command=self.exit)

        option_menu = tk.Menu(menu_bar, tearoff=0)

        option_menu.add_checkbutton(
            label="Load Kinesis",
            variable=self.checkbutton_checkmark,
            command=lambda: self.plugin_manager.toggle_plugin(
                "kinesis.py", "kinesis", "KcubeHandle", self.checkbutton_checkmark
            )
        )

        menu_bar.add_cascade(label="Options", menu=option_menu)
        self.config(menu=menu_bar)

    def exit(self) -> None:
        """Exit app """

        self.quit()


if __name__ == "__main__":
    app = App()
    app.mainloop()
