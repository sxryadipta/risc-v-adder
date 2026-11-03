"""Standalone emitter tests: each of rca/cla/bka at widths 1..8 (exhaustive) and 16 (random),
plus cross-check against rtl/ref 8-bit modules."""
import subprocess, sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from generator.adders import EMIT, FULL_ADDER
ROOT = pathlib.Path(__file__).resolve().parents[1]; B = ROOT / "build" / "unit"; B.mkdir(parents=True, exist_ok=True)

def tb(kind, n):
    loops = (f"for(i=0;i<{1<<n};i=i+1) for(j=0;j<{1<<n};j=j+1) for(k=0;k<2;k=k+1) begin a=i;b=j;cin=k;chk; end"
             if n <= 8 else "for(i=0;i<100000;i=i+1) begin a=$random(sd);b=$random(sd);cin=$random(sd);if(i%3==1)b=~a;chk; end a=-1;b=1;cin=0;chk;a=-1;b=0;cin=1;chk;")
    ref = ""
    if n == 8:
        ref = (f"wire [7:0] rs; wire rc; {'rca' if kind=='rca' else kind}_8bit REF(.a(a),.b(b),.cin(cin),.sum(rs),.cout(rc));\n")
    refchk = "if ({rc,rs} !== {cout,sum}) err=err+1;" if n == 8 else ""
    return f"""module tb; reg [{n-1}:0] a,b; reg cin; wire [{n-1}:0] sum; wire cout; integer i,j,k,err=0,sd=7;
{kind}_w{n} d(.a(a),.b(b),.cin(cin),.sum(sum),.cout(cout)); {ref}
task chk; begin #1; if ({{cout,sum}} !== a+b+cin) err=err+1; {refchk} end endtask
initial begin {loops} if (err==0) $display("PASS"); else $display("FAIL"); $finish; end endmodule"""

bad = 0
for t, (kind, fn) in EMIT.items():
    for n in list(range(1, 9)) + [16]:
        f = B / f"{kind}{n}.v"; f.write_text(FULL_ADDER + fn(n) + tb(kind, n))
        srcs = [str(f)] + ([str(ROOT/"rtl/ref"/f"{kind}_8bit.v")] if n == 8 else [])
        if n == 8 and kind == "rca": srcs = [str(f), str(ROOT/"rtl/ref/rca_8bit.v")]
        # ref rca uses full_adder from rtl/ref; ours defines it already -> exclude ref full_adder.v
        r = subprocess.run(["iverilog", "-o", str(B/"s.out")] + srcs, capture_output=True, text=True)
        out = r.stderr
        if r.returncode == 0:
            out = subprocess.run(["vvp", str(B/"s.out")], capture_output=True, text=True).stdout
        ok = "PASS" in out; bad += not ok
        print(f"{kind}_w{n:<2} {'PASS' if ok else 'FAIL '+out[:200]}")
sys.exit(1 if bad else 0)
