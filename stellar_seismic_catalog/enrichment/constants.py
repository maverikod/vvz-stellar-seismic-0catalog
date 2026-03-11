"""
Solar and physical constants for normalization and derived observables.

Author: Vasiliy Zdanovskiy
email: vasilyvz@gmail.com
"""

import json
from pathlib import Path

# SI and cgs: R_sun (m), M_sun (kg), L_sun (W), T_sun (K)
# Asteroseismic: nu_max_sun (microHz), delta_nu_sun (microHz)
SOLAR_CONSTANTS = {
    "R_sun_m": 6.957e8,
    "M_sun_kg": 1.98847e30,
    "L_sun_W": 3.828e26,
    "T_sun_K": 5772.0,
    "nu_max_sun_microHz": 3090.0,
    "delta_nu_sun_microHz": 135.1,
}

# For dimensionless ratios in catalog (solar units)
R_SUN = 1.0  # Rsun
M_SUN = 1.0  # Msun
L_SUN = 1.0  # Lsun
T_SUN = SOLAR_CONSTANTS["T_sun_K"]
NU_MAX_SUN = SOLAR_CONSTANTS["nu_max_sun_microHz"]
DELTA_NU_SUN = SOLAR_CONSTANTS["delta_nu_sun_microHz"]


def write_constants_json(output_path: str | Path) -> Path:
    """Write SOLAR_CONSTANTS to constants.json. Returns path."""
    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    with open(out, "w", encoding="utf-8") as f:
        json.dump(SOLAR_CONSTANTS, f, indent=2)
    return out


def load_constants_json(path: str | Path) -> dict[str, float]:
    """Load constants from JSON."""
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    return dict(data)
