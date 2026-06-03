import json


class ConfigManager:

    def __init__(self, path):

        self.path = path

        with open(path, "r", encoding="utf-8") as f:
            self.data = json.load(f)

    def get(self, *keys, default=None):

        value = self.data

        try:

            for key in keys:
                value = value[key]

            return value

        except (KeyError, TypeError):

            return default

    def get_bool(self, *keys):

        return bool(self.get(*keys, default=False))

    def set(self, *keys, value):

        data = self.data

        for key in keys[:-1]:

            if key not in data:
                data[key] = {}

            data = data[key]

        data[keys[-1]] = value

    def save(self):

        with open(self.path, "w", encoding="utf-8") as f:

            json.dump(
                self.data,
                f,
                indent=4
            )