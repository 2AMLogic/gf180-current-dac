// 6-bit binary to 63-line thermometer decoder (combinational).
// t[i] = (code > i) for i = 0..62: code 0 -> all low, code 63 -> all high.
module thermo_decoder (
    input  wire [5:0]  code,
    output wire [62:0] t
);
    genvar i;
    generate
        for (i = 0; i < 63; i = i + 1) begin : g_t
            assign t[i] = (code > i);
        end
    endgenerate
endmodule
