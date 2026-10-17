"""Spintronics: STT-MTJ switching and energy accounting."""
from .llg import STTMTJ, gamma_0, mu_B, k_B
from .energy_audit import (
    thermal_switching_energy, mram_energy_per_bit, compare_all,
    E_CMOS_J, E_ADIABATIC_J, E_LANDAUER_J,
    E_MRAM_WRITE_J, E_MRAM_READ_J, E_SPIN_LOGIC_J,
)

__version__ = "0.1.0"
__all__ = [
    "STTMTJ", "gamma_0", "mu_B", "k_B",
    "thermal_switching_energy", "mram_energy_per_bit", "compare_all",
    "E_CMOS_J", "E_ADIABATIC_J", "E_LANDAUER_J",
    "E_MRAM_WRITE_J", "E_MRAM_READ_J", "E_SPIN_LOGIC_J",
]
