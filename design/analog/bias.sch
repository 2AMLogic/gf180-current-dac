v {xschem version=3.4.4 file_version=1.2
}
G {}
V {}
S {}
E {}
C {nfet_03v3.sym} 0 0 0 0 {name=Mc0 L=1u W=5.2u nf=1 m=1 ad="'int((nf+1)/2) * W/nf * 0.18u'" pd="'2*int((nf+1)/2) * (W/nf + 0.18u)'" as="'int((nf+2)/2) * W/nf * 0.18u'" ps="'2*int((nf+2)/2) * (W/nf + 0.18u)'" nrd="'0.18u / W'" nrs="'0.18u / W'" sa=0 sb=0 sd=0 model=nfet_03v3 spiceprefix=X}
N 20 -30 20 -50 {}
C {devices/lab_pin.sym} 20 -50 3 0 {name=l1 sig_type=std_logic lab=iref}
N 20 30 20 50 {}
C {devices/lab_pin.sym} 20 50 1 0 {name=l2 sig_type=std_logic lab=vbn}
N -20 0 -40 0 {}
C {devices/lab_pin.sym} -40 0 0 0 {name=l3 sig_type=std_logic lab=iref}
N 20 0 40 0 {}
C {devices/lab_pin.sym} 40 0 2 0 {name=l4 sig_type=std_logic lab=vss}
C {nfet_03v3.sym} 0 200 0 0 {name=Mb0 L=10.3u W=2.6u nf=1 m=1 ad="'int((nf+1)/2) * W/nf * 0.18u'" pd="'2*int((nf+1)/2) * (W/nf + 0.18u)'" as="'int((nf+2)/2) * W/nf * 0.18u'" ps="'2*int((nf+2)/2) * (W/nf + 0.18u)'" nrd="'0.18u / W'" nrs="'0.18u / W'" sa=0 sb=0 sd=0 model=nfet_03v3 spiceprefix=X}
N 20 170 20 150 {}
C {devices/lab_pin.sym} 20 150 3 0 {name=l5 sig_type=std_logic lab=vbn}
N 20 230 20 250 {}
C {devices/lab_pin.sym} 20 250 1 0 {name=l6 sig_type=std_logic lab=vss}
N -20 200 -40 200 {}
C {devices/lab_pin.sym} -40 200 0 0 {name=l7 sig_type=std_logic lab=vbn}
N 20 200 40 200 {}
C {devices/lab_pin.sym} 40 200 2 0 {name=l8 sig_type=std_logic lab=vss}
C {nfet_03v3.sym} 120 0 0 0 {name=Mc1 L=1u W=5.2u nf=1 m=1 ad="'int((nf+1)/2) * W/nf * 0.18u'" pd="'2*int((nf+1)/2) * (W/nf + 0.18u)'" as="'int((nf+2)/2) * W/nf * 0.18u'" ps="'2*int((nf+2)/2) * (W/nf + 0.18u)'" nrd="'0.18u / W'" nrs="'0.18u / W'" sa=0 sb=0 sd=0 model=nfet_03v3 spiceprefix=X}
N 140 -30 140 -50 {}
C {devices/lab_pin.sym} 140 -50 3 0 {name=l9 sig_type=std_logic lab=iref}
N 140 30 140 50 {}
C {devices/lab_pin.sym} 140 50 1 0 {name=l10 sig_type=std_logic lab=vbn}
N 100 0 80 0 {}
C {devices/lab_pin.sym} 80 0 0 0 {name=l11 sig_type=std_logic lab=iref}
N 140 0 160 0 {}
C {devices/lab_pin.sym} 160 0 2 0 {name=l12 sig_type=std_logic lab=vss}
C {nfet_03v3.sym} 120 200 0 0 {name=Mb1 L=10.3u W=2.6u nf=1 m=1 ad="'int((nf+1)/2) * W/nf * 0.18u'" pd="'2*int((nf+1)/2) * (W/nf + 0.18u)'" as="'int((nf+2)/2) * W/nf * 0.18u'" ps="'2*int((nf+2)/2) * (W/nf + 0.18u)'" nrd="'0.18u / W'" nrs="'0.18u / W'" sa=0 sb=0 sd=0 model=nfet_03v3 spiceprefix=X}
N 140 170 140 150 {}
C {devices/lab_pin.sym} 140 150 3 0 {name=l13 sig_type=std_logic lab=vbn}
N 140 230 140 250 {}
C {devices/lab_pin.sym} 140 250 1 0 {name=l14 sig_type=std_logic lab=vss}
N 100 200 80 200 {}
C {devices/lab_pin.sym} 80 200 0 0 {name=l15 sig_type=std_logic lab=vbn}
N 140 200 160 200 {}
C {devices/lab_pin.sym} 160 200 2 0 {name=l16 sig_type=std_logic lab=vss}
C {nfet_03v3.sym} 240 0 0 0 {name=Mc2 L=1u W=5.2u nf=1 m=1 ad="'int((nf+1)/2) * W/nf * 0.18u'" pd="'2*int((nf+1)/2) * (W/nf + 0.18u)'" as="'int((nf+2)/2) * W/nf * 0.18u'" ps="'2*int((nf+2)/2) * (W/nf + 0.18u)'" nrd="'0.18u / W'" nrs="'0.18u / W'" sa=0 sb=0 sd=0 model=nfet_03v3 spiceprefix=X}
N 260 -30 260 -50 {}
C {devices/lab_pin.sym} 260 -50 3 0 {name=l17 sig_type=std_logic lab=iref}
N 260 30 260 50 {}
C {devices/lab_pin.sym} 260 50 1 0 {name=l18 sig_type=std_logic lab=vbn}
N 220 0 200 0 {}
C {devices/lab_pin.sym} 200 0 0 0 {name=l19 sig_type=std_logic lab=iref}
N 260 0 280 0 {}
C {devices/lab_pin.sym} 280 0 2 0 {name=l20 sig_type=std_logic lab=vss}
C {nfet_03v3.sym} 240 200 0 0 {name=Mb2 L=10.3u W=2.6u nf=1 m=1 ad="'int((nf+1)/2) * W/nf * 0.18u'" pd="'2*int((nf+1)/2) * (W/nf + 0.18u)'" as="'int((nf+2)/2) * W/nf * 0.18u'" ps="'2*int((nf+2)/2) * (W/nf + 0.18u)'" nrd="'0.18u / W'" nrs="'0.18u / W'" sa=0 sb=0 sd=0 model=nfet_03v3 spiceprefix=X}
N 260 170 260 150 {}
C {devices/lab_pin.sym} 260 150 3 0 {name=l21 sig_type=std_logic lab=vbn}
N 260 230 260 250 {}
C {devices/lab_pin.sym} 260 250 1 0 {name=l22 sig_type=std_logic lab=vss}
N 220 200 200 200 {}
C {devices/lab_pin.sym} 200 200 0 0 {name=l23 sig_type=std_logic lab=vbn}
N 260 200 280 200 {}
C {devices/lab_pin.sym} 280 200 2 0 {name=l24 sig_type=std_logic lab=vss}
C {nfet_03v3.sym} 360 0 0 0 {name=Mc3 L=1u W=5.2u nf=1 m=1 ad="'int((nf+1)/2) * W/nf * 0.18u'" pd="'2*int((nf+1)/2) * (W/nf + 0.18u)'" as="'int((nf+2)/2) * W/nf * 0.18u'" ps="'2*int((nf+2)/2) * (W/nf + 0.18u)'" nrd="'0.18u / W'" nrs="'0.18u / W'" sa=0 sb=0 sd=0 model=nfet_03v3 spiceprefix=X}
N 380 -30 380 -50 {}
C {devices/lab_pin.sym} 380 -50 3 0 {name=l25 sig_type=std_logic lab=iref}
N 380 30 380 50 {}
C {devices/lab_pin.sym} 380 50 1 0 {name=l26 sig_type=std_logic lab=vbn}
N 340 0 320 0 {}
C {devices/lab_pin.sym} 320 0 0 0 {name=l27 sig_type=std_logic lab=iref}
N 380 0 400 0 {}
C {devices/lab_pin.sym} 400 0 2 0 {name=l28 sig_type=std_logic lab=vss}
C {nfet_03v3.sym} 360 200 0 0 {name=Mb3 L=10.3u W=2.6u nf=1 m=1 ad="'int((nf+1)/2) * W/nf * 0.18u'" pd="'2*int((nf+1)/2) * (W/nf + 0.18u)'" as="'int((nf+2)/2) * W/nf * 0.18u'" ps="'2*int((nf+2)/2) * (W/nf + 0.18u)'" nrd="'0.18u / W'" nrs="'0.18u / W'" sa=0 sb=0 sd=0 model=nfet_03v3 spiceprefix=X}
N 380 170 380 150 {}
C {devices/lab_pin.sym} 380 150 3 0 {name=l29 sig_type=std_logic lab=vbn}
N 380 230 380 250 {}
C {devices/lab_pin.sym} 380 250 1 0 {name=l30 sig_type=std_logic lab=vss}
N 340 200 320 200 {}
C {devices/lab_pin.sym} 320 200 0 0 {name=l31 sig_type=std_logic lab=vbn}
N 380 200 400 200 {}
C {devices/lab_pin.sym} 400 200 2 0 {name=l32 sig_type=std_logic lab=vss}
C {nfet_03v3.sym} 480 0 0 0 {name=Mc4 L=1u W=5.2u nf=1 m=1 ad="'int((nf+1)/2) * W/nf * 0.18u'" pd="'2*int((nf+1)/2) * (W/nf + 0.18u)'" as="'int((nf+2)/2) * W/nf * 0.18u'" ps="'2*int((nf+2)/2) * (W/nf + 0.18u)'" nrd="'0.18u / W'" nrs="'0.18u / W'" sa=0 sb=0 sd=0 model=nfet_03v3 spiceprefix=X}
N 500 -30 500 -50 {}
C {devices/lab_pin.sym} 500 -50 3 0 {name=l33 sig_type=std_logic lab=iref}
N 500 30 500 50 {}
C {devices/lab_pin.sym} 500 50 1 0 {name=l34 sig_type=std_logic lab=vbn}
N 460 0 440 0 {}
C {devices/lab_pin.sym} 440 0 0 0 {name=l35 sig_type=std_logic lab=iref}
N 500 0 520 0 {}
C {devices/lab_pin.sym} 520 0 2 0 {name=l36 sig_type=std_logic lab=vss}
C {nfet_03v3.sym} 480 200 0 0 {name=Mb4 L=10.3u W=2.6u nf=1 m=1 ad="'int((nf+1)/2) * W/nf * 0.18u'" pd="'2*int((nf+1)/2) * (W/nf + 0.18u)'" as="'int((nf+2)/2) * W/nf * 0.18u'" ps="'2*int((nf+2)/2) * (W/nf + 0.18u)'" nrd="'0.18u / W'" nrs="'0.18u / W'" sa=0 sb=0 sd=0 model=nfet_03v3 spiceprefix=X}
N 500 170 500 150 {}
C {devices/lab_pin.sym} 500 150 3 0 {name=l37 sig_type=std_logic lab=vbn}
N 500 230 500 250 {}
C {devices/lab_pin.sym} 500 250 1 0 {name=l38 sig_type=std_logic lab=vss}
N 460 200 440 200 {}
C {devices/lab_pin.sym} 440 200 0 0 {name=l39 sig_type=std_logic lab=vbn}
N 500 200 520 200 {}
C {devices/lab_pin.sym} 520 200 2 0 {name=l40 sig_type=std_logic lab=vss}
C {nfet_03v3.sym} 600 0 0 0 {name=Mc5 L=1u W=5.2u nf=1 m=1 ad="'int((nf+1)/2) * W/nf * 0.18u'" pd="'2*int((nf+1)/2) * (W/nf + 0.18u)'" as="'int((nf+2)/2) * W/nf * 0.18u'" ps="'2*int((nf+2)/2) * (W/nf + 0.18u)'" nrd="'0.18u / W'" nrs="'0.18u / W'" sa=0 sb=0 sd=0 model=nfet_03v3 spiceprefix=X}
N 620 -30 620 -50 {}
C {devices/lab_pin.sym} 620 -50 3 0 {name=l41 sig_type=std_logic lab=iref}
N 620 30 620 50 {}
C {devices/lab_pin.sym} 620 50 1 0 {name=l42 sig_type=std_logic lab=vbn}
N 580 0 560 0 {}
C {devices/lab_pin.sym} 560 0 0 0 {name=l43 sig_type=std_logic lab=iref}
N 620 0 640 0 {}
C {devices/lab_pin.sym} 640 0 2 0 {name=l44 sig_type=std_logic lab=vss}
C {nfet_03v3.sym} 600 200 0 0 {name=Mb5 L=10.3u W=2.6u nf=1 m=1 ad="'int((nf+1)/2) * W/nf * 0.18u'" pd="'2*int((nf+1)/2) * (W/nf + 0.18u)'" as="'int((nf+2)/2) * W/nf * 0.18u'" ps="'2*int((nf+2)/2) * (W/nf + 0.18u)'" nrd="'0.18u / W'" nrs="'0.18u / W'" sa=0 sb=0 sd=0 model=nfet_03v3 spiceprefix=X}
N 620 170 620 150 {}
C {devices/lab_pin.sym} 620 150 3 0 {name=l45 sig_type=std_logic lab=vbn}
N 620 230 620 250 {}
C {devices/lab_pin.sym} 620 250 1 0 {name=l46 sig_type=std_logic lab=vss}
N 580 200 560 200 {}
C {devices/lab_pin.sym} 560 200 0 0 {name=l47 sig_type=std_logic lab=vbn}
N 620 200 640 200 {}
C {devices/lab_pin.sym} 640 200 2 0 {name=l48 sig_type=std_logic lab=vss}
C {nfet_03v3.sym} 720 0 0 0 {name=Mc6 L=1u W=5.2u nf=1 m=1 ad="'int((nf+1)/2) * W/nf * 0.18u'" pd="'2*int((nf+1)/2) * (W/nf + 0.18u)'" as="'int((nf+2)/2) * W/nf * 0.18u'" ps="'2*int((nf+2)/2) * (W/nf + 0.18u)'" nrd="'0.18u / W'" nrs="'0.18u / W'" sa=0 sb=0 sd=0 model=nfet_03v3 spiceprefix=X}
N 740 -30 740 -50 {}
C {devices/lab_pin.sym} 740 -50 3 0 {name=l49 sig_type=std_logic lab=iref}
N 740 30 740 50 {}
C {devices/lab_pin.sym} 740 50 1 0 {name=l50 sig_type=std_logic lab=vbn}
N 700 0 680 0 {}
C {devices/lab_pin.sym} 680 0 0 0 {name=l51 sig_type=std_logic lab=iref}
N 740 0 760 0 {}
C {devices/lab_pin.sym} 760 0 2 0 {name=l52 sig_type=std_logic lab=vss}
C {nfet_03v3.sym} 720 200 0 0 {name=Mb6 L=10.3u W=2.6u nf=1 m=1 ad="'int((nf+1)/2) * W/nf * 0.18u'" pd="'2*int((nf+1)/2) * (W/nf + 0.18u)'" as="'int((nf+2)/2) * W/nf * 0.18u'" ps="'2*int((nf+2)/2) * (W/nf + 0.18u)'" nrd="'0.18u / W'" nrs="'0.18u / W'" sa=0 sb=0 sd=0 model=nfet_03v3 spiceprefix=X}
N 740 170 740 150 {}
C {devices/lab_pin.sym} 740 150 3 0 {name=l53 sig_type=std_logic lab=vbn}
N 740 230 740 250 {}
C {devices/lab_pin.sym} 740 250 1 0 {name=l54 sig_type=std_logic lab=vss}
N 700 200 680 200 {}
C {devices/lab_pin.sym} 680 200 0 0 {name=l55 sig_type=std_logic lab=vbn}
N 740 200 760 200 {}
C {devices/lab_pin.sym} 760 200 2 0 {name=l56 sig_type=std_logic lab=vss}
C {nfet_03v3.sym} 840 0 0 0 {name=Mc7 L=1u W=5.2u nf=1 m=1 ad="'int((nf+1)/2) * W/nf * 0.18u'" pd="'2*int((nf+1)/2) * (W/nf + 0.18u)'" as="'int((nf+2)/2) * W/nf * 0.18u'" ps="'2*int((nf+2)/2) * (W/nf + 0.18u)'" nrd="'0.18u / W'" nrs="'0.18u / W'" sa=0 sb=0 sd=0 model=nfet_03v3 spiceprefix=X}
N 860 -30 860 -50 {}
C {devices/lab_pin.sym} 860 -50 3 0 {name=l57 sig_type=std_logic lab=iref}
N 860 30 860 50 {}
C {devices/lab_pin.sym} 860 50 1 0 {name=l58 sig_type=std_logic lab=vbn}
N 820 0 800 0 {}
C {devices/lab_pin.sym} 800 0 0 0 {name=l59 sig_type=std_logic lab=iref}
N 860 0 880 0 {}
C {devices/lab_pin.sym} 880 0 2 0 {name=l60 sig_type=std_logic lab=vss}
C {nfet_03v3.sym} 840 200 0 0 {name=Mb7 L=10.3u W=2.6u nf=1 m=1 ad="'int((nf+1)/2) * W/nf * 0.18u'" pd="'2*int((nf+1)/2) * (W/nf + 0.18u)'" as="'int((nf+2)/2) * W/nf * 0.18u'" ps="'2*int((nf+2)/2) * (W/nf + 0.18u)'" nrd="'0.18u / W'" nrs="'0.18u / W'" sa=0 sb=0 sd=0 model=nfet_03v3 spiceprefix=X}
N 860 170 860 150 {}
C {devices/lab_pin.sym} 860 150 3 0 {name=l61 sig_type=std_logic lab=vbn}
N 860 230 860 250 {}
C {devices/lab_pin.sym} 860 250 1 0 {name=l62 sig_type=std_logic lab=vss}
N 820 200 800 200 {}
C {devices/lab_pin.sym} 800 200 0 0 {name=l63 sig_type=std_logic lab=vbn}
N 860 200 880 200 {}
C {devices/lab_pin.sym} 880 200 2 0 {name=l64 sig_type=std_logic lab=vss}
C {nfet_03v3.sym} 960 0 0 0 {name=Mc8 L=1u W=5.2u nf=1 m=1 ad="'int((nf+1)/2) * W/nf * 0.18u'" pd="'2*int((nf+1)/2) * (W/nf + 0.18u)'" as="'int((nf+2)/2) * W/nf * 0.18u'" ps="'2*int((nf+2)/2) * (W/nf + 0.18u)'" nrd="'0.18u / W'" nrs="'0.18u / W'" sa=0 sb=0 sd=0 model=nfet_03v3 spiceprefix=X}
N 980 -30 980 -50 {}
C {devices/lab_pin.sym} 980 -50 3 0 {name=l65 sig_type=std_logic lab=iref}
N 980 30 980 50 {}
C {devices/lab_pin.sym} 980 50 1 0 {name=l66 sig_type=std_logic lab=vbn}
N 940 0 920 0 {}
C {devices/lab_pin.sym} 920 0 0 0 {name=l67 sig_type=std_logic lab=iref}
N 980 0 1000 0 {}
C {devices/lab_pin.sym} 1000 0 2 0 {name=l68 sig_type=std_logic lab=vss}
C {nfet_03v3.sym} 960 200 0 0 {name=Mb8 L=10.3u W=2.6u nf=1 m=1 ad="'int((nf+1)/2) * W/nf * 0.18u'" pd="'2*int((nf+1)/2) * (W/nf + 0.18u)'" as="'int((nf+2)/2) * W/nf * 0.18u'" ps="'2*int((nf+2)/2) * (W/nf + 0.18u)'" nrd="'0.18u / W'" nrs="'0.18u / W'" sa=0 sb=0 sd=0 model=nfet_03v3 spiceprefix=X}
N 980 170 980 150 {}
C {devices/lab_pin.sym} 980 150 3 0 {name=l69 sig_type=std_logic lab=vbn}
N 980 230 980 250 {}
C {devices/lab_pin.sym} 980 250 1 0 {name=l70 sig_type=std_logic lab=vss}
N 940 200 920 200 {}
C {devices/lab_pin.sym} 920 200 0 0 {name=l71 sig_type=std_logic lab=vbn}
N 980 200 1000 200 {}
C {devices/lab_pin.sym} 1000 200 2 0 {name=l72 sig_type=std_logic lab=vss}
C {nfet_03v3.sym} 1080 0 0 0 {name=Mc9 L=1u W=5.2u nf=1 m=1 ad="'int((nf+1)/2) * W/nf * 0.18u'" pd="'2*int((nf+1)/2) * (W/nf + 0.18u)'" as="'int((nf+2)/2) * W/nf * 0.18u'" ps="'2*int((nf+2)/2) * (W/nf + 0.18u)'" nrd="'0.18u / W'" nrs="'0.18u / W'" sa=0 sb=0 sd=0 model=nfet_03v3 spiceprefix=X}
N 1100 -30 1100 -50 {}
C {devices/lab_pin.sym} 1100 -50 3 0 {name=l73 sig_type=std_logic lab=iref}
N 1100 30 1100 50 {}
C {devices/lab_pin.sym} 1100 50 1 0 {name=l74 sig_type=std_logic lab=vbn}
N 1060 0 1040 0 {}
C {devices/lab_pin.sym} 1040 0 0 0 {name=l75 sig_type=std_logic lab=iref}
N 1100 0 1120 0 {}
C {devices/lab_pin.sym} 1120 0 2 0 {name=l76 sig_type=std_logic lab=vss}
C {nfet_03v3.sym} 1080 200 0 0 {name=Mb9 L=10.3u W=2.6u nf=1 m=1 ad="'int((nf+1)/2) * W/nf * 0.18u'" pd="'2*int((nf+1)/2) * (W/nf + 0.18u)'" as="'int((nf+2)/2) * W/nf * 0.18u'" ps="'2*int((nf+2)/2) * (W/nf + 0.18u)'" nrd="'0.18u / W'" nrs="'0.18u / W'" sa=0 sb=0 sd=0 model=nfet_03v3 spiceprefix=X}
N 1100 170 1100 150 {}
C {devices/lab_pin.sym} 1100 150 3 0 {name=l77 sig_type=std_logic lab=vbn}
N 1100 230 1100 250 {}
C {devices/lab_pin.sym} 1100 250 1 0 {name=l78 sig_type=std_logic lab=vss}
N 1060 200 1040 200 {}
C {devices/lab_pin.sym} 1040 200 0 0 {name=l79 sig_type=std_logic lab=vbn}
N 1100 200 1120 200 {}
C {devices/lab_pin.sym} 1120 200 2 0 {name=l80 sig_type=std_logic lab=vss}
C {devices/iopin.sym} -400 0 0 0 {name=p81 lab=iref}
N -400 0 -420 0 {}
C {devices/lab_pin.sym} -420 0 0 0 {name=l82 sig_type=std_logic lab=iref}
C {devices/iopin.sym} -400 20 0 0 {name=p83 lab=vss}
N -400 20 -420 20 {}
C {devices/lab_pin.sym} -420 20 0 0 {name=l84 sig_type=std_logic lab=vss}
C {devices/opin.sym} 1400 0 0 0 {name=p85 lab=vbn}
N 1400 0 1380 0 {}
C {devices/lab_pin.sym} 1380 0 0 0 {name=l86 sig_type=std_logic lab=vbn}
