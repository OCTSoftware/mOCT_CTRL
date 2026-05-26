"""Value convesion"""


class StageLogic:
    """Value convesion"""

    def __init__(self):
        self.old_val_prb = 0.0
        self.old_val_ref = 0.0

    # --------------------------------------------------------------------------
    @staticmethod
    def ni_piezo_position_to_voltage(value) -> float:
        """
        Converts stepsize (mm) into voltage for the piezo controller

        Travel distance of the piezo is 0 µm to 400 µm
        Input voltage in the piezo controller is 0 V to 10 V
        """
        return 10 * float(value) / 400

    # --------------------------------------------------------------------------
    @staticmethod
    def ni_piezo_volatage_to_position(value) -> float:
        """
        Converts voltages into tepsize (mm) for the piezo controller

        Travel distance of the piezo is 0 µm to 400 µm
        Input voltage in the piezo controller is 0 V to 10 V
        """
        return float(value) * 400 / 10
