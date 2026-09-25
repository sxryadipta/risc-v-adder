module rca_8bit(
    input  wire [7:0] a, b,
    input  wire        cin,
    output wire [7:0] sum,
    output wire        cout
);
    wire [7:0] c;

    full_adder fa0(.a(a[0]), .b(b[0]), .cin(cin), .sum(sum[0]), .cout(c[0]));

    genvar i;
    generate
        for (i = 1; i < 8; i = i + 1) begin : fa_chain
            full_adder fa(.a(a[i]), .b(b[i]), .cin(c[i-1]), .sum(sum[i]), .cout(c[i]));
        end
    endgenerate

    assign cout = c[7];
endmodule