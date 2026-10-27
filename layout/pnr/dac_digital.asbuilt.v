module dac_digital (clk,
    b_q,
    din,
    t_q);
 input clk;
 output [3:0] b_q;
 input [9:0] din;
 output [62:0] t_q;

 wire \u_dec/_000_ ;
 wire \u_dec/_001_ ;
 wire \u_dec/_002_ ;
 wire \u_dec/_003_ ;
 wire \u_dec/_004_ ;
 wire clknet_3_3__leaf_clk;
 wire \u_dec/_006_ ;
 wire clknet_3_1__leaf_clk;
 wire clknet_3_2__leaf_clk;
 wire \u_dec/_009_ ;
 wire \u_dec/_010_ ;
 wire \u_dec/_011_ ;
 wire clknet_3_5__leaf_clk;
 wire clknet_3_4__leaf_clk;
 wire \u_dec/_014_ ;
 wire \u_dec/_015_ ;
 wire \u_dec/_016_ ;
 wire \u_dec/_017_ ;
 wire \u_dec/_018_ ;
 wire \u_dec/_019_ ;
 wire \u_dec/_020_ ;
 wire clknet_3_0__leaf_clk;
 wire \u_dec/_022_ ;
 wire clknet_0_clk;
 wire \u_dec/_024_ ;
 wire \u_dec/_025_ ;
 wire \u_dec/_026_ ;
 wire \u_dec/_027_ ;
 wire \u_dec/_028_ ;
 wire \u_dec/_029_ ;
 wire \u_dec/_030_ ;
 wire \u_dec/_031_ ;
 wire \u_dec/_032_ ;
 wire \u_dec/_033_ ;
 wire \u_dec/_034_ ;
 wire \u_dec/_035_ ;
 wire \u_dec/_036_ ;
 wire \u_dec/_037_ ;
 wire clknet_3_6__leaf_clk;
 wire clknet_3_7__leaf_clk;
 wire [62:0] t_d;

 gf180mcu_fd_sc_mcu7t5v0__dffq_1 _00_ (.D(t_d[0]),
    .CLK(clknet_3_2__leaf_clk),
    .Q(t_q[0]));
 gf180mcu_fd_sc_mcu7t5v0__dffq_1 _01_ (.D(t_d[1]),
    .CLK(clknet_3_4__leaf_clk),
    .Q(t_q[1]));
 gf180mcu_fd_sc_mcu7t5v0__dffq_1 _02_ (.D(t_d[2]),
    .CLK(clknet_3_1__leaf_clk),
    .Q(t_q[2]));
 gf180mcu_fd_sc_mcu7t5v0__dffq_1 _03_ (.D(t_d[3]),
    .CLK(clknet_3_2__leaf_clk),
    .Q(t_q[3]));
 gf180mcu_fd_sc_mcu7t5v0__dffq_1 _04_ (.D(t_d[4]),
    .CLK(clknet_3_5__leaf_clk),
    .Q(t_q[4]));
 gf180mcu_fd_sc_mcu7t5v0__dffq_1 _05_ (.D(t_d[5]),
    .CLK(clknet_3_2__leaf_clk),
    .Q(t_q[5]));
 gf180mcu_fd_sc_mcu7t5v0__dffq_1 _06_ (.D(t_d[6]),
    .CLK(clknet_3_4__leaf_clk),
    .Q(t_q[6]));
 gf180mcu_fd_sc_mcu7t5v0__dffq_1 _07_ (.D(t_d[7]),
    .CLK(clknet_3_1__leaf_clk),
    .Q(t_q[7]));
 gf180mcu_fd_sc_mcu7t5v0__dffq_1 _08_ (.D(t_d[8]),
    .CLK(clknet_3_2__leaf_clk),
    .Q(t_q[8]));
 gf180mcu_fd_sc_mcu7t5v0__dffq_1 _09_ (.D(t_d[9]),
    .CLK(clknet_3_2__leaf_clk),
    .Q(t_q[9]));
 gf180mcu_fd_sc_mcu7t5v0__dffq_1 _10_ (.D(t_d[10]),
    .CLK(clknet_3_3__leaf_clk),
    .Q(t_q[10]));
 gf180mcu_fd_sc_mcu7t5v0__dffq_1 _11_ (.D(t_d[11]),
    .CLK(clknet_3_3__leaf_clk),
    .Q(t_q[11]));
 gf180mcu_fd_sc_mcu7t5v0__dffq_1 _12_ (.D(t_d[12]),
    .CLK(clknet_3_0__leaf_clk),
    .Q(t_q[12]));
 gf180mcu_fd_sc_mcu7t5v0__dffq_1 _13_ (.D(t_d[13]),
    .CLK(clknet_3_3__leaf_clk),
    .Q(t_q[13]));
 gf180mcu_fd_sc_mcu7t5v0__dffq_1 _14_ (.D(t_d[14]),
    .CLK(clknet_3_2__leaf_clk),
    .Q(t_q[14]));
 gf180mcu_fd_sc_mcu7t5v0__dffq_1 _15_ (.D(t_d[15]),
    .CLK(clknet_3_1__leaf_clk),
    .Q(t_q[15]));
 gf180mcu_fd_sc_mcu7t5v0__dffq_1 _16_ (.D(t_d[16]),
    .CLK(clknet_3_2__leaf_clk),
    .Q(t_q[16]));
 gf180mcu_fd_sc_mcu7t5v0__dffq_1 _17_ (.D(t_d[17]),
    .CLK(clknet_3_0__leaf_clk),
    .Q(t_q[17]));
 gf180mcu_fd_sc_mcu7t5v0__dffq_1 _18_ (.D(t_d[18]),
    .CLK(clknet_3_3__leaf_clk),
    .Q(t_q[18]));
 gf180mcu_fd_sc_mcu7t5v0__dffq_1 _19_ (.D(t_d[19]),
    .CLK(clknet_3_4__leaf_clk),
    .Q(t_q[19]));
 gf180mcu_fd_sc_mcu7t5v0__dffq_1 _20_ (.D(t_d[20]),
    .CLK(clknet_3_5__leaf_clk),
    .Q(t_q[20]));
 gf180mcu_fd_sc_mcu7t5v0__dffq_1 _21_ (.D(t_d[21]),
    .CLK(clknet_3_2__leaf_clk),
    .Q(t_q[21]));
 gf180mcu_fd_sc_mcu7t5v0__dffq_1 _22_ (.D(t_d[22]),
    .CLK(clknet_3_6__leaf_clk),
    .Q(t_q[22]));
 gf180mcu_fd_sc_mcu7t5v0__dffq_1 _23_ (.D(t_d[23]),
    .CLK(clknet_3_1__leaf_clk),
    .Q(t_q[23]));
 gf180mcu_fd_sc_mcu7t5v0__dffq_1 _24_ (.D(t_d[24]),
    .CLK(clknet_3_5__leaf_clk),
    .Q(t_q[24]));
 gf180mcu_fd_sc_mcu7t5v0__dffq_1 _25_ (.D(t_d[25]),
    .CLK(clknet_3_2__leaf_clk),
    .Q(t_q[25]));
 gf180mcu_fd_sc_mcu7t5v0__dffq_1 _26_ (.D(t_d[26]),
    .CLK(clknet_3_4__leaf_clk),
    .Q(t_q[26]));
 gf180mcu_fd_sc_mcu7t5v0__dffq_1 _27_ (.D(t_d[27]),
    .CLK(clknet_3_7__leaf_clk),
    .Q(t_q[27]));
 gf180mcu_fd_sc_mcu7t5v0__dffq_1 _28_ (.D(t_d[28]),
    .CLK(clknet_3_5__leaf_clk),
    .Q(t_q[28]));
 gf180mcu_fd_sc_mcu7t5v0__dffq_1 _29_ (.D(t_d[29]),
    .CLK(clknet_3_2__leaf_clk),
    .Q(t_q[29]));
 gf180mcu_fd_sc_mcu7t5v0__dffq_1 _30_ (.D(t_d[30]),
    .CLK(clknet_3_7__leaf_clk),
    .Q(t_q[30]));
 gf180mcu_fd_sc_mcu7t5v0__dffq_1 _31_ (.D(din[9]),
    .CLK(clknet_3_4__leaf_clk),
    .Q(t_q[31]));
 gf180mcu_fd_sc_mcu7t5v0__dffq_1 _32_ (.D(t_d[32]),
    .CLK(clknet_3_2__leaf_clk),
    .Q(t_q[32]));
 gf180mcu_fd_sc_mcu7t5v0__dffq_1 _33_ (.D(t_d[33]),
    .CLK(clknet_3_1__leaf_clk),
    .Q(t_q[33]));
 gf180mcu_fd_sc_mcu7t5v0__dffq_1 _34_ (.D(t_d[34]),
    .CLK(clknet_3_3__leaf_clk),
    .Q(t_q[34]));
 gf180mcu_fd_sc_mcu7t5v0__dffq_1 _35_ (.D(t_d[35]),
    .CLK(clknet_3_4__leaf_clk),
    .Q(t_q[35]));
 gf180mcu_fd_sc_mcu7t5v0__dffq_1 _36_ (.D(t_d[36]),
    .CLK(clknet_3_6__leaf_clk),
    .Q(t_q[36]));
 gf180mcu_fd_sc_mcu7t5v0__dffq_1 _37_ (.D(t_d[37]),
    .CLK(clknet_3_0__leaf_clk),
    .Q(t_q[37]));
 gf180mcu_fd_sc_mcu7t5v0__dffq_1 _38_ (.D(t_d[38]),
    .CLK(clknet_3_4__leaf_clk),
    .Q(t_q[38]));
 gf180mcu_fd_sc_mcu7t5v0__dffq_1 _39_ (.D(t_d[39]),
    .CLK(clknet_3_3__leaf_clk),
    .Q(t_q[39]));
 gf180mcu_fd_sc_mcu7t5v0__dffq_1 _40_ (.D(t_d[40]),
    .CLK(clknet_3_0__leaf_clk),
    .Q(t_q[40]));
 gf180mcu_fd_sc_mcu7t5v0__dffq_1 _41_ (.D(t_d[41]),
    .CLK(clknet_3_0__leaf_clk),
    .Q(t_q[41]));
 gf180mcu_fd_sc_mcu7t5v0__dffq_1 _42_ (.D(t_d[42]),
    .CLK(clknet_3_6__leaf_clk),
    .Q(t_q[42]));
 gf180mcu_fd_sc_mcu7t5v0__dffq_1 _43_ (.D(t_d[43]),
    .CLK(clknet_3_6__leaf_clk),
    .Q(t_q[43]));
 gf180mcu_fd_sc_mcu7t5v0__dffq_1 _44_ (.D(t_d[44]),
    .CLK(clknet_3_1__leaf_clk),
    .Q(t_q[44]));
 gf180mcu_fd_sc_mcu7t5v0__dffq_1 _45_ (.D(t_d[45]),
    .CLK(clknet_3_0__leaf_clk),
    .Q(t_q[45]));
 gf180mcu_fd_sc_mcu7t5v0__dffq_1 _46_ (.D(t_d[46]),
    .CLK(clknet_3_6__leaf_clk),
    .Q(t_q[46]));
 gf180mcu_fd_sc_mcu7t5v0__dffq_1 _47_ (.D(t_d[47]),
    .CLK(clknet_3_2__leaf_clk),
    .Q(t_q[47]));
 gf180mcu_fd_sc_mcu7t5v0__dffq_1 _48_ (.D(t_d[48]),
    .CLK(clknet_3_2__leaf_clk),
    .Q(t_q[48]));
 gf180mcu_fd_sc_mcu7t5v0__dffq_1 _49_ (.D(t_d[49]),
    .CLK(clknet_3_5__leaf_clk),
    .Q(t_q[49]));
 gf180mcu_fd_sc_mcu7t5v0__dffq_1 _50_ (.D(t_d[50]),
    .CLK(clknet_3_3__leaf_clk),
    .Q(t_q[50]));
 gf180mcu_fd_sc_mcu7t5v0__dffq_1 _51_ (.D(t_d[51]),
    .CLK(clknet_3_0__leaf_clk),
    .Q(t_q[51]));
 gf180mcu_fd_sc_mcu7t5v0__dffq_1 _52_ (.D(t_d[52]),
    .CLK(clknet_3_6__leaf_clk),
    .Q(t_q[52]));
 gf180mcu_fd_sc_mcu7t5v0__dffq_1 _53_ (.D(t_d[53]),
    .CLK(clknet_3_0__leaf_clk),
    .Q(t_q[53]));
 gf180mcu_fd_sc_mcu7t5v0__dffq_1 _54_ (.D(t_d[54]),
    .CLK(clknet_3_6__leaf_clk),
    .Q(t_q[54]));
 gf180mcu_fd_sc_mcu7t5v0__dffq_1 _55_ (.D(t_d[55]),
    .CLK(clknet_3_6__leaf_clk),
    .Q(t_q[55]));
 gf180mcu_fd_sc_mcu7t5v0__dffq_1 _56_ (.D(t_d[56]),
    .CLK(clknet_3_0__leaf_clk),
    .Q(t_q[56]));
 gf180mcu_fd_sc_mcu7t5v0__dffq_1 _57_ (.D(t_d[57]),
    .CLK(clknet_3_3__leaf_clk),
    .Q(t_q[57]));
 gf180mcu_fd_sc_mcu7t5v0__dffq_1 _58_ (.D(t_d[58]),
    .CLK(clknet_3_3__leaf_clk),
    .Q(t_q[58]));
 gf180mcu_fd_sc_mcu7t5v0__dffq_1 _59_ (.D(t_d[59]),
    .CLK(clknet_3_1__leaf_clk),
    .Q(t_q[59]));
 gf180mcu_fd_sc_mcu7t5v0__dffq_1 _60_ (.D(t_d[60]),
    .CLK(clknet_3_1__leaf_clk),
    .Q(t_q[60]));
 gf180mcu_fd_sc_mcu7t5v0__dffq_1 _61_ (.D(t_d[61]),
    .CLK(clknet_3_2__leaf_clk),
    .Q(t_q[61]));
 gf180mcu_fd_sc_mcu7t5v0__dffq_1 _62_ (.D(t_d[62]),
    .CLK(clknet_3_1__leaf_clk),
    .Q(t_q[62]));
 gf180mcu_fd_sc_mcu7t5v0__dffq_1 _63_ (.D(din[0]),
    .CLK(clknet_3_7__leaf_clk),
    .Q(b_q[0]));
 gf180mcu_fd_sc_mcu7t5v0__dffq_1 _64_ (.D(din[1]),
    .CLK(clknet_3_7__leaf_clk),
    .Q(b_q[1]));
 gf180mcu_fd_sc_mcu7t5v0__dffq_1 _65_ (.D(din[2]),
    .CLK(clknet_3_7__leaf_clk),
    .Q(b_q[2]));
 gf180mcu_fd_sc_mcu7t5v0__dffq_1 _66_ (.D(din[3]),
    .CLK(clknet_3_7__leaf_clk),
    .Q(b_q[3]));
 gf180mcu_fd_sc_mcu7t5v0__buf_4 clkbuf_0_clk (.I(clk),
    .Z(clknet_0_clk));
 gf180mcu_fd_sc_mcu7t5v0__buf_4 clkbuf_3_0__f_clk (.I(clknet_0_clk),
    .Z(clknet_3_0__leaf_clk));
 gf180mcu_fd_sc_mcu7t5v0__buf_4 clkbuf_3_1__f_clk (.I(clknet_0_clk),
    .Z(clknet_3_1__leaf_clk));
 gf180mcu_fd_sc_mcu7t5v0__buf_4 clkbuf_3_2__f_clk (.I(clknet_0_clk),
    .Z(clknet_3_2__leaf_clk));
 gf180mcu_fd_sc_mcu7t5v0__buf_4 clkbuf_3_3__f_clk (.I(clknet_0_clk),
    .Z(clknet_3_3__leaf_clk));
 gf180mcu_fd_sc_mcu7t5v0__buf_4 clkbuf_3_4__f_clk (.I(clknet_0_clk),
    .Z(clknet_3_4__leaf_clk));
 gf180mcu_fd_sc_mcu7t5v0__buf_4 clkbuf_3_5__f_clk (.I(clknet_0_clk),
    .Z(clknet_3_5__leaf_clk));
 gf180mcu_fd_sc_mcu7t5v0__buf_4 clkbuf_3_6__f_clk (.I(clknet_0_clk),
    .Z(clknet_3_6__leaf_clk));
 gf180mcu_fd_sc_mcu7t5v0__buf_4 clkbuf_3_7__f_clk (.I(clknet_0_clk),
    .Z(clknet_3_7__leaf_clk));
 gf180mcu_fd_sc_mcu7t5v0__clkinv_4 clkload0 (.I(clknet_3_0__leaf_clk));
 gf180mcu_fd_sc_mcu7t5v0__clkinv_4 clkload1 (.I(clknet_3_1__leaf_clk));
 gf180mcu_fd_sc_mcu7t5v0__clkinv_4 clkload2 (.I(clknet_3_3__leaf_clk));
 gf180mcu_fd_sc_mcu7t5v0__inv_4 clkload3 (.I(clknet_3_4__leaf_clk));
 gf180mcu_fd_sc_mcu7t5v0__clkinv_8 clkload4 (.I(clknet_3_5__leaf_clk));
 gf180mcu_fd_sc_mcu7t5v0__inv_4 clkload5 (.I(clknet_3_6__leaf_clk));
 gf180mcu_fd_sc_mcu7t5v0__clkinv_8 clkload6 (.I(clknet_3_7__leaf_clk));
 gf180mcu_fd_sc_mcu7t5v0__nand2_4 \u_dec/_038_  (.A1(din[8]),
    .A2(din[9]),
    .ZN(\u_dec/_020_ ));
 gf180mcu_fd_sc_mcu7t5v0__clkinv_1 \u_dec/_040_  (.I(\u_dec/_020_ ),
    .ZN(t_d[47]));
 gf180mcu_fd_sc_mcu7t5v0__inv_1 \u_dec/_041_  (.I(din[7]),
    .ZN(\u_dec/_022_ ));
 gf180mcu_fd_sc_mcu7t5v0__nor2_1 \u_dec/_043_  (.A1(\u_dec/_022_ ),
    .A2(\u_dec/_020_ ),
    .ZN(t_d[55]));
 gf180mcu_fd_sc_mcu7t5v0__buf_8 \u_dec/_044_  (.I(din[7]),
    .Z(\u_dec/_024_ ));
 gf180mcu_fd_sc_mcu7t5v0__buf_8 \u_dec/_045_  (.I(din[6]),
    .Z(\u_dec/_025_ ));
 gf180mcu_fd_sc_mcu7t5v0__nand2_2 \u_dec/_046_  (.A1(\u_dec/_024_ ),
    .A2(\u_dec/_025_ ),
    .ZN(\u_dec/_026_ ));
 gf180mcu_fd_sc_mcu7t5v0__nor2_1 \u_dec/_047_  (.A1(\u_dec/_020_ ),
    .A2(\u_dec/_026_ ),
    .ZN(t_d[59]));
 gf180mcu_fd_sc_mcu7t5v0__buf_8 \u_dec/_048_  (.I(din[5]),
    .Z(\u_dec/_027_ ));
 gf180mcu_fd_sc_mcu7t5v0__nand3_2 \u_dec/_049_  (.A1(\u_dec/_024_ ),
    .A2(\u_dec/_025_ ),
    .A3(\u_dec/_027_ ),
    .ZN(\u_dec/_028_ ));
 gf180mcu_fd_sc_mcu7t5v0__nor2_1 \u_dec/_050_  (.A1(\u_dec/_020_ ),
    .A2(\u_dec/_028_ ),
    .ZN(t_d[61]));
 gf180mcu_fd_sc_mcu7t5v0__nand2_2 \u_dec/_051_  (.A1(din[5]),
    .A2(din[4]),
    .ZN(\u_dec/_029_ ));
 gf180mcu_fd_sc_mcu7t5v0__nor3_2 \u_dec/_052_  (.A1(\u_dec/_020_ ),
    .A2(\u_dec/_026_ ),
    .A3(\u_dec/_029_ ),
    .ZN(t_d[62]));
 gf180mcu_fd_sc_mcu7t5v0__oai211_4 \u_dec/_053_  (.A1(\u_dec/_027_ ),
    .A2(din[4]),
    .B(\u_dec/_024_ ),
    .C(\u_dec/_025_ ),
    .ZN(\u_dec/_030_ ));
 gf180mcu_fd_sc_mcu7t5v0__nor2_1 \u_dec/_054_  (.A1(\u_dec/_020_ ),
    .A2(\u_dec/_030_ ),
    .ZN(t_d[60]));
 gf180mcu_fd_sc_mcu7t5v0__aoi21_2 \u_dec/_055_  (.A1(din[5]),
    .A2(din[4]),
    .B(din[6]),
    .ZN(\u_dec/_031_ ));
 gf180mcu_fd_sc_mcu7t5v0__nor3_2 \u_dec/_056_  (.A1(\u_dec/_022_ ),
    .A2(\u_dec/_020_ ),
    .A3(\u_dec/_031_ ),
    .ZN(t_d[58]));
 gf180mcu_fd_sc_mcu7t5v0__oai21_2 \u_dec/_057_  (.A1(\u_dec/_025_ ),
    .A2(\u_dec/_027_ ),
    .B(\u_dec/_024_ ),
    .ZN(\u_dec/_032_ ));
 gf180mcu_fd_sc_mcu7t5v0__nor2_1 \u_dec/_058_  (.A1(\u_dec/_020_ ),
    .A2(\u_dec/_032_ ),
    .ZN(t_d[57]));
 gf180mcu_fd_sc_mcu7t5v0__oai31_4 \u_dec/_059_  (.A1(\u_dec/_025_ ),
    .A2(\u_dec/_027_ ),
    .A3(din[4]),
    .B(\u_dec/_024_ ),
    .ZN(\u_dec/_033_ ));
 gf180mcu_fd_sc_mcu7t5v0__nor2_1 \u_dec/_060_  (.A1(\u_dec/_020_ ),
    .A2(\u_dec/_033_ ),
    .ZN(t_d[56]));
 gf180mcu_fd_sc_mcu7t5v0__nor2_2 \u_dec/_061_  (.A1(din[7]),
    .A2(din[6]),
    .ZN(\u_dec/_034_ ));
 gf180mcu_fd_sc_mcu7t5v0__nor2_1 \u_dec/_062_  (.A1(\u_dec/_020_ ),
    .A2(\u_dec/_034_ ),
    .ZN(t_d[51]));
 gf180mcu_fd_sc_mcu7t5v0__aoi21_2 \u_dec/_063_  (.A1(\u_dec/_027_ ),
    .A2(din[4]),
    .B(din[7]),
    .ZN(\u_dec/_035_ ));
 gf180mcu_fd_sc_mcu7t5v0__nor3_1 \u_dec/_064_  (.A1(\u_dec/_020_ ),
    .A2(\u_dec/_034_ ),
    .A3(\u_dec/_035_ ),
    .ZN(t_d[54]));
 gf180mcu_fd_sc_mcu7t5v0__aoi21_1 \u_dec/_065_  (.A1(\u_dec/_025_ ),
    .A2(\u_dec/_027_ ),
    .B(din[7]),
    .ZN(\u_dec/_036_ ));
 gf180mcu_fd_sc_mcu7t5v0__nor2_1 \u_dec/_066_  (.A1(\u_dec/_020_ ),
    .A2(\u_dec/_036_ ),
    .ZN(t_d[53]));
 gf180mcu_fd_sc_mcu7t5v0__nor3_2 \u_dec/_067_  (.A1(din[7]),
    .A2(din[5]),
    .A3(din[4]),
    .ZN(\u_dec/_037_ ));
 gf180mcu_fd_sc_mcu7t5v0__nor3_1 \u_dec/_068_  (.A1(\u_dec/_020_ ),
    .A2(\u_dec/_034_ ),
    .A3(\u_dec/_037_ ),
    .ZN(t_d[52]));
 gf180mcu_fd_sc_mcu7t5v0__aoi21_1 \u_dec/_069_  (.A1(\u_dec/_029_ ),
    .A2(\u_dec/_034_ ),
    .B(\u_dec/_020_ ),
    .ZN(t_d[50]));
 gf180mcu_fd_sc_mcu7t5v0__clkinv_1 \u_dec/_070_  (.I(\u_dec/_027_ ),
    .ZN(\u_dec/_000_ ));
 gf180mcu_fd_sc_mcu7t5v0__aoi21_1 \u_dec/_071_  (.A1(\u_dec/_000_ ),
    .A2(\u_dec/_034_ ),
    .B(\u_dec/_020_ ),
    .ZN(t_d[49]));
 gf180mcu_fd_sc_mcu7t5v0__nor4_4 \u_dec/_072_  (.A1(din[7]),
    .A2(din[6]),
    .A3(din[5]),
    .A4(din[4]),
    .ZN(\u_dec/_001_ ));
 gf180mcu_fd_sc_mcu7t5v0__nor2_1 \u_dec/_073_  (.A1(\u_dec/_020_ ),
    .A2(\u_dec/_001_ ),
    .ZN(t_d[48]));
 gf180mcu_fd_sc_mcu7t5v0__nand3_2 \u_dec/_074_  (.A1(\u_dec/_024_ ),
    .A2(\u_dec/_025_ ),
    .A3(din[9]),
    .ZN(\u_dec/_002_ ));
 gf180mcu_fd_sc_mcu7t5v0__nand2_1 \u_dec/_075_  (.A1(\u_dec/_020_ ),
    .A2(\u_dec/_002_ ),
    .ZN(t_d[43]));
 gf180mcu_fd_sc_mcu7t5v0__clkinv_1 \u_dec/_076_  (.I(din[8]),
    .ZN(\u_dec/_003_ ));
 gf180mcu_fd_sc_mcu7t5v0__aoi22_1 \u_dec/_077_  (.A1(\u_dec/_003_ ),
    .A2(\u_dec/_029_ ),
    .B1(\u_dec/_002_ ),
    .B2(\u_dec/_020_ ),
    .ZN(t_d[46]));
 gf180mcu_fd_sc_mcu7t5v0__inv_2 \u_dec/_078_  (.I(din[9]),
    .ZN(\u_dec/_004_ ));
 gf180mcu_fd_sc_mcu7t5v0__nor2_1 \u_dec/_080_  (.A1(\u_dec/_024_ ),
    .A2(din[8]),
    .ZN(\u_dec/_006_ ));
 gf180mcu_fd_sc_mcu7t5v0__nor2_1 \u_dec/_081_  (.A1(\u_dec/_004_ ),
    .A2(\u_dec/_006_ ),
    .ZN(t_d[39]));
 gf180mcu_fd_sc_mcu7t5v0__aoi21_1 \u_dec/_083_  (.A1(\u_dec/_003_ ),
    .A2(\u_dec/_028_ ),
    .B(\u_dec/_004_ ),
    .ZN(t_d[45]));
 gf180mcu_fd_sc_mcu7t5v0__aoi21_1 \u_dec/_084_  (.A1(\u_dec/_003_ ),
    .A2(\u_dec/_030_ ),
    .B(\u_dec/_004_ ),
    .ZN(t_d[44]));
 gf180mcu_fd_sc_mcu7t5v0__oai31_2 \u_dec/_086_  (.A1(\u_dec/_022_ ),
    .A2(\u_dec/_004_ ),
    .A3(\u_dec/_031_ ),
    .B(\u_dec/_020_ ),
    .ZN(t_d[42]));
 gf180mcu_fd_sc_mcu7t5v0__aoi21_1 \u_dec/_087_  (.A1(\u_dec/_003_ ),
    .A2(\u_dec/_032_ ),
    .B(\u_dec/_004_ ),
    .ZN(t_d[41]));
 gf180mcu_fd_sc_mcu7t5v0__aoi21_1 \u_dec/_088_  (.A1(\u_dec/_003_ ),
    .A2(\u_dec/_033_ ),
    .B(\u_dec/_004_ ),
    .ZN(t_d[40]));
 gf180mcu_fd_sc_mcu7t5v0__oai21_1 \u_dec/_089_  (.A1(\u_dec/_024_ ),
    .A2(\u_dec/_025_ ),
    .B(din[9]),
    .ZN(\u_dec/_009_ ));
 gf180mcu_fd_sc_mcu7t5v0__nand2_1 \u_dec/_090_  (.A1(\u_dec/_020_ ),
    .A2(\u_dec/_009_ ),
    .ZN(t_d[35]));
 gf180mcu_fd_sc_mcu7t5v0__oai21_1 \u_dec/_091_  (.A1(\u_dec/_009_ ),
    .A2(\u_dec/_035_ ),
    .B(\u_dec/_020_ ),
    .ZN(t_d[38]));
 gf180mcu_fd_sc_mcu7t5v0__aoi21_1 \u_dec/_092_  (.A1(\u_dec/_003_ ),
    .A2(\u_dec/_036_ ),
    .B(\u_dec/_004_ ),
    .ZN(t_d[37]));
 gf180mcu_fd_sc_mcu7t5v0__oai21_1 \u_dec/_093_  (.A1(\u_dec/_009_ ),
    .A2(\u_dec/_037_ ),
    .B(\u_dec/_020_ ),
    .ZN(t_d[36]));
 gf180mcu_fd_sc_mcu7t5v0__aoi21_1 \u_dec/_094_  (.A1(\u_dec/_031_ ),
    .A2(\u_dec/_006_ ),
    .B(\u_dec/_004_ ),
    .ZN(t_d[34]));
 gf180mcu_fd_sc_mcu7t5v0__nor2_1 \u_dec/_095_  (.A1(\u_dec/_025_ ),
    .A2(\u_dec/_027_ ),
    .ZN(\u_dec/_010_ ));
 gf180mcu_fd_sc_mcu7t5v0__aoi21_1 \u_dec/_096_  (.A1(\u_dec/_010_ ),
    .A2(\u_dec/_006_ ),
    .B(\u_dec/_004_ ),
    .ZN(t_d[33]));
 gf180mcu_fd_sc_mcu7t5v0__aoi21_1 \u_dec/_097_  (.A1(\u_dec/_003_ ),
    .A2(\u_dec/_001_ ),
    .B(\u_dec/_004_ ),
    .ZN(t_d[32]));
 gf180mcu_fd_sc_mcu7t5v0__nor2_4 \u_dec/_098_  (.A1(din[8]),
    .A2(din[9]),
    .ZN(\u_dec/_011_ ));
 gf180mcu_fd_sc_mcu7t5v0__clkinv_1 \u_dec/_100_  (.I(\u_dec/_011_ ),
    .ZN(t_d[15]));
 gf180mcu_fd_sc_mcu7t5v0__aoi21_2 \u_dec/_102_  (.A1(din[7]),
    .A2(din[6]),
    .B(din[9]),
    .ZN(\u_dec/_014_ ));
 gf180mcu_fd_sc_mcu7t5v0__nor2_1 \u_dec/_103_  (.A1(\u_dec/_011_ ),
    .A2(\u_dec/_014_ ),
    .ZN(t_d[27]));
 gf180mcu_fd_sc_mcu7t5v0__aoi211_1 \u_dec/_104_  (.A1(\u_dec/_004_ ),
    .A2(\u_dec/_029_ ),
    .B(\u_dec/_011_ ),
    .C(\u_dec/_014_ ),
    .ZN(t_d[30]));
 gf180mcu_fd_sc_mcu7t5v0__nand2_1 \u_dec/_105_  (.A1(\u_dec/_024_ ),
    .A2(din[8]),
    .ZN(\u_dec/_015_ ));
 gf180mcu_fd_sc_mcu7t5v0__nand2_1 \u_dec/_106_  (.A1(\u_dec/_004_ ),
    .A2(\u_dec/_015_ ),
    .ZN(t_d[23]));
 gf180mcu_fd_sc_mcu7t5v0__oai21_1 \u_dec/_107_  (.A1(\u_dec/_003_ ),
    .A2(\u_dec/_028_ ),
    .B(\u_dec/_004_ ),
    .ZN(t_d[29]));
 gf180mcu_fd_sc_mcu7t5v0__nor3_1 \u_dec/_108_  (.A1(\u_dec/_027_ ),
    .A2(din[9]),
    .A3(din[4]),
    .ZN(\u_dec/_016_ ));
 gf180mcu_fd_sc_mcu7t5v0__nor3_1 \u_dec/_109_  (.A1(\u_dec/_011_ ),
    .A2(\u_dec/_014_ ),
    .A3(\u_dec/_016_ ),
    .ZN(t_d[28]));
 gf180mcu_fd_sc_mcu7t5v0__oai21_1 \u_dec/_110_  (.A1(\u_dec/_015_ ),
    .A2(\u_dec/_031_ ),
    .B(\u_dec/_004_ ),
    .ZN(t_d[26]));
 gf180mcu_fd_sc_mcu7t5v0__oai21_1 \u_dec/_111_  (.A1(\u_dec/_003_ ),
    .A2(\u_dec/_032_ ),
    .B(\u_dec/_004_ ),
    .ZN(t_d[25]));
 gf180mcu_fd_sc_mcu7t5v0__oai21_1 \u_dec/_112_  (.A1(\u_dec/_027_ ),
    .A2(din[4]),
    .B(\u_dec/_024_ ),
    .ZN(\u_dec/_017_ ));
 gf180mcu_fd_sc_mcu7t5v0__aoi21_1 \u_dec/_113_  (.A1(\u_dec/_017_ ),
    .A2(\u_dec/_014_ ),
    .B(\u_dec/_011_ ),
    .ZN(t_d[24]));
 gf180mcu_fd_sc_mcu7t5v0__nor3_2 \u_dec/_114_  (.A1(din[7]),
    .A2(din[6]),
    .A3(din[9]),
    .ZN(\u_dec/_018_ ));
 gf180mcu_fd_sc_mcu7t5v0__nor2_1 \u_dec/_115_  (.A1(\u_dec/_011_ ),
    .A2(\u_dec/_018_ ),
    .ZN(t_d[19]));
 gf180mcu_fd_sc_mcu7t5v0__aoi211_1 \u_dec/_116_  (.A1(\u_dec/_004_ ),
    .A2(\u_dec/_035_ ),
    .B(\u_dec/_011_ ),
    .C(\u_dec/_018_ ),
    .ZN(t_d[22]));
 gf180mcu_fd_sc_mcu7t5v0__oai21_1 \u_dec/_117_  (.A1(\u_dec/_003_ ),
    .A2(\u_dec/_036_ ),
    .B(\u_dec/_004_ ),
    .ZN(t_d[21]));
 gf180mcu_fd_sc_mcu7t5v0__aoi211_1 \u_dec/_118_  (.A1(\u_dec/_004_ ),
    .A2(\u_dec/_037_ ),
    .B(\u_dec/_011_ ),
    .C(\u_dec/_018_ ),
    .ZN(t_d[20]));
 gf180mcu_fd_sc_mcu7t5v0__aoi21_1 \u_dec/_119_  (.A1(\u_dec/_029_ ),
    .A2(\u_dec/_018_ ),
    .B(\u_dec/_011_ ),
    .ZN(t_d[18]));
 gf180mcu_fd_sc_mcu7t5v0__oai211_1 \u_dec/_120_  (.A1(\u_dec/_003_ ),
    .A2(\u_dec/_010_ ),
    .B(\u_dec/_015_ ),
    .C(\u_dec/_004_ ),
    .ZN(t_d[17]));
 gf180mcu_fd_sc_mcu7t5v0__oai21_1 \u_dec/_121_  (.A1(\u_dec/_003_ ),
    .A2(\u_dec/_001_ ),
    .B(\u_dec/_004_ ),
    .ZN(t_d[16]));
 gf180mcu_fd_sc_mcu7t5v0__oai21_1 \u_dec/_122_  (.A1(\u_dec/_026_ ),
    .A2(\u_dec/_029_ ),
    .B(\u_dec/_011_ ),
    .ZN(t_d[14]));
 gf180mcu_fd_sc_mcu7t5v0__nand2_1 \u_dec/_123_  (.A1(\u_dec/_022_ ),
    .A2(\u_dec/_011_ ),
    .ZN(t_d[7]));
 gf180mcu_fd_sc_mcu7t5v0__nand2_1 \u_dec/_124_  (.A1(\u_dec/_028_ ),
    .A2(\u_dec/_011_ ),
    .ZN(t_d[13]));
 gf180mcu_fd_sc_mcu7t5v0__nand2_1 \u_dec/_125_  (.A1(\u_dec/_030_ ),
    .A2(\u_dec/_011_ ),
    .ZN(t_d[12]));
 gf180mcu_fd_sc_mcu7t5v0__nand2_1 \u_dec/_126_  (.A1(\u_dec/_026_ ),
    .A2(\u_dec/_011_ ),
    .ZN(t_d[11]));
 gf180mcu_fd_sc_mcu7t5v0__oai21_1 \u_dec/_127_  (.A1(\u_dec/_022_ ),
    .A2(\u_dec/_031_ ),
    .B(\u_dec/_011_ ),
    .ZN(t_d[10]));
 gf180mcu_fd_sc_mcu7t5v0__nand2_1 \u_dec/_128_  (.A1(\u_dec/_032_ ),
    .A2(\u_dec/_011_ ),
    .ZN(t_d[9]));
 gf180mcu_fd_sc_mcu7t5v0__nand2_1 \u_dec/_129_  (.A1(\u_dec/_033_ ),
    .A2(\u_dec/_011_ ),
    .ZN(t_d[8]));
 gf180mcu_fd_sc_mcu7t5v0__nand2_1 \u_dec/_130_  (.A1(\u_dec/_034_ ),
    .A2(\u_dec/_011_ ),
    .ZN(t_d[3]));
 gf180mcu_fd_sc_mcu7t5v0__clkinv_1 \u_dec/_131_  (.I(\u_dec/_025_ ),
    .ZN(\u_dec/_019_ ));
 gf180mcu_fd_sc_mcu7t5v0__oai211_1 \u_dec/_132_  (.A1(\u_dec/_019_ ),
    .A2(\u_dec/_029_ ),
    .B(\u_dec/_011_ ),
    .C(\u_dec/_022_ ),
    .ZN(t_d[6]));
 gf180mcu_fd_sc_mcu7t5v0__nand2_1 \u_dec/_133_  (.A1(\u_dec/_036_ ),
    .A2(\u_dec/_011_ ),
    .ZN(t_d[5]));
 gf180mcu_fd_sc_mcu7t5v0__oai21_1 \u_dec/_134_  (.A1(\u_dec/_034_ ),
    .A2(\u_dec/_037_ ),
    .B(\u_dec/_011_ ),
    .ZN(t_d[4]));
 gf180mcu_fd_sc_mcu7t5v0__nand3_1 \u_dec/_135_  (.A1(\u_dec/_029_ ),
    .A2(\u_dec/_034_ ),
    .A3(\u_dec/_011_ ),
    .ZN(t_d[2]));
 gf180mcu_fd_sc_mcu7t5v0__nand3_1 \u_dec/_136_  (.A1(\u_dec/_000_ ),
    .A2(\u_dec/_034_ ),
    .A3(\u_dec/_011_ ),
    .ZN(t_d[1]));
 gf180mcu_fd_sc_mcu7t5v0__nand2_1 \u_dec/_137_  (.A1(\u_dec/_001_ ),
    .A2(\u_dec/_011_ ),
    .ZN(t_d[0]));
endmodule
