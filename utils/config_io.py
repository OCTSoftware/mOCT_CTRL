class CONFIG_IO:
    @staticmethod
    def read_value(path, key, default=None):
        try:
            with open(path, "r", encoding="utf-8") as f:
                for line in f:
                    if "=" not in line:
                        continue

                    k, v = [x.strip() for x in line.split("=", 1)]

                    if k == key:
                        if v == "True":
                            return True
                        if v == "False":
                            return False
                        return v

        except FileNotFoundError:
            pass

        return default

    @staticmethod
    def write_value(path, key, value):
        lines = []
        found = False

        try:
            with open(path, "r", encoding="utf-8") as f:
                lines = f.readlines()
        except FileNotFoundError:
            pass

        for i, line in enumerate(lines):
            if "=" in line:
                k, _ = line.strip().split("=", 1)
                if k == key:
                    lines[i] = f"{key}={value}\n"
                    found = True
                    break

        if not found:
            lines.append(f"{key}={value}\n")

        with open(path, "w", encoding="utf-8") as f:
            f.writelines(lines)

    @staticmethod
    def save_runtime_config(app, path):
        try:
            config_path = path

            # nidaq
            if hasattr(app, "nidaq_frame"):
                CONFIG_IO.write_value(
                    config_path, "nidaq_position", app.nidaq_frame.nidaq_position
                )

            # objective selector
            if hasattr(app, "kcube_frame"):
                selected = app.kcube_frame.selected_var.get()

                CONFIG_IO.write_value(config_path, "last_selected", selected)

                if selected in ("05x16", "10x03", "20x05", "40x08"):
                    pos = app.kcube_frame.ctrl.get_position()

                    CONFIG_IO.write_value(config_path, selected, pos)

            # ------------------------------------------------------------------
            # stepper controller
            # ------------------------------------------------------------------
            if hasattr(app, "stepper_controller"):
                driver = app.stepper_controller.driver

                CONFIG_IO.write_value(
                    config_path, "stepper_connected", driver.is_connected
                )

                if hasattr(driver, "sys_state"):
                    CONFIG_IO.write_value(
                        config_path, "stepper_state", driver.sys_state
                    )

                if hasattr(driver, "limits"):
                    CONFIG_IO.write_value(config_path, "stepper_limits", driver.limits)

            # optional UI/runtime state
            if hasattr(app, "stepper_frame"):
                frame = app.stepper_frame

                if hasattr(frame, "selected_port"):
                    CONFIG_IO.write_value(
                        config_path, "stepper_port", frame.selected_port.get()
                    )

                if hasattr(frame, "baudrate_var"):
                    CONFIG_IO.write_value(
                        config_path, "stepper_baudrate", frame.baudrate_var.get()
                    )

        except Exception as e:
            print(f"[config save] failed: {e}")


class CheckConfig:
    load_variables = staticmethod(CONFIG_IO.read_value)
