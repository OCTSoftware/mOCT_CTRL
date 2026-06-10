# =========================
# Physical calibration
# =========================

# Stepper:
# 3200 Steps == 1000 um == 1 Rev
#   32 Steps ==   10 µm
STEPS_PER_UM = 32.0 / 10.0

# NI-DAQ:
# 0.25 V = 10 µm
VOLTS_PER_UM = 0.25 / 10.0


def steps_to_um(steps: float) -> float:
    return steps / STEPS_PER_UM


def um_to_steps(um: float) -> int:
    return round(um * STEPS_PER_UM)


def volts_to_um(volts: float) -> float:
    return volts / VOLTS_PER_UM


def um_to_volts(um: float) -> float:
    return um * VOLTS_PER_UM