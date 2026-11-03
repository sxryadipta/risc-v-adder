"""Generate RTL + testbench per config, simulate with iverilog, write results CSV.
Usage: python3 scripts/run_all.py --n 8 [--max-segs 4 --min-w 2 --jobs 8 --limit K]"""
import argparse, subprocess, sys, pathlib, re, os
from concurrent.futures import ThreadPoolExecutor
import pandas as pd
ROOT = pathlib.Path(__file__).resolve().parents[1]; sys.path.insert(0, str(ROOT))
from generator.hybrid import enumerate_configs, emit_hybrid, name_of, verilog_name
from generator.tbgen import emit_tb

ap = argparse.ArgumentParser()
ap.add_argument("--n", type=int, default=8); ap.add_argument("--max-segs", type=int, default=4)
ap.add_argument("--min-w", type=int, default=2); ap.add_argument("--max-w", type=int, default=None)
ap.add_argument("--jobs", type=int, default=os.cpu_count() or 4); ap.add_argument("--limit", type=int, default=0)
ap.add_argument("--n-random", type=int, default=20000)
a = ap.parse_args()

RTL = ROOT/"rtl/generated"/f"n{a.n}"; TB = ROOT/"tb/generated"/f"n{a.n}"; BLD = ROOT/"build"/f"n{a.n}"
for d in (RTL, TB, BLD): d.mkdir(parents=True, exist_ok=True)
cfgs = enumerate_configs(a.n, a.max_segs, a.min_w, a.max_w)
if a.limit: cfgs = cfgs[:a.limit]

def run(cfg):
    nm = name_of(cfg); vn = verilog_name(cfg)
    (RTL/f"{vn}.v").write_text(emit_hybrid(cfg)); (TB/f"tb_{vn}.v").write_text(emit_tb(cfg, a.n_random))
    exe = BLD/f"{vn}.out"
    c = subprocess.run(["iverilog", "-o", str(exe), str(RTL/f"{vn}.v"), str(TB/f"tb_{vn}.v")], capture_output=True, text=True)
    if c.returncode: return dict(config=nm, status="COMPILE_ERROR", vectors=0, detail=c.stderr[:200])
    out = subprocess.run(["vvp", str(exe)], capture_output=True, text=True).stdout
    exe.unlink(missing_ok=True)
    m = re.search(r"^(PASS|FAIL) \S+ vectors=(\d+)", out, re.M)
    return dict(config=nm, status=m.group(1) if m else "NO_RESULT", vectors=int(m.group(2)) if m else 0,
                detail="" if m and m.group(1) == "PASS" else out[:200].replace("\n", " | "))

with ThreadPoolExecutor(a.jobs) as ex: rows = list(ex.map(run, cfgs))
df = pd.DataFrame(rows)
df["n_bits"] = a.n; df["n_segments"] = df.config.str.count("-") + 1
for t in "RCB": df[f"n_{t}"] = df.config.str.count(rf"\d{t}")
(ROOT/"results").mkdir(exist_ok=True)
df.to_csv(ROOT/"results"/f"functional_n{a.n}.csv", index=False)
df[df.status == "PASS"][["config"]].to_csv(ROOT/"results"/f"passing_n{a.n}.csv", index=False)
print(f"N={a.n}: {len(df)} configs | PASS={(df.status=='PASS').sum()} | non-PASS={(df.status!='PASS').sum()} | vectors/config={df.vectors.max()}")
if (df.status != "PASS").any(): print(df[df.status != "PASS"].head(10).to_string())
