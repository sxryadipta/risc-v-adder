`timescale 1ns/1ps

module tb_waveform;
    reg  [7:0] a, b;
    reg        cin;
    wire [7:0] sum_rca, sum_cla, sum_bka;
    wire       cout_rca, cout_cla, cout_bka;

    rca_8bit RCA(.a(a), .b(b), .cin(cin), .sum(sum_rca), .cout(cout_rca));
    cla_8bit CLA(.a(a), .b(b), .cin(cin), .sum(sum_cla), .cout(cout_cla));
    bka_8bit BKA(.a(a), .b(b), .cin(cin), .sum(sum_bka), .cout(cout_bka));

    initial begin
        $dumpfile("waveform.vcd");
        $dumpvars(0, tb_waveform);

        a = 8'd0;   b = 8'd0;   cin = 0; #10;
        a = 8'd15;  b = 8'd17;  cin = 0; #10;
        a = 8'd255; b = 8'd1;   cin = 0; #10;   // triggers carry-out
        a = 8'd128; b = 8'd127; cin = 0; #10;
        a = 8'd170; b = 8'd85;  cin = 0; #10;   // alternating bit pattern
        a = 8'd200; b = 8'd100; cin = 1; #10;
        a = 8'd255; b = 8'd255; cin = 1; #10;   // max overflow case
        a = 8'd1;   b = 8'd1;   cin = 0; #10;

        $finish;
    end
endmodule