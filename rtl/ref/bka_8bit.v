module bka_8bit(
    input  wire [7:0] a, b,
    input  wire        cin,
    output wire [7:0] sum,
    output wire        cout
);
    wire [7:0] g, p;
    assign g = a & b;
    assign p = a ^ b;

    wire g0_eff = g[0] | (p[0] & cin);

    wire G1_0, P1_0, G3_2, P3_2, G5_4, P5_4, G7_6, P7_6;
    assign G1_0 = g[1] | (p[1] & g0_eff);   assign P1_0 = p[1] & p[0];
    assign G3_2 = g[3] | (p[3] & g[2]);     assign P3_2 = p[3] & p[2];
    assign G5_4 = g[5] | (p[5] & g[4]);     assign P5_4 = p[5] & p[4];
    assign G7_6 = g[7] | (p[7] & g[6]);     assign P7_6 = p[7] & p[6];

    wire G3_0, P3_0, G7_4, P7_4;
    assign G3_0 = G3_2 | (P3_2 & G1_0);   assign P3_0 = P3_2 & P1_0;
    assign G7_4 = G7_6 | (P7_6 & G5_4);   assign P7_4 = P7_6 & P5_4;

    wire G7_0, P7_0;
    assign G7_0 = G7_4 | (P7_4 & G3_0);   assign P7_0 = P7_4 & P3_0;

    wire G2_0, P2_0, G4_0, P4_0, G5_0, P5_0;
    assign G2_0 = g[2] | (p[2] & G1_0);   assign P2_0 = p[2] & P1_0;
    assign G4_0 = g[4] | (p[4] & G3_0);   assign P4_0 = p[4] & P3_0;
    assign G5_0 = G5_4 | (P5_4 & G3_0);   assign P5_0 = P5_4 & P3_0;

    wire G6_0, P6_0;
    assign G6_0 = g[6] | (p[6] & G5_0);   assign P6_0 = p[6] & P5_0;

    assign sum[0] = p[0] ^ cin;
    assign sum[1] = p[1] ^ g0_eff;
    assign sum[2] = p[2] ^ G1_0;
    assign sum[3] = p[3] ^ G2_0;
    assign sum[4] = p[4] ^ G3_0;
    assign sum[5] = p[5] ^ G4_0;
    assign sum[6] = p[6] ^ G5_0;
    assign sum[7] = p[7] ^ G6_0;
    assign cout   = G7_0;
endmodule