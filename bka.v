// 8-bit Brent-Kung parallel-prefix adder
module bka8 (
    input  [7:0] a,
    input  [7:0] b,
    input        cin,
    output [7:0] sum,
    output       cout
);
    wire [7:0] g0, p0;
    assign g0 = a & b;
    assign p0 = a ^ b;

    // Level 1 (stride 1): pairs (1,0)(3,2)(5,4)(7,6)
    wire g1_1,p1_1, g1_3,p1_3, g1_5,p1_5, g1_7,p1_7;
    assign g1_1 = g0[1] | (p0[1] & g0[0]); assign p1_1 = p0[1] & p0[0];
    assign g1_3 = g0[3] | (p0[3] & g0[2]); assign p1_3 = p0[3] & p0[2];
    assign g1_5 = g0[5] | (p0[5] & g0[4]); assign p1_5 = p0[5] & p0[4];
    assign g1_7 = g0[7] | (p0[7] & g0[6]); assign p1_7 = p0[7] & p0[6];

    // Level 2 (stride 2): combine (3:0) and (7:4)
    wire g2_3,p2_3, g2_7,p2_7;
    assign g2_3 = g1_3 | (p1_3 & g1_1); assign p2_3 = p1_3 & p1_1;
    assign g2_7 = g1_7 | (p1_7 & g1_5); assign p2_7 = p1_7 & p1_5;

    // Level 3 (stride 4): combine (7:0)
    wire g3_7;
    assign g3_7 = g2_7 | (p2_7 & g2_3);

    // Carries (with cin folded in)
    wire c0,c1,c2,c3,c4,c5,c6,c7,c8;
    assign c0 = cin;
    assign c1 = g0[0] | (p0[0] & c0);
    assign c2 = g1_1 | (p1_1 & c0);
    assign c3 = g0[2] | (p0[2] & c2);
    assign c4 = g2_3 | (p2_3 & c0);
    assign c5 = g0[4] | (p0[4] & c4);
    assign c6 = g1_5 | (p1_5 & c4);
    assign c7 = g0[6] | (p0[6] & c6);
    assign c8 = g3_7 | ((p2_7 & p2_3) & c0);

    assign sum = p0 ^ {c7,c6,c5,c4,c3,c2,c1,c0};
    assign cout = c8;
endmodule
