from utils.config_io import CONFIG_IO

class ConfigManager:

    def __init__(self, path):
        self.path = path

    def get(self, key, default=None):
        return CONFIG_IO.read_value(self.path, key, default)

    def get_bool(self, key):
        value = CONFIG_IO.read_value(self.path, key, "true")
        return str(value).strip().lower() == "true"

    def get_float(self, key, default=0.0):
        try:
            return float(CONFIG_IO.read_value(self.path, key, default))
        except (TypeError, ValueError):
            return default

    def set(self, key, value):
        CONFIG_IO.write_value(self.path, key, value)