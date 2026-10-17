# spintronics-sim

Spintronics simulator: STT-MTJ switching via the
Landau-Lifshitz-Gilbert equation with Slonczewski spin-transfer
torque.

## The honest verdict

Spintronics is a **memory technology**, not a logic technology.
Comparing it to CMOS switches is apples-to-oranges.

| Operation | Energy |
|---|---|
| Landauer limit | 2.87 zJ |
| Adiabatic CMOS switch | 2.45 aJ |
| CMOS switch (7nm) | 245 aJ |
| Thermal minimum (40 kT) | 0.17 aJ |
| MRAM read | 20 fJ |
| MRAM write | 200 fJ |
| Spintronic logic (research) | 1 fJ |

**Per-operation:** spintronics is 4-800x worse than CMOS.
**Per-bit-stored-and-retained:** spintronics wins, because SRAM
is volatile and flash wears out at 10^5 cycles.

## Physics

- LLG equation with Slonczewski STT term
- Perpendicular magnetic anisotropy (CoFeB/MgO/CoFeB)
- Realistic parameters: Ms=1000 kA/m, t=1.3 nm, alpha=0.01
- Thermal stability: Delta = E_barrier / kT > 60

## Install

    pip install -e .

## CLI

    spintronics-sim mtj              # device properties
    spintronics-sim switch           # switching dynamics
    spintronics-sim audit            # energy comparison

## Tests

    pytest tests/ -v

## License

Apache 2.0
