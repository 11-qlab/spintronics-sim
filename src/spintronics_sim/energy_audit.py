"""Spintronics energy audit vs CMOS and adiabatic.

Reference (from adiabatic-sim):
  CMOS per switch:     245 aJ
  Adiabatic (100 ps):  2.45 aJ
  Landauer limit:      2.87 zJ

Spintronics (STT-MTJ) is fundamentally different from logic:
  - It's a NON-VOLATILE memory element, not a logic gate
  - Switching energy = barrier energy (typically 30-60 kT)
  - Write energy is dominated by I^2 R during the current pulse

For MRAM (the shipping commercial technology):
  - Write energy per bit: ~100-500 fJ = 100,000-500,000 aJ
  - Read energy per bit:  ~10-50 fJ = 10,000-50,000 aJ

So a spintronic memory cell is ~1000-2000x the energy per bit of
an adiabatic CMOS switch.  But it does a DIFFERENT job: it stores
a bit persistently.  Comparing it to a logic gate is apples-to-
oranges.

The fair comparison for spintronics is against SRAM (which is
volatile but fast) or against flash (non-volatile but slow and
wears out).

For spintronic LOGIC (which is a research topic, not shipping):
  - Typical demonstrated switching: ~1 fJ per logic operation
  - With 1 ns switching time
  - Room temperature, no cooling
  - So per-operation energy ~1 fJ = 1000 aJ
  - Compared to adiabatic CMOS: 1000/2.45 = 408x worse
  - Compared to CMOS: 1000/245 = 4x worse
"""
from __future__ import annotations
from .llg import STTMTJ, k_B


# Reference energies
E_CMOS_J = 245e-18
E_ADIABATIC_J = 2.45e-18
E_LANDAUER_J = 2.87e-21

# Spintronic write energies (from MRAM datasheets and published papers)
E_MRAM_WRITE_J = 200e-15     # 200 fJ per write
E_MRAM_READ_J = 20e-15       # 20 fJ per read
E_SPIN_LOGIC_J = 1e-15       # 1 fJ per logic operation (research)
E_SPIN_SWITCH_THERMAL_J = 40 * k_B * 300   # 40 kT thermal switching energy


def thermal_switching_energy():
    """Minimum energy to switch an MTJ at 40 kT barrier."""
    return 40 * k_B * 300


def mram_energy_per_bit(operation="write"):
    if operation == "write":
        return E_MRAM_WRITE_J
    return E_MRAM_READ_J


def compare_all():
    """Compare spintronic energies to electronic baselines."""
    return {
        "mram_write_J": E_MRAM_WRITE_J,
        "mram_read_J": E_MRAM_READ_J,
        "spin_logic_J": E_SPIN_LOGIC_J,
        "thermal_minimum_J": thermal_switching_energy(),
        "cmos_J": E_CMOS_J,
        "adiabatic_J": E_ADIABATIC_J,
        "landauer_J": E_LANDAUER_J,
        "mram_vs_cmos": E_MRAM_WRITE_J / E_CMOS_J,
        "mram_vs_adiabatic": E_MRAM_WRITE_J / E_ADIABATIC_J,
        "spin_logic_vs_adiabatic": E_SPIN_LOGIC_J / E_ADIABATIC_J,
    }


if __name__ == "__main__":
    print("=== Spintronics energy audit ===\n")

    print("STT-MTJ device parameters (CoFeB/MgO/CoFeB pMTJ):")
    mtj = STTMTJ()
    print(f"  Barrier energy E = {mtj.E_barrier*1e21:.1f} zJ")
    print(f"  Thermal stability Delta = {mtj.thermal_stability():.1f}")
    print(f"  Minimum thermal switch: 40 kT = {thermal_switching_energy()*1e18:.2f} aJ")
    print()

    print("Energy per operation:")
    print(f"{'operation':<30s} {'energy':>14s} {'vs CMOS':>10s} {'vs adiabatic':>14s}")
    print("-" * 72)

    data = [
        ("Landauer limit", E_LANDAUER_J),
        ("Adiabatic CMOS switch", E_ADIABATIC_J),
        ("CMOS switch (7nm)", E_CMOS_J),
        ("Spintronic logic (research)", E_SPIN_LOGIC_J),
        ("Thermal minimum (40 kT)", thermal_switching_energy()),
        ("MRAM read", E_MRAM_READ_J),
        ("MRAM write", E_MRAM_WRITE_J),
    ]
    for name, E in data:
        ratio_cmos = E / E_CMOS_J
        ratio_adi = E / E_ADIABATIC_J
        print(f"{name:<30s} {E*1e18:>12.3f} aJ "
              f"{ratio_cmos:>10.2f} {ratio_adi:>14.2f}")

    print()
    print("Interpretation:")
    print("  Spintronics is a MEMORY technology, not a logic technology.")
    print("  MRAM write: 200 fJ/bit vs SRAM ~0.5 fJ/bit (400x worse)")
    print("  MRAM read:  20 fJ/bit vs SRAM ~0.1 fJ/bit (200x worse)")
    print()
    print("  But MRAM is NON-VOLATILE. SRAM is volatile, and flash is")
    print("  non-volatile but 1000x slower and wears out.")
    print()
    print("  Spintronic logic at ~1 fJ/operation is:")
    print(f"    {E_SPIN_LOGIC_J/E_CMOS_J:.1f}x worse than CMOS")
    print(f"    {E_SPIN_LOGIC_J/E_ADIABATIC_J:.0f}x worse than adiabatic")
