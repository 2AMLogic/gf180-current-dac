v {xschem version=3.4.4 file_version=1.2
}
G {}
V {}
S {}
E {}
C {pfet_03v3.sym} 0 -70 0 0 {name=Mp1 L=0.28u W=2u nf=1 m=1 ad="'int((nf+1)/2) * W/nf * 0.18u'" pd="'2*int((nf+1)/2) * (W/nf + 0.18u)'" as="'int((nf+2)/2) * W/nf * 0.18u'" ps="'2*int((nf+2)/2) * (W/nf + 0.18u)'" nrd="'0.18u / W'" nrs="'0.18u / W'" sa=0 sb=0 sd=0 model=pfet_03v3 spiceprefix=X}
N 20 -100 20 -120 {}
C {devices/lab_pin.sym} 20 -120 3 0 {name=l1 sig_type=std_logic lab=vdd}
N 20 -40 20 -20 {}
C {devices/lab_pin.sym} 20 -20 1 0 {name=l2 sig_type=std_logic lab=na}
N -20 -70 -40 -70 {}
C {devices/lab_pin.sym} -40 -70 0 0 {name=l3 sig_type=std_logic lab=d}
N 20 -70 40 -70 {}
C {devices/lab_pin.sym} 40 -70 2 0 {name=l4 sig_type=std_logic lab=vdd}
C {nfet_03v3.sym} 0 70 0 0 {name=Mn1 L=0.28u W=1u nf=1 m=1 ad="'int((nf+1)/2) * W/nf * 0.18u'" pd="'2*int((nf+1)/2) * (W/nf + 0.18u)'" as="'int((nf+2)/2) * W/nf * 0.18u'" ps="'2*int((nf+2)/2) * (W/nf + 0.18u)'" nrd="'0.18u / W'" nrs="'0.18u / W'" sa=0 sb=0 sd=0 model=nfet_03v3 spiceprefix=X}
N 20 40 20 20 {}
C {devices/lab_pin.sym} 20 20 3 0 {name=l5 sig_type=std_logic lab=na}
N 20 100 20 120 {}
C {devices/lab_pin.sym} 20 120 1 0 {name=l6 sig_type=std_logic lab=vss}
N -20 70 -40 70 {}
C {devices/lab_pin.sym} -40 70 0 0 {name=l7 sig_type=std_logic lab=d}
N 20 70 40 70 {}
C {devices/lab_pin.sym} 40 70 2 0 {name=l8 sig_type=std_logic lab=vss}
C {pfet_03v3.sym} 200 -70 0 0 {name=Mp2 L=0.28u W=2u nf=1 m=1 ad="'int((nf+1)/2) * W/nf * 0.18u'" pd="'2*int((nf+1)/2) * (W/nf + 0.18u)'" as="'int((nf+2)/2) * W/nf * 0.18u'" ps="'2*int((nf+2)/2) * (W/nf + 0.18u)'" nrd="'0.18u / W'" nrs="'0.18u / W'" sa=0 sb=0 sd=0 model=pfet_03v3 spiceprefix=X}
N 220 -100 220 -120 {}
C {devices/lab_pin.sym} 220 -120 3 0 {name=l9 sig_type=std_logic lab=vdd}
N 220 -40 220 -20 {}
C {devices/lab_pin.sym} 220 -20 1 0 {name=l10 sig_type=std_logic lab=sp}
N 180 -70 160 -70 {}
C {devices/lab_pin.sym} 160 -70 0 0 {name=l11 sig_type=std_logic lab=na}
N 220 -70 240 -70 {}
C {devices/lab_pin.sym} 240 -70 2 0 {name=l12 sig_type=std_logic lab=vdd}
C {nfet_03v3.sym} 200 70 0 0 {name=Mn2 L=0.28u W=1u nf=1 m=1 ad="'int((nf+1)/2) * W/nf * 0.18u'" pd="'2*int((nf+1)/2) * (W/nf + 0.18u)'" as="'int((nf+2)/2) * W/nf * 0.18u'" ps="'2*int((nf+2)/2) * (W/nf + 0.18u)'" nrd="'0.18u / W'" nrs="'0.18u / W'" sa=0 sb=0 sd=0 model=nfet_03v3 spiceprefix=X}
N 220 40 220 20 {}
C {devices/lab_pin.sym} 220 20 3 0 {name=l13 sig_type=std_logic lab=sp}
N 220 100 220 120 {}
C {devices/lab_pin.sym} 220 120 1 0 {name=l14 sig_type=std_logic lab=vss}
N 180 70 160 70 {}
C {devices/lab_pin.sym} 160 70 0 0 {name=l15 sig_type=std_logic lab=na}
N 220 70 240 70 {}
C {devices/lab_pin.sym} 240 70 2 0 {name=l16 sig_type=std_logic lab=vss}
C {pfet_03v3.sym} 400 -70 0 0 {name=Mp3 L=0.28u W=2u nf=1 m=1 ad="'int((nf+1)/2) * W/nf * 0.18u'" pd="'2*int((nf+1)/2) * (W/nf + 0.18u)'" as="'int((nf+2)/2) * W/nf * 0.18u'" ps="'2*int((nf+2)/2) * (W/nf + 0.18u)'" nrd="'0.18u / W'" nrs="'0.18u / W'" sa=0 sb=0 sd=0 model=pfet_03v3 spiceprefix=X}
N 420 -100 420 -120 {}
C {devices/lab_pin.sym} 420 -120 3 0 {name=l17 sig_type=std_logic lab=vdd}
N 420 -40 420 -20 {}
C {devices/lab_pin.sym} 420 -20 1 0 {name=l18 sig_type=std_logic lab=sn}
N 380 -70 360 -70 {}
C {devices/lab_pin.sym} 360 -70 0 0 {name=l19 sig_type=std_logic lab=sp}
N 420 -70 440 -70 {}
C {devices/lab_pin.sym} 440 -70 2 0 {name=l20 sig_type=std_logic lab=vdd}
C {nfet_03v3.sym} 400 70 0 0 {name=Mn3 L=0.28u W=1u nf=1 m=1 ad="'int((nf+1)/2) * W/nf * 0.18u'" pd="'2*int((nf+1)/2) * (W/nf + 0.18u)'" as="'int((nf+2)/2) * W/nf * 0.18u'" ps="'2*int((nf+2)/2) * (W/nf + 0.18u)'" nrd="'0.18u / W'" nrs="'0.18u / W'" sa=0 sb=0 sd=0 model=nfet_03v3 spiceprefix=X}
N 420 40 420 20 {}
C {devices/lab_pin.sym} 420 20 3 0 {name=l21 sig_type=std_logic lab=sn}
N 420 100 420 120 {}
C {devices/lab_pin.sym} 420 120 1 0 {name=l22 sig_type=std_logic lab=vss}
N 380 70 360 70 {}
C {devices/lab_pin.sym} 360 70 0 0 {name=l23 sig_type=std_logic lab=sp}
N 420 70 440 70 {}
C {devices/lab_pin.sym} 440 70 2 0 {name=l24 sig_type=std_logic lab=vss}
C {devices/ipin.sym} -400 0 0 0 {name=p25 lab=d}
N -400 0 -380 0 {}
C {devices/lab_pin.sym} -380 0 2 0 {name=l26 sig_type=std_logic lab=d}
C {devices/iopin.sym} -400 20 0 0 {name=p27 lab=vdd}
N -400 20 -420 20 {}
C {devices/lab_pin.sym} -420 20 0 0 {name=l28 sig_type=std_logic lab=vdd}
C {devices/iopin.sym} -400 40 0 0 {name=p29 lab=vss}
N -400 40 -420 40 {}
C {devices/lab_pin.sym} -420 40 0 0 {name=l30 sig_type=std_logic lab=vss}
C {devices/opin.sym} 700 0 0 0 {name=p31 lab=sp}
N 700 0 680 0 {}
C {devices/lab_pin.sym} 680 0 0 0 {name=l32 sig_type=std_logic lab=sp}
C {devices/opin.sym} 700 20 0 0 {name=p33 lab=sn}
N 700 20 680 20 {}
C {devices/lab_pin.sym} 680 20 0 0 {name=l34 sig_type=std_logic lab=sn}
