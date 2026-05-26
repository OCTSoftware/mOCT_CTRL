from types import ModuleType
import importlib
import os
import sys
from typing import Tuple, List, Optional
from pathlib import Path

class PluginManager:
    """Manages dynamic loading and unloading of hardware plugins."""

    def __init__(self, config_path: str):
        self.config_path = config_path
        self.loaded_modules: dict[str, ModuleType] = {}
        self.plugin_active: dict[str, bool] = {}

    def load_plugin(self, module_path: str, module_name: str, import_names: List[str]) -> Tuple[int, Optional[ModuleType]]:
        """
        Dynamic equivalent of 'from module_name import name1, name2, ...'

        Args:
            module_path: Full path to .py file or package directory
            module_name: Name to register in sys.modules (e.g. 'FOO')
            import_names: List of names to import (e.g. ['BAR'])

        Returns:
            Tuple of (status_code, module):
            - 0, module: Success
            - -1, None: Cannot load module
            - -2, None: Missing attribute(s)
        """
        if not os.path.isdir(module_path) and not module_path.endswith('.py'):
            module_path += '.py'

        module = None
        try:
            spec = importlib.util.spec_from_file_location(module_name, module_path)
            if spec is None:
                return -1, None

            module = importlib.util.module_from_spec(spec)
            sys.modules[module_name] = module
            spec.loader.exec_module(module)

            for name in import_names:
                if not hasattr(module, name):
                    return -2, None

            for name in import_names:
                globals()[name] = getattr(module, name)

            self.loaded_modules[module_name] = module
            self.plugin_active[module_name] = True
            return 0, module

        except Exception:
            return -1, None

    def unload_plugin(self, module_name: str, import_names: List[str]) -> None:
        """Cleanup after load_plugin - removes module and imported names."""
        if module_name in sys.modules:
            del sys.modules[module_name]

        for name in import_names:
            if name in globals() and getattr(globals()[name], '__module__', '') == module_name:
                del globals()[name]

        self.loaded_modules.pop(module_name, None)
        self.plugin_active[module_name] = False

    def toggle_plugin(self, fname_plugin: str, hw_name: str, hw_handle: str, check_var: Optional['tk.BooleanVar'] = None) -> None:
        """
        Toggle plugin loading/unloading (renamed from drv_plugin).

        Args:
            fname_plugin: Plugin file name
            hw_name: Hardware name for logging
            hw_handle: Handle class name
            check_var: Optional BooleanVar for checkbox sync
        """
        import_names = [hw_handle]

        if self.plugin_active.get(hw_name, False):
            print(f"Unloading {hw_name}")
            self.unload_plugin(hw_name, import_names)
            if check_var:
                check_var.set(False)
        else:
            print(f"Loading {hw_name}")
            status, mod = self.load_plugin(fname_plugin, hw_name, import_names)

            if status == 0:
                print(f"Loaded successfully: {mod}")
                kcube_serial = FILEIO.read_value(self.config_path, 'kcube_serial_number')
                # Use loaded handle: e.g., kcube = globals()[hw_handle](str(int(kcube_serial)))
            elif status == -1:
                print("Load failed")
            elif status == -2:
                print("Missing attributes")

            if check_var:
                check_var.set(status == 0)