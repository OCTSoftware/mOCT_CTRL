'''  Load variables from a txt file and check if they are true or false '''


class CheckConfig:
    ''' CheckCOnfig'''

    def __init__(Self) -> None:
        ''' __init__ '''

        pass

# -----------------------------------------------------------------------------
    def load_variables(file_path, var_to_check) -> bool:
        ''' load_variables '''

        variables = {}

        with open(file_path, 'r', encoding="utf-8") as file:
            for line in file:
                # Strip leading/trailing spaces and ignore empty lines or comments
                line = line.strip()
                if line and not line.startswith("#"):
                    # Split the line into the variable name and its value
                    var_name, var_value = line.split('=', 1)
                    var_name = var_name.strip()  # Remove extra spaces around variable name
                    var_value = var_value.strip()  # Remove extra spaces around the value

                    # Store the value in the dictionary
                    if var_value == 'True':
                        variables[var_name] = True
                    elif var_value == 'False':
                        variables[var_name] = False
                    else:
                        variables[var_name] = var_value  # Store as string if not boolean

        # Check if the variable to check exists and return its value, otherwise None
        return variables.get(var_to_check, None)
