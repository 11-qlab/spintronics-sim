"""Tests for spintronics simulator."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
import numpy as np
import pytest


def test_mtj_thermal_stability():
    """Standard pMTJ should have Delta > 40 (10-year retention)."""
    from spintronics_sim import STTMTJ
    mtj = STTMTJ()
    assert mtj.thermal_stability() > 40


def test_critical_current_positive():
    from spintronics_sim import STTMTJ
    mtj = STTMTJ()
    assert mtj.critical_current() > 0


def test_switching_above_Jc():
    """Switching occurs above critical current (write-1: +z -> -z)."""
    from spintronics_sim import STTMTJ
    mtj = STTMTJ()
    Jc = mtj.critical_current()
    # Negative current switches from +z (parallel) to -z (antiparallel)
    t, mz = mtj.switch(-2 * Jc, t_end=2e-9)
    assert mz[0] > 0.9
    assert mz[-1] < -0.5   # switched to -z


def test_no_switching_below_Jc():
    """Below critical current, magnetization stays in +z."""
    from spintronics_sim import STTMTJ
    mtj = STTMTJ()
    Jc = mtj.critical_current()
    t, mz = mtj.switch(-0.5 * Jc, t_end=2e-9)
    assert np.all(mz > 0.5)   # stays in +z


def test_thermal_switching_energy():
    """40 kT at 300 K is ~100 zJ (0.1 aJ)."""
    from spintronics_sim import thermal_switching_energy
    E = thermal_switching_energy()
    assert 1e-19 < E < 1e-18   # 0.1-1 aJ range


def test_mram_write_above_adiabatic():
    """MRAM write is much higher than adiabatic CMOS per switch."""
    from spintronics_sim import E_MRAM_WRITE_J, E_ADIABATIC_J
    assert E_MRAM_WRITE_J > 100 * E_ADIABATIC_J


def test_compare_all_fields():
    from spintronics_sim import compare_all
    r = compare_all()
    assert "mram_write_J" in r
    assert "spin_logic_J" in r
    assert "adiabatic_J" in r
    assert r["mram_vs_adiabatic"] > 1.0
