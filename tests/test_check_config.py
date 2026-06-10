class CONFIG_IO:
    @staticmethod
    def read_value(path, key, default=None):
        try:
            with open(path, "r", encoding="utf-8") as f:
                for line in f:
                    if "=" not in line:
                        continue

                    k, v = line.strip().split("=", 1)

                    if k == key:
                        if v == "True":
                            return True
                        if v == "False":
                            return False
                        return v

        except FileNotFoundError:
            pass

        return default
