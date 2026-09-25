`timescale 1ns/1ps

module tb_adders;
    reg  [7:0] a, b;
    reg        cin;
    wire [7:0] sum_rca, sum_cla, sum_bka;
    wire       cout_rca, cout_cla, cout_bka;

    rca_8bit RCA(.a(a), .b(b), .cin(cin), .sum(sum_rca), .cout(cout_rca));
    cla_8bit CLA(.a(a), .b(b), .cin(cin), .sum(sum_cla), .cout(cout_cla));
    bka_8bit BKA(.a(a), .b(b), .cin(cin), .sum(sum_bka), .cout(cout_bka));

    integer i, j, k;
    integer vectors = 0;
    integer errors_rca = 0, errors_cla = 0, errors_bka = 0;
    reg [8:0] expected;

    initial begin
        for (i = 0; i < 256; i = i + 1) begin
            for (j = 0; j < 256; j = j + 1) begin
                for (k = 0; k < 2; k = k + 1) begin
                    a = i[7:0];
                    b = j[7:0];
                    cin = k[0];
                    #1;

                    expected = a + b + cin;
                    vectors  = vectors + 1;

                    if ({cout_rca, sum_rca} !== expected) begin
                        errors_rca = errors_rca + 1;
                        if (errors_rca <= 5)
                            $display("RCA MISMATCH: a=%0d b=%0d cin=%0d got=%0d exp=%0d",
                                      a, b, cin, {cout_rca, sum_rca}, expected);
                    end
                    if ({cout_cla, sum_cla} !== expected) begin
                        errors_cla = errors_cla + 1;
                        if (errors_cla <= 5)
                            $display("CLA MISMATCH: a=%0d b=%0d cin=%0d got=%0d exp=%0d",
                                      a, b, cin, {cout_cla, sum_cla}, expected);
                    end
                    if ({cout_bka, sum_bka} !== expected) begin
                        errors_bka = errors_bka + 1;
                        if (errors_bka <= 5)
                            $display("BKA MISMATCH: a=%0d b=%0d cin=%0d got=%0d exp=%0d",
                                      a, b, cin, {cout_bka, sum_bka}, expected);
                    end
                end
            end
        end

        $display("==========================================");
        $display("Total vectors tested : %0d", vectors);
        $display("RCA errors : %0d (%s)", errors_rca, (errors_rca==0) ? "PASS" : "FAIL");
        $display("CLA errors : %0d (%s)", errors_cla, (errors_cla==0) ? "PASS" : "FAIL");
        $display("BKA errors : %0d (%s)", errors_bka, (errors_bka==0) ? "PASS" : "FAIL");
        $display("==========================================");
        $finish;
    end
endmodule