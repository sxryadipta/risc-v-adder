"""Arbitrary-width RCA / CLA / Brent-Kung emitters.
Convention: module <type>_w<N>(input [N-1:0] a,b; input cin; output [N-1:0] sum; output cout)
RCA instantiates full_adder(a,b,cin,sum,cout) (rtl/ref/full_adder.v)."""

FULL_ADDER = """module full_adder(input a, input b, input cin, output sum, output cout);
    assign sum  = a ^ b ^ cin;
    assign cout = (a & b) | (cin & (a ^ b));
endmodule
"""

def _hdr(kind, n):
    return (f"module {kind}_w{n}(input [{n-1}:0] a, input [{n-1}:0] b, input cin,\n"
            f"    output [{n-1}:0] sum, output cout);\n")

def rca(n):
    s = _hdr("rca", n) + f"    wire [{n}:0] c;\n    assign c[0] = cin;\n"
    for i in range(n):
        s += f"    full_adder fa{i}(.a(a[{i}]), .b(b[{i}]), .cin(c[{i}]), .sum(sum[{i}]), .cout(c[{i+1}]));\n"
    return s + f"    assign cout = c[{n}];\nendmodule\n"

def _pg(n):
    return (f"    wire [{n-1}:0] p = a ^ b;\n    wire [{n-1}:0] g = a & b;\n")

def cla(n):
    """Flat lookahead: c[i+1] = g[i] | p[i]g[i-1] | ... | p[i]..p[0]cin (single-level SOP)."""
    s = _hdr("cla", n) + _pg(n) + f"    wire [{n}:0] c;\n    assign c[0] = cin;\n"
    for i in range(n):
        terms = []
        for j in range(i, -1, -1):  # g[j] with p[i..j+1]
            t = [f"p[{k}]" for k in range(i, j, -1)] + [f"g[{j}]"]
            terms.append(" & ".join(t))
        terms.append(" & ".join([f"p[{k}]" for k in range(i, -1, -1)] + ["cin"]))
        s += f"    assign c[{i+1}] = " + "\n        | ".join(terms) + ";\n"
    s += f"    assign sum = p ^ c[{n-1}:0];\n    assign cout = c[{n}];\nendmodule\n"
    return s

def bka(n):
    """General Brent-Kung prefix tree over M=n+1 nodes; node 0 = (G=cin, P=0)."""
    M = n + 1
    s = _hdr("bka", n) + _pg(n)
    G = ["cin"] + [f"g[{i}]" for i in range(n)]
    P = [None] + [f"p[{i}]" for i in range(n)]
    cnt = [0]
    def combine(hi, lo):
        k = cnt[0]; cnt[0] += 1
        nonlocal s
        s += f"    wire gg{k} = {G[hi]} | ({P[hi]} & {G[lo]});\n"
        G[hi] = f"gg{k}"
        if P[lo] is not None:
            s += f"    wire pp{k} = {P[hi]} & {P[lo]};\n"
            P[hi] = f"pp{k}"
        else:
            P[hi] = None
    d = 1
    while 2 * d <= M:                       # up-sweep
        for i in range(2 * d - 1, M, 2 * d):
            combine(i, i - d)
        d *= 2
    d //= 2
    while d >= 1:                           # down-sweep
        d_ = d
        for i in range(3 * d_ - 1, M, 2 * d_):
            combine(i, i - d_)
        d //= 2
    s += f"    wire [{n}:0] c;\n"
    for j in range(M):
        s += f"    assign c[{j}] = {G[j]};\n"
    s += f"    assign sum = p ^ c[{n-1}:0];\n    assign cout = c[{n}];\nendmodule\n"
    return s

EMIT = {"R": ("rca", rca), "C": ("cla", cla), "B": ("bka", bka)}
