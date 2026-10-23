* probe inst
.include $PDK_VERSION_DIR/gf180mcuD/libs.tech/ngspice/design.ngspice
.lib $PDK_VERSION_DIR/gf180mcuD/libs.tech/ngspice/sm141064.ngspice typical
.param sw_stat_global=0
.param sw_stat_mismatch=1
Vg g 0 1.0
Vd d 0 1.0
XM1 d g 0 0 nfet_03v3 w=2u l=2u
XM2 d g 0 0 nfet_03v3 w=2u l=2u
XM3 d g 0 0 nfet_03v3 w=2u l=2u
XM4 d g 0 0 nfet_03v3 w=2u l=2u
XM5 d g 0 0 nfet_03v3 w=2u l=2u
XM6 d g 0 0 nfet_03v3 w=2u l=2u
XM7 d g 0 0 nfet_03v3 w=2u l=2u
XM8 d g 0 0 nfet_03v3 w=2u l=2u
XM9 d g 0 0 nfet_03v3 w=2u l=2u
XM10 d g 0 0 nfet_03v3 w=2u l=2u
XM11 d g 0 0 nfet_03v3 w=2u l=2u
XM12 d g 0 0 nfet_03v3 w=2u l=2u
XM13 d g 0 0 nfet_03v3 w=2u l=2u
XM14 d g 0 0 nfet_03v3 w=2u l=2u
XM15 d g 0 0 nfet_03v3 w=2u l=2u
XM16 d g 0 0 nfet_03v3 w=2u l=2u
XM17 d g 0 0 nfet_03v3 w=2u l=2u
XM18 d g 0 0 nfet_03v3 w=2u l=2u
XM19 d g 0 0 nfet_03v3 w=2u l=2u
XM20 d g 0 0 nfet_03v3 w=2u l=2u
XM21 d g 0 0 nfet_03v3 w=2u l=2u
XM22 d g 0 0 nfet_03v3 w=2u l=2u
XM23 d g 0 0 nfet_03v3 w=2u l=2u
XM24 d g 0 0 nfet_03v3 w=2u l=2u
XM25 d g 0 0 nfet_03v3 w=2u l=2u
XM26 d g 0 0 nfet_03v3 w=2u l=2u
XM27 d g 0 0 nfet_03v3 w=2u l=2u
XM28 d g 0 0 nfet_03v3 w=2u l=2u
XM29 d g 0 0 nfet_03v3 w=2u l=2u
XM30 d g 0 0 nfet_03v3 w=2u l=2u
XM31 d g 0 0 nfet_03v3 w=2u l=2u
XM32 d g 0 0 nfet_03v3 w=2u l=2u
XM33 d g 0 0 nfet_03v3 w=2u l=2u
XM34 d g 0 0 nfet_03v3 w=2u l=2u
XM35 d g 0 0 nfet_03v3 w=2u l=2u
XM36 d g 0 0 nfet_03v3 w=2u l=2u
XM37 d g 0 0 nfet_03v3 w=2u l=2u
XM38 d g 0 0 nfet_03v3 w=2u l=2u
XM39 d g 0 0 nfet_03v3 w=2u l=2u
XM40 d g 0 0 nfet_03v3 w=2u l=2u
.op
.control
run
print -i(Vd)
.endc
.end
