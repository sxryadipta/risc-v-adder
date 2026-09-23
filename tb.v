`timescale 1ns/1ps
module tb;
    reg  [7:0] a, b;
    reg        cin;
    wire [7:0] sum_rca, sum_cla, sum_bka;
    wire       cout_rca, cout_cla, cout_bka;
    integer errors_rca, errors_cla, errors_bka;
    integer count;
    integer ai, bi, ci;
    reg [8:0] expected;

    rca8 U_RCA(.a(a), .b(b), .cin(cin), .sum(sum_rca), .cout(cout_rca));
    cla8 U_CLA(.a(a), .b(b), .cin(cin), .sum(sum_cla), .cout(cout_cla));
    bka8 U_BKA(.a(a), .b(b), .cin(cin), .sum(sum_bka), .cout(cout_bka));

    initial begin
        errors_rca = 0; errors_cla = 0; errors_bka = 0; count = 0;
        for (ai = 0; ai < 256; ai = ai + 1) begin
            for (bi = 0; bi < 256; bi = bi + 1) begin
                for (ci = 0; ci < 2; ci = ci + 1) begin
                    a = ai; b = bi; cin = ci;
                    #1;
                    expected = a + b + cin;
                    count = count + 1;
                    if ({cout_rca, sum_rca} !== expected) errors_rca = errors_rca + 1;
                    if ({cout_cla, sum_cla} !== expected) errors_cla = errors_cla + 1;
                    if ({cout_bka, sum_bka} !== expected) errors_bka = errors_bka + 1;
                end
            end
        end
        $display("========================================================");
        $display(" EXHAUSTIVE FUNCTIONAL VERIFICATION -- 8-bit ADDERS");
        $display(" Golden reference model: sum = a + b + cin (behavioral)");
        $display("========================================================");
        $display(" Total test vectors per adder : %0d", count);
        $display(" RCA8  (Ripple Carry Adder)   : %0d errors", errors_rca);
        $display(" CLA8  (Carry Lookahead Adder): %0d errors", errors_cla);
        $display(" BKA8  (Brent-Kung Adder)     : %0d errors", errors_bka);
        $display("--------------------------------------------------------");
        if (errors_rca==0 && errors_cla==0 && errors_bka==0)
            $display(" RESULT: ALL THREE BASELINE ADDERS PASS (0 mismatches)");
        else
            $display(" RESULT: FAILURES DETECTED -- see counts above");
        $display("========================================================");
        $finish;
    end
endmodule
