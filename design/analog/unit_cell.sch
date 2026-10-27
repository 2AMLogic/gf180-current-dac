v {xschem version=3.4.4 file_version=1.2
}
G {}
V {}
S {}
E {}
C {nfet_03v3.sym} 0 300 0 0 {name=M1 L=10.3u W=2.6u nf=1 m=1 ad="'int((nf+1)/2) * W/nf * 0.18u'" pd="'2*int((nf+1)/2) * (W/nf + 0.18u)'" as="'int((nf+2)/2) * W/nf * 0.18u'" ps="'2*int((nf+2)/2) * (W/nf + 0.18u)'" nrd="'0.18u / W'" nrs="'0.18u / W'" sa=0 sb=0 sd=0 model=nfet_03v3 spiceprefix=X}
N 20 270 20 250 {}
C {devices/lab_pin.sym} 20 250 3 0 {name=l1 sig_type=std_logic lab=n1}
N 20 330 20 350 {}
C {devices/lab_pin.sym} 20 350 1 0 {name=l2 sig_type=std_logic lab=vss}
N -20 300 -40 300 {}
C {devices/lab_pin.sym} -40 300 0 0 {name=l3 sig_type=std_logic lab=vbn}
N 20 300 40 300 {}
C {devices/lab_pin.sym} 40 300 2 0 {name=l4 sig_type=std_logic lab=vss}
C {nfet_03v3.sym} 0 160 0 0 {name=M2 L=1u W=5.2u nf=1 m=1 ad="'int((nf+1)/2) * W/nf * 0.18u'" pd="'2*int((nf+1)/2) * (W/nf + 0.18u)'" as="'int((nf+2)/2) * W/nf * 0.18u'" ps="'2*int((nf+2)/2) * (W/nf + 0.18u)'" nrd="'0.18u / W'" nrs="'0.18u / W'" sa=0 sb=0 sd=0 model=nfet_03v3 spiceprefix=X}
N 20 130 20 110 {}
C {devices/lab_pin.sym} 20 110 3 0 {name=l5 sig_type=std_logic lab=n2}
N 20 190 20 210 {}
C {devices/lab_pin.sym} 20 210 1 0 {name=l6 sig_type=std_logic lab=n1}
N -20 160 -40 160 {}
C {devices/lab_pin.sym} -40 160 0 0 {name=l7 sig_type=std_logic lab=vcas}
N 20 160 40 160 {}
C {devices/lab_pin.sym} 40 160 2 0 {name=l8 sig_type=std_logic lab=vss}
C {nfet_03v3.sym} -120 20 0 0 {name=Msp L=0.28u W=2.6u nf=1 m=1 ad="'int((nf+1)/2) * W/nf * 0.18u'" pd="'2*int((nf+1)/2) * (W/nf + 0.18u)'" as="'int((nf+2)/2) * W/nf * 0.18u'" ps="'2*int((nf+2)/2) * (W/nf + 0.18u)'" nrd="'0.18u / W'" nrs="'0.18u / W'" sa=0 sb=0 sd=0 model=nfet_03v3 spiceprefix=X}
N -100 -10 -100 -30 {}
C {devices/lab_pin.sym} -100 -30 3 0 {name=l9 sig_type=std_logic lab=outp}
N -100 50 -100 70 {}
C {devices/lab_pin.sym} -100 70 1 0 {name=l10 sig_type=std_logic lab=n2}
N -140 20 -160 20 {}
C {devices/lab_pin.sym} -160 20 0 0 {name=l11 sig_type=std_logic lab=sp}
N -100 20 -80 20 {}
C {devices/lab_pin.sym} -80 20 2 0 {name=l12 sig_type=std_logic lab=vss}
C {nfet_03v3.sym} 120 20 0 0 {name=Msn L=0.28u W=2.6u nf=1 m=1 ad="'int((nf+1)/2) * W/nf * 0.18u'" pd="'2*int((nf+1)/2) * (W/nf + 0.18u)'" as="'int((nf+2)/2) * W/nf * 0.18u'" ps="'2*int((nf+2)/2) * (W/nf + 0.18u)'" nrd="'0.18u / W'" nrs="'0.18u / W'" sa=0 sb=0 sd=0 model=nfet_03v3 spiceprefix=X}
N 140 -10 140 -30 {}
C {devices/lab_pin.sym} 140 -30 3 0 {name=l13 sig_type=std_logic lab=outn}
N 140 50 140 70 {}
C {devices/lab_pin.sym} 140 70 1 0 {name=l14 sig_type=std_logic lab=n2}
N 100 20 80 20 {}
C {devices/lab_pin.sym} 80 20 0 0 {name=l15 sig_type=std_logic lab=sn}
N 140 20 160 20 {}
C {devices/lab_pin.sym} 160 20 2 0 {name=l16 sig_type=std_logic lab=vss}
C {devices/ipin.sym} -400 0 0 0 {name=p17 lab=vbn}
N -400 0 -380 0 {}
C {devices/lab_pin.sym} -380 0 2 0 {name=l18 sig_type=std_logic lab=vbn}
C {devices/ipin.sym} -400 20 0 0 {name=p19 lab=vcas}
N -400 20 -380 20 {}
C {devices/lab_pin.sym} -380 20 2 0 {name=l20 sig_type=std_logic lab=vcas}
C {devices/ipin.sym} -400 40 0 0 {name=p21 lab=sp}
N -400 40 -380 40 {}
C {devices/lab_pin.sym} -380 40 2 0 {name=l22 sig_type=std_logic lab=sp}
C {devices/ipin.sym} -400 60 0 0 {name=p23 lab=sn}
N -400 60 -380 60 {}
C {devices/lab_pin.sym} -380 60 2 0 {name=l24 sig_type=std_logic lab=sn}
C {devices/iopin.sym} -400 80 0 0 {name=p25 lab=vss}
N -400 80 -420 80 {}
C {devices/lab_pin.sym} -420 80 0 0 {name=l26 sig_type=std_logic lab=vss}
C {devices/iopin.sym} -400 100 0 0 {name=p27 lab=outp}
N -400 100 -420 100 {}
C {devices/lab_pin.sym} -420 100 0 0 {name=l28 sig_type=std_logic lab=outp}
C {devices/iopin.sym} -400 120 0 0 {name=p29 lab=outn}
N -400 120 -420 120 {}
C {devices/lab_pin.sym} -420 120 0 0 {name=l30 sig_type=std_logic lab=outn}
