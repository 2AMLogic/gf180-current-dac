// Exhaustive check of dac_digital over all 64 unary codes x 16 binary codes.
// Checks: t_q is the thermometer code of din[9:4], b_q equals din[3:0], both
// appear on the same clock edge (one cycle after din), and the code 15 -> 16
// major carry flips exactly one thermometer line while b_q goes 15 -> 0.
// Design sanity check only; not the item-9 testbench inventory.
`timescale 1ns/1ps
module tb_dac_digital;
    reg         clk = 0;
    reg  [9:0]  din = 0;
    wire [62:0] t_q;
    wire [3:0]  b_q;
    integer     errors = 0;
    integer     k, i;
    reg  [62:0] exp_t;
    reg  [62:0] prev_t;

    dac_digital dut (.clk(clk), .din(din), .t_q(t_q), .b_q(b_q));

    always #5 clk = ~clk;

    initial begin
        prev_t = 0;
        for (k = 0; k < 1024; k = k + 1) begin
            din = k[9:0];
            @(posedge clk);
            #1;
            for (i = 0; i < 63; i = i + 1) exp_t[i] = (k[9:4] > i);
            if (t_q !== exp_t || b_q !== k[3:0]) begin
                errors = errors + 1;
                $display("FAIL code %0d: t_q=%h exp=%h b_q=%h exp=%h", k, t_q, exp_t, b_q, k[3:0]);
            end
            if (k[3:0] == 4'd0 && k >= 16) begin
                // major carry: exactly one new thermometer line, b wrapped to 0
                if ((t_q ^ prev_t) !== (63'd1 << (k[9:4] - 1))) begin
                    errors = errors + 1;
                    $display("FAIL carry at %0d: t flip %h", k, t_q ^ prev_t);
                end
            end
            prev_t = t_q;
        end
        if (errors == 0) $display("PASS: 1024 codes");
        else             $display("FAIL: %0d errors", errors);
        $finish;
    end
endmodule
