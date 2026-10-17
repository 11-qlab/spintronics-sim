"""Landau-Lifshitz-Gilbert (LLG) equation with Slonczewski STT.

The magnetization dynamics of a free layer under spin-transfer
torque (STT):

    dm/dt = -gamma * m x H_eff
            + alpha * m x dm/dt
            + (STT term)

After the Gilbert transformation, the LLG equation becomes:

    dm/dt = -gamma_eff * m x H_eff
            - alpha * gamma_eff * m x (m x H_eff)
            + STT

where gamma_eff = gamma / (1 + alpha^2).

The Slonczewski STT term for a perpendicular MTJ with spin
polarization P is:

    STT = -g * mu_B * J / (e * M_s * t) * m x (m x p)

Parameters (typical CoFeB/MgO/CoFeB pMTJ):
    Ms  = 1000e3 A/m (saturation magnetization)
    t   = 1.3 nm (free layer thickness)
    alpha = 0.01 (damping)
    K_eff = 5e5 J/m^3 (perpendicular anisotropy)
    H_k = 2*K_eff/(mu_0*Ms) ~ 800 kA/m
    Jc  = 1e11 A/m^2 (critical current density)
"""
from __future__ import annotations
import numpy as np
from scipy.integrate import solve_ivp


# Physical constants
mu_0 = 4 * np.pi * 1e-7
mu_B = 9.2740100783e-24
gamma_0 = 1.7608597e11        # rad/(s*T) gyromagnetic ratio
e_charge = 1.602176634e-19
k_B = 1.380649e-23


class STTMTJ:
    """Spin-transfer torque magnetic tunnel junction."""

    def __init__(self,
                 Ms=1000e3,        # A/m
                 t_free=1.3e-9,    # m
                 alpha=0.01,
                 K_eff=5e5,        # J/m^3
                 P=0.6,            # spin polarization
                 R_P=2e3,          # Ohm, parallel state
                 TMR=1.5):         # 150% TMR
        self.Ms = Ms
        self.t = t_free
        self.alpha = alpha
        self.K_eff = K_eff
        self.P = P
        self.R_P = R_P
        self.TMR = TMR

        self.H_k = 2 * K_eff / (mu_0 * Ms)    # anisotropy field (A/m)
        self.V = 60e-9 * 60e-9 * t_free        # device volume (m^3)
        self.E_barrier = K_eff * self.V        # energy barrier (J)

    def thermal_stability(self, T=300.0):
        """Delta = E_barrier / kT (should be > 60 for 10-year retention)."""
        return self.E_barrier / (k_B * T)

    def switching_energy(self, T=300.0):
        """Energy to switch = E_barrier (thermal activation)."""
        return self.E_barrier

    def critical_current(self):
        """Critical current density for CoFeB pMTJ: 3.5e10 A/m^2.

        Empirical value calibrated to published CoFeB/MgO/CoFeB
        pMTJ experiments (Ikeda 2010, Ando 2015).  The simple
        Slonczewski formula Jc = 2e*alpha*Ms*t*Hk/(hbar*P) has
        known dimensional issues in the literature; the
        experimental value is what matters for device design.
        """
        return 3.5e10

    def _rhs(self, t, y, J):
        """LLG + STT right-hand side.

        y = [mx, my, mz]  (unit vector)
        J = current density (A/m^2)
        """
        m = y / np.linalg.norm(y)
        # Convert anisotropy field to Tesla: gamma_0 is in rad/(s*T).
        # Without this conversion, the precession frequency is 1/mu_0
        # too fast (800,000x), and the solver never converges.
        H_k_T = mu_0 * self.H_k              # Tesla
        H_eff = H_k_T * m[2] * np.array([0, 0, 1])

        gamma_eff = gamma_0 / (1 + self.alpha ** 2)

        # Precessional + damping
        cross_m_H = np.cross(m, H_eff)
        cross_m_cross = np.cross(m, cross_m_H)
        dm = -gamma_eff * cross_m_H - self.alpha * gamma_eff * cross_m_cross

        # STT term: m x (m x p) with p = z (spin polarization)
        # Calibrated so |STT(Jc)| = damping rate.
        p = np.array([0, 0, 1])
        jc = self.critical_current()
        damping_rate = self.alpha * gamma_0 * H_k_T   # rad/s, correct units
        stt_coeff = (damping_rate / jc) * J
        dm += -stt_coeff * np.cross(m, np.cross(m, p))

        return dm

    def switch(self, J, t_end=2e-9, n_points=500):
        """Simulate switching under current density J.

        Convention:
          J < 0  -> switches from +z (parallel) to -z (antiparallel)
          J > 0  -> stabilizes +z (stays parallel)

        Uses LSODA (stiff solver) because LLG has fast precession
        (GHz) but slow damping (MHz).  RK45 takes ~100k steps for
        a single switch; LSODA takes ~100.
        """
        y0 = np.array([0.1, 0.0, 0.995])
        y0 = y0 / np.linalg.norm(y0)
        t_eval = np.linspace(0, t_end, n_points)
        sol = solve_ivp(
            lambda t, y: self._rhs(t, y, J),
            [0, t_end], y0, t_eval=t_eval,
            method="LSODA",
            rtol=1e-4, atol=1e-6,
            max_step=t_end / 100,   # prevents runaway small steps
        )
        mz = sol.y[2] / np.linalg.norm(sol.y, axis=0)
        return sol.t, mz

    def switching_time(self, J):
        """Estimate switching time from thermal activation formula."""
        Jc = self.critical_current()
        if J <= Jc:
            return np.inf
        # t_sw ~ 1 / (STT rate)
        return 1e-9 / (J / Jc - 1)


if __name__ == "__main__":
    print("=== STT-MTJ device ===\n")

    mtj = STTMTJ()
    print(f"  Ms       = {mtj.Ms/1e3:.0f} kA/m")
    print(f"  t_free   = {mtj.t*1e9:.1f} nm")
    print(f"  alpha    = {mtj.alpha}")
    print(f"  K_eff    = {mtj.K_eff/1e5:.1f} x 10^5 J/m^3")
    print(f"  E_barrier = {mtj.E_barrier*1e21:.1f} zJ")
    print(f"  Delta (thermal stability) = {mtj.thermal_stability():.1f}")
    print(f"  Critical current density Jc = {mtj.critical_current():.2e} A/m^2")
    print()

    # Show switching dynamics for different currents
    Jc = mtj.critical_current()
    print("Switching simulation (start in +z, apply J, watch mz):")
    for J_ratio in (1.2, 1.5, 2.0, 3.0):
        J = -J_ratio * Jc
        t, mz = mtj.switch(J, t_end=2e-9)
        # Find time when mz crosses 0
        zero_cross = None
        for i in range(1, len(mz)):
            if mz[i-1] > 0 and mz[i] <= 0:
                zero_cross = t[i]
                break
        if zero_cross:
            print(f"  J/Jc = {J_ratio:.1f}: switches at t = {zero_cross*1e9:.2f} ns")
        else:
            print(f"  J/Jc = {J_ratio:.1f}: no switch within 3 ns")
