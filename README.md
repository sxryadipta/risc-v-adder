# Automated Design Optimization of Hybrid Adders for RISC-V Processors
Group 10, ECE, PEC Chandigarh — Atinder Singh, Yash Kandoi, Suryadipta Ghosh. Supervisor: Dr. Jasbir Kaur.

## Layout
- `generator/` – `adders.py` (arbitrary-width RCA/CLA/Brent-Kung emitters), `hybrid.py` (segment chaining, config enumeration/naming), `tbgen.py` (self-checking testbench generator)
- `rtl/ref/` – original hand-written 8-bit reference adders (cross-check only); `rtl/generated/` – generated (gitignored)
- `tb/` – original testbenches; `tb/generated/` (gitignored)
- `scripts/` – `unit_test_emitters.py`, `run_all.py` (batch runner); `results/` – CSVs

## Conventions
Segment modules: `rca_w<N>`, `cla_w<N>`, `bka_w<N>` with `(a[N-1:0], b[N-1:0], cin, sum[N-1:0], cout)`.
Config name = segments LSB-first, `<width><R|C|B>` joined by `-`, e.g. `3R-2C-3B` (top module `hyb_3R_2C_3B`); `cout` of each segment feeds the next `cin`.
Enumeration: contiguous compositions, ≤4 segments, min width 2 (defaults), adjacent RCA-RCA dropped (identical to one wider RCA). N=8 → 235 configs.
BKA: general Brent-Kung prefix tree over N+1 nodes, with `cin` as node 0.

## Run
`make all` (emitter unit tests + all 8-bit configs, exhaustive 2^17 vectors each) → `results/functional_n8.csv`, `results/passing_n8.csv`.
`make n16` – 16-bit configs: corner cases + constrained-random (seeded, deterministic). Requires Icarus Verilog, Python 3 + pandas.

## Status
G1 (8-bit refs) ✔ · G2 generator ✔ · G3 verification ✔ (N=8). Next: Yosys/OpenSTA/Sky130 PPA, NSGA-II, Pareto plots.
