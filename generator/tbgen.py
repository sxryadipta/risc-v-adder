"""Self-checking testbench generator. Exhaustive for N<=8, corner+constrained-random otherwise."""
from .hybrid import verilog_name

def emit_tb(cfg, n_random=20000, seed=12345, exhaustive_max=8):
    n = sum(w for w, _ in cfg)
    dut = verilog_name(cfg)
    s = f"""`timescale 1ns/1ps
module tb;
    reg [{n-1}:0] a, b; reg cin;
    wire [{n-1}:0] sum; wire cout;
    {dut} dut(.a(a), .b(b), .cin(cin), .sum(sum), .cout(cout));
    integer errors = 0, vectors = 0;
    integer i, j, k, seed = {seed};
    reg [{n}:0] expected;
    task check; begin
        #1; expected = a + b + cin; vectors = vectors + 1;
        if ({{cout, sum}} !== expected) begin
            errors = errors + 1;
            if (errors <= 5) $display("MISMATCH a=%h b=%h cin=%b got=%h exp=%h", a, b, cin, {{cout,sum}}, expected);
        end
    end endtask
    initial begin
"""
    if n <= exhaustive_max:
        s += f"""        for (i = 0; i < {1<<n}; i = i + 1)
          for (j = 0; j < {1<<n}; j = j + 1)
            for (k = 0; k < 2; k = k + 1) begin a = i; b = j; cin = k; check; end
"""
    else:
        ones = f"{{{n}{{1'b1}}}}"
        s += f"""        // corner cases
        for (k = 0; k < 2; k = k + 1) begin
            cin = k;
            a = 0; b = 0; check;  a = {ones}; b = 0; check;  a = 0; b = {ones}; check;
            a = {ones}; b = {ones}; check;  a = {ones}; b = 1; check;  a = 1; b = {ones}; check;
            a = {{{(n+1)//2}{{2'b10}}}}; b = {{{(n+1)//2}{{2'b01}}}}; check;   // alternating, full propagate
            a = {{{(n+1)//2}{{2'b01}}}}; b = {{{(n+1)//2}{{2'b10}}}}; check;
            a = {{{(n+1)//2}{{2'b10}}}}; b = {{{(n+1)//2}{{2'b10}}}}; check;
            for (i = 0; i < {n}; i = i + 1) begin   // single-bit / carry-chain starts
                a = 1 << i; b = 1 << i; check;
                a = {ones}; b = 1 << i; check;
                a = ~(1 << i); b = 1 << i; check;
                a = 1 << i; b = 0; check;
            end
            for (i = 0; i < {n}; i = i + 1)         // ripple across every boundary
                for (j = i; j < {n}; j = j + 1) begin
                    a = ({ones} >> ({n}-1-j)) & ~({ones} >> ({n}-i)); b = 1 << i; check;
                end
        end
        // constrained random: uniform + sparse/dense (long carry chains)
        for (i = 0; i < {n_random}; i = i + 1) begin
            a = $random(seed); b = $random(seed); cin = $random(seed);
            case (i % 4)
              1: begin a = a | $random(seed); b = b | $random(seed); end   // dense
              2: begin a = a & $random(seed); b = b & $random(seed); end   // sparse
              3: b = ~a ^ (1 << ($random(seed) & {n-1 if (n & (n-1))==0 else 0}));     // near-propagate
            endcase
            check;
        end
"""
    s += f"""        if (errors == 0) $display("PASS {dut} vectors=%0d", vectors);
        else $display("FAIL {dut} vectors=%0d errors=%0d", vectors, errors);
        $finish;
    end
endmodule
"""
    return s
