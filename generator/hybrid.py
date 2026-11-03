"""Hybrid adder generator + config enumeration.
Config = tuple of (width, type) segments, LSB segment first. Name: "3R-2C-3B"."""
import re
from .adders import EMIT, FULL_ADDER

def name_of(cfg):
    return "-".join(f"{w}{t}" for w, t in cfg)

def parse(name):
    return tuple((int(w), t) for w, t in re.findall(r"(\d+)([RCB])", name))

def verilog_name(cfg):
    return "hyb_" + name_of(cfg).replace("-", "_")

def enumerate_configs(n, max_segs=4, min_w=2, max_w=None, merge_rca=True):
    """All compositions of n (parts in [min_w,max_w], <= max_segs) x type assignments.
    merge_rca: drop configs with adjacent RCA segments (identical to one wider RCA)."""
    max_w = max_w or n
    out = []
    def comps(rem, k):
        if rem == 0: yield (); return
        if k == 0: return
        for w in range(min_w, min(max_w, rem) + 1):
            for rest in comps(rem - w, k - 1):
                yield (w,) + rest
    def types(k):
        if k == 0: yield (); return
        for t in "RCB":
            for rest in types(k - 1): yield (t,) + rest
    for ws in comps(n, max_segs):
        for ts in types(len(ws)):
            if merge_rca and any(a == b == "R" for a, b in zip(ts, ts[1:])): continue
            out.append(tuple(zip(ws, ts)))
    return out

def emit_lib(widths_types):
    return "\n".join(EMIT[t][1](w) for w, t in sorted(set(widths_types), key=lambda x: (x[1], x[0])))

def emit_hybrid(cfg, with_full_adder=True):
    n = sum(w for w, _ in cfg)
    s = (FULL_ADDER + "\n" if with_full_adder else "") + emit_lib(cfg) + "\n"
    s += (f"module {verilog_name(cfg)}(input [{n-1}:0] a, input [{n-1}:0] b, input cin,\n"
          f"    output [{n-1}:0] sum, output cout);\n    wire [{len(cfg)}:0] c;\n    assign c[0] = cin;\n")
    lo = 0
    for i, (w, t) in enumerate(cfg):
        hi = lo + w - 1
        s += (f"    {EMIT[t][0]}_w{w} u{i}(.a(a[{hi}:{lo}]), .b(b[{hi}:{lo}]), .cin(c[{i}]), "
              f".sum(sum[{hi}:{lo}]), .cout(c[{i+1}]));\n")
        lo = hi + 1
    return s + f"    assign cout = c[{len(cfg)}];\nendmodule\n"
