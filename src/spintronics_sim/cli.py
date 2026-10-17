"""CLI for spintronics-sim."""
import argparse, sys
from .llg import STTMTJ
from .energy_audit import compare_all, thermal_switching_energy


def main(argv=None):
    p = argparse.ArgumentParser(prog="spintronics-sim",
        description="Spintronics simulator (STT-MTJ)")
    sub = p.add_subparsers(dest="cmd", required=True)

    pm = sub.add_parser("mtj", help="MTJ device properties")
    pm.add_argument("--Ms", type=float, default=1000e3)
    pm.add_argument("--t", type=float, default=1.3e-9)
    pm.add_argument("--alpha", type=float, default=0.01)

    ps = sub.add_parser("switch", help="Switching simulation")
    ps.add_argument("--J_ratio", type=float, nargs="+",
                    default=[1.2, 1.5, 2.0, 3.0])
    ps.add_argument("--t_end", type=float, default=2e-9)

    pa = sub.add_parser("audit", help="Energy comparison")

    args = p.parse_args(argv)

    if args.cmd == "mtj":
        mtj = STTMTJ(Ms=args.Ms, t_free=args.t, alpha=args.alpha)
        print(f"STT-MTJ (CoFeB/MgO/CoFeB):")
        print(f"  Ms         = {mtj.Ms/1e3:.0f} kA/m")
        print(f"  t_free     = {mtj.t*1e9:.1f} nm")
        print(f"  alpha      = {mtj.alpha}")
        print(f"  E_barrier  = {mtj.E_barrier*1e21:.1f} zJ")
        print(f"  Delta      = {mtj.thermal_stability():.1f}")
        print(f"  H_k        = {mtj.H_k/1e3:.0f} kA/m")
        print(f"  Jc         = {mtj.critical_current():.2e} A/m^2")
        return 0

    if args.cmd == "switch":
        mtj = STTMTJ()
        Jc = mtj.critical_current()
        print(f"Switching from +z (Jc = {Jc:.2e} A/m^2, t_end = {args.t_end*1e9:.1f} ns):")
        print(f"Negative J switches to -z:")
        for ratio in args.J_ratio:
            J = -ratio * Jc
            t, mz = mtj.switch(J, t_end=args.t_end)
            zero_cross = None
            for i in range(1, len(mz)):
                if mz[i-1] > 0 and mz[i] <= 0:
                    zero_cross = t[i]
                    break
            if zero_cross:
                print(f"  J/Jc = {ratio:.1f}: t_sw = {zero_cross*1e9:.2f} ns")
            else:
                print(f"  J/Jc = {ratio:.1f}: no switch in {args.t_end*1e9:.1f} ns")
        return 0

    if args.cmd == "audit":
        r = compare_all()
        print(f"{'operation':<30s} {'energy':>14s} {'vs CMOS':>10s}")
        print("-" * 56)
        print(f"{'Adiabatic CMOS':<30s} {r['adiabatic_J']*1e18:>12.2f} aJ "
              f"{r['adiabatic_J']/r['cmos_J']:>10.4f}")
        print(f"{'CMOS 7nm':<30s} {r['cmos_J']*1e18:>12.2f} aJ {1.0:>10.4f}")
        print(f"{'Spintronic logic (research)':<30s} {r['spin_logic_J']*1e18:>12.2f} aJ "
              f"{r['spin_logic_J']/r['cmos_J']:>10.2f}")
        print(f"{'Thermal minimum (40 kT)':<30s} {r['thermal_minimum_J']*1e18:>12.2f} aJ "
              f"{r['thermal_minimum_J']/r['cmos_J']:>10.2f}")
        print(f"{'MRAM read':<30s} {r['mram_read_J']*1e18:>12.2f} aJ "
              f"{r['mram_read_J']/r['cmos_J']:>10.2f}")
        print(f"{'MRAM write':<30s} {r['mram_write_J']*1e18:>12.2f} aJ "
              f"{r['mram_write_J']/r['cmos_J']:>10.2f}")
        return 0
    return 1


if __name__ == "__main__":
    sys.exit(main())
