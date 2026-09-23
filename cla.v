module cla8 (
    input  [7:0] a,
    input  [7:0] b,
    input        cin,
    output [7:0] sum,
    output       cout
);
    wire [7:0] g, p;
    wire [8:0] c;
    assign g = a & b;
    assign p = a ^ b;
    assign c[0] = cin;
    genvar i;
    generate
        for (i = 0; i < 8; i = i + 1) begin : cgen
            assign c[i+1] = g[i] | (p[i] & c[i]);
        end
    endgenerate
    assign sum = p ^ c[7:0];
    assign cout = c[8];
endmodule
