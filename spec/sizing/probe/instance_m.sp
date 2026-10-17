* probe m
.include $PDK_VERSION_DIR/gf180mcuD/libs.tech/ngspice/design.ngspice
.lib $PDK_VERSION_DIR/gf180mcuD/libs.tech/ngspice/sm141064.ngspice typical
.param sw_stat_global=0
.param sw_stat_mismatch=1
Vg g 0 1.0
Vd d 0 1.0
XM1 d g 0 0 nfet_03v3 w=2u l=2u m=40
.op
.control
run
print -i(Vd)
.endc
.end
