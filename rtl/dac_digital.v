// Digital partition of the current-steering DAC: 6 + 4 segmentation.
// din[9:4] is decoded to 63 thermometer lines; din[3:0] is the binary LSB
// path. Thermometer and binary bits share one retiming register bank on the
// update clock, so every output launches from a flop on the same edge and the
// binary bits arrive in the same cycle as the thermometer lines (decoder
// depth is absorbed by the registers, not by an inserted delay chain, which
// synthesis would remove). Outputs end at the switch-driver inputs.
// Latency: one clk cycle.
module dac_digital (
    input  wire        clk,
    input  wire [9:0]  din,
    output reg  [62:0] t_q,
    output reg  [3:0]  b_q
);
    wire [62:0] t_d;

    thermo_decoder u_dec (.code(din[9:4]), .t(t_d));

    always @(posedge clk) begin
        t_q <= t_d;
        b_q <= din[3:0];
    end
endmodule
