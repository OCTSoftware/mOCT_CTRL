"""
fileIO.py

Class to control the config file

Created on Feb 20, 2025 by Martin Ahrens
m.ahrens@uni-luebeck.de
"""


class FILEIO:
    @staticmethod
    def read_value(filename, test_name):
        try:
            with open(filename, "r", encoding="utf-8") as file:
                for line in file:
                    line = line.strip()

                    if not line or line.startswith("#"):
                        continue

                    if "=" not in line:
                        continue

                    key, value = line.split("=", 1)

                    if key.strip() == test_name:
                        return value.strip()

        except FileNotFoundError:
            print(f"File {filename} not found.")
            return None

        except OSError as exc:
            print(f"Error reading {filename}: {exc}")
            return None

        return None

    @staticmethod
    def write_value(filename, test_name, value):
        lines = []
        found = False

        try:
            with open(filename, "r", encoding="utf-8") as file:
                lines = file.readlines()

        except FileNotFoundError:
            pass

        with open(filename, "w", encoding="utf-8") as file:
            for line in lines:
                stripped = line.strip()

                if "=" in stripped:
                    key = stripped.split("=", 1)[0].strip()

                    if key == test_name:
                        file.write(f"{test_name} = {value}\n")
                        found = True
                        continue

                file.write(line)

            if not found:
                file.write(f"{test_name} = {value}\n")
