"""
fileIO.py

Class to control the config file

Created on Feb 20, 2025 by Martin Ahrens
m.ahrens@uni-luebeck.de
"""

class FILEIO:

    def read_value(filename, test_name):
        try:
            with open(filename, 'r') as file:
                for line in file:
                    if line.startswith(test_name):
                        # Split the line by '=' and return the float value
                        return line.split('=')[1].strip()
        except FileNotFoundError:
            print(f"File {filename} not found.")
            return None
        except ValueError:
            print(f"Error in value format for {test_name}.")
            return None

    def write_value(filename, test_name, value):
        lines = []
        found = False

        # Read all lines and check if the test_name already exists
        try:
            with open(filename, 'r') as file:
                lines = file.readlines()

            with open(filename, 'w') as file:
                for line in lines:
                    if line.startswith(test_name):
                        file.write(f"{test_name} = {value}\n")
                        found = True
                    else:
                        file.write(line)

                # If the test_name is not found, add it at the end
                if not found:
                    file.write(f"{test_name} = {value}\n")
                    
        except FileNotFoundError:
            with open(filename, 'w') as file:
                file.write(f"{test_name} = {value}\n")
                print(f"File {filename} not found, creating a new one.")