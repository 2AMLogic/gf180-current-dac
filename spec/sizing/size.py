#!/usr/bin/env python3
"""Reproducible sizing for the current-steering DAC spec (issue #2).

One command regenerates every number in the sizing section of
spec/target-spec.md and writes spec/sizing/sizing-output.md:

    python3 spec/sizing/size.py            # write sizing-output.md
    python3 spec/sizing/size.py --check    # exit 1 if it differs from the file

Stdlib only, seeded, single process. Everything printed here is a MODEL
result (analytic or Monte Carlo over this script's own model). None of it is
measured, and none of it is a SPICE result.

Mismatch model: the gf180mcuD `fets_mm` terms, read from
sm141064.spice in the PDK pinned by sim/pdk.json:
  sigma(Vth)  = 0.7071 * par_vth * 1e-6 / sqrt(Leff*Weff)   (per device)
  sigma(dK/K) = 0.7071 * par_k   * 1e-6 / sqrt(Leff*Weff)   (mobility, per device)
  Leff = L - par_l,  Weff = par*(W - par_w)   (metres; par_w < 0)
The 0.7071 makes the *pair* difference equal par*1e-6/sqrt(Leff*Weff).
Per-device terms are in V*m / m, i.e. mV*um when par_vth is in V.
The PDK carries no spatial-gradient data; the gradient below is an ASSUMPTION
(decision record 0003).
"""

from __future__ import annotations

import argparse
import math
import random
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE / "sizing-output.md"

# --- PDK mismatch coefficients, gf180mcuD sm141064.spice (bin 1 of each flavor)
# (par_vth [V], par_k [-], par_l [m], par_w [m]); sigma uses 1e-6 m scaling.
PDK_MM = {
    "nfet_03v3": (0.007148, 0.007008, 1.5e-7, -1.0e-7),
    "pfet_03v3": (0.00666, 0.002833, 1.5e-7, -1.0e-7),
    "nfet_06v0": (0.01155, 0.0, 4.0e-7, -5.0e-7),
    "pfet_06v0": (0.01051, 0.00517, 3.0e-7, -4.0e-7),
}

# --- Targets (README table; see spec/target-spec.md)
TIERS = {
    "target": dict(nbits=10, fs=100e6, inl=0.5, sfdr=60.0),
    "fallback": dict(nbits=8, fs=50e6, inl=1.0, sfdr=50.0),
    "stretch": dict(nbits=12, fs=200e6, inl=0.25, sfdr=70.0),  # analytic only
}
YIELD = 0.997  # INL yield criterion (3-sigma equivalent)
SEG = {"target": (6, 4), "fallback": (4, 4)}  # (unary bits, binary bits)
MC_SAMPLES = 10000
SEED = 20261017
SIGMA_SOURCE = 0.005  # budget for the current-source device alone (spec row)

# --- Output stage
IFS = 2.0e-3  # full-scale current per output, A
RL = 50.0  # ohm per output, to the supply rail
F_NYQ_FRAC = 0.45  # "near Nyquist" test tone, fraction of fs

# --- Gradient ASSUMPTION: peak-to-peak relative current variation across the
# whole array edge-to-edge. Not from the PDK.
GRAD_LIN = 0.005
GRAD_QUAD = 0.002


def sigma_vth_k(flavor: str, w: float, l: float) -> tuple[float, float]:
    """Per-device sigma(delvto) [V] and sigma(dK/K) from the PDK formula."""
    par_vth, par_k, par_l, par_w = PDK_MM[flavor]
    area = math.sqrt((l - par_l) * (w - par_w))
    return 0.7071 * par_vth * 1e-6 / area, 0.7071 * par_k * 1e-6 / area


def sigma_i(flavor: str, w: float, l: float, vov: float) -> float:
    """Relative drain-current sigma of one device, square-law gm/Id = 2/Vov."""
    sv, sk = sigma_vth_k(flavor, w, l)
    return math.hypot(2.0 / vov * sv, sk)


def min_area(flavor: str, vov: float, sig_target: float) -> tuple[float, float]:
    """Smallest Leff*Weff [um^2] meeting sig_target, and the side of the
    equivalent square (Leff = Weff)."""
    par_vth, par_k, _, _ = PDK_MM[flavor]
    # sigma_i^2 * area = (2/vov * 0.7071*par_vth)^2 + (0.7071*par_k)^2 (um^2 units)
    coef = (2.0 / vov * 0.7071 * par_vth) ** 2 + (0.7071 * par_k) ** 2
    area_um2 = coef / sig_target**2
    return area_um2, math.sqrt(area_um2)


def inl_dnl_samples(nbits, ubits, bbits, sig_u, n, rng, grad, seq):
    """Monte Carlo of max|INL| and max|DNL| in LSB (endpoint-corrected).

    Unary element = 2**bbits unit cells at one site of a square grid of
    2**ubits sites (one extra site, the last, carries the binary block and is
    not switched). Unit errors are independent N(0, sig_u). A gradient adds a
    deterministic linear + quadratic field to the site position; its direction
    and sign are random per sample.
    """
    nu = 2**ubits - 1
    nsite = 2**ubits
    side = int(round(math.sqrt(nsite)))
    assert side * side == nsite, "unary sites must form a square grid"
    xy = [((i % side) - (side - 1) / 2) / ((side - 1) / 2) for i in range(nsite)]
    yy = [((i // side) - (side - 1) / 2) / ((side - 1) / 2) for i in range(nsite)]
    order = sequence(side, seq)[:nu]
    wu = 2**bbits
    codes = 2**nbits
    res = []
    for _ in range(n):
        ang = rng.uniform(0, 2 * math.pi)
        gx, gy = math.cos(ang) * grad[0] / 2, math.sin(ang) * grad[0] / 2
        q = rng.choice((-1, 1)) * grad[1] / 2
        un = []
        for s in order:
            field = gx * xy[s] + gy * yy[s] + q * (xy[s] ** 2 + yy[s] ** 2 - 2 / 3)
            un.append(rng.gauss(0, sig_u * math.sqrt(wu)) + wu * field)
        bin_ = [rng.gauss(0, sig_u * math.sqrt(2**b)) for b in range(bbits)]
        # value of code c: sum of unary errors up to u plus binary bit errors
        cum = [0.0]
        for e in un:
            cum.append(cum[-1] + e)
        btab = [sum(bin_[k] for k in range(bbits) if b >> k & 1) for b in range(wu)]
        val = [c + cum[c // wu] + btab[c % wu] for c in range(codes)]
        # endpoint fit: gain-normalize so code (codes-1) is exact
        gain = (codes - 1) / (val[-1] - val[0])
        val = [(v - val[0]) * gain for v in val]
        inl = max(abs(val[c] - c) for c in range(codes))
        dnl = max(abs(val[c + 1] - val[c] - 1) for c in range(codes - 1))
        res.append((inl, dnl))
    return res


def sequence(side: int, kind: str) -> list[int]:
    """Order in which the unary elements turn on, as grid site indices."""
    n = side * side
    if kind == "raster":
        return list(range(n))
    centre = (side - 1) / 2
    # point-symmetric partner of site s
    partner = lambda s: n - 1 - s
    seen, pairs = set(), []
    for s in sorted(range(n), key=lambda s: (
        (s % side - centre) ** 2 + (s // side - centre) ** 2, s)):
        if s in seen:
            continue
        seen.update((s, partner(s)))
        pairs.append((s, partner(s)))
    if kind == "centroid-pairs":
        return [s for p in pairs for s in p]
    if kind == "inout-pairs":
        # point-symmetric pairs (cancel the linear term every two steps),
        # taken alternately from the innermost and outermost remaining radius
        # so the quadratic (radial) term is also cancelled progressively
        lo, hi, out = 0, len(pairs) - 1, []
        while lo <= hi:
            out.extend(pairs[lo])
            lo += 1
            if lo <= hi:
                out.extend(pairs[hi])
                hi -= 1
        return out
    raise ValueError(kind)


def yield_pct(samples, spec_inl):
    return 100.0 * sum(1 for i, _ in samples if i <= spec_inl) / len(samples)


def pct(samples, idx, q):
    v = sorted(s[idx] for s in samples)
    return v[min(len(v) - 1, int(q * len(v)))]


def fmt(x, nd=3):
    return f"{x:.{nd}g}"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--samples", type=int, default=MC_SAMPLES)
    args = ap.parse_args()
    rng = random.Random(SEED)
    L = []
    w = L.append
    w("# Sizing output")
    w("")
    w("Generated by `python3 spec/sizing/size.py`. Model results (analytic and")
    w("Monte Carlo over this script's own model). Not measured, not SPICE.")
    w(f"Seed {SEED}; Monte Carlo samples per scenario {args.samples}; yield")
    w(f"criterion: max|INL| <= tier limit for {YIELD*100:.1f} % of samples.")
    w("")

    w("## 1. Unit mismatch sigma needed (analytic)")
    w("")
    w("INL peaks at mid-scale: sigma_INL = sigma_u * sqrt(2^N) / 2 [LSB].")
    w("Tier limit / z(yield) = sigma_INL, where z = 2.97 for 99.7 % (two-sided")
    w("0.3 % tail, used as a 3-sigma equivalent). This ignores the maximum over")
    w("codes, so section 3 (Monte Carlo) is the binding number.")
    w("")
    w("| Tier | N | INL limit [LSB] | sigma_u analytic [%] |")
    w("|---|---|---|---|")
    z = 2.97
    ana = {}
    for t, p in TIERS.items():
        s = p["inl"] / z / (math.sqrt(2 ** p["nbits"]) / 2)
        ana[t] = s
        w(f"| {t} | {p['nbits']} | {p['inl']} | {100*s:.3f} |")
    w("")

    w("## 2. Segmentation trade (target tier, N = 10)")
    w("")
    w("Unary bits U, binary bits B = N - U. Cell count is 2^N - 1 unit cells for")
    w("every U; what changes is decoder size, the largest single step and the")
    w("DNL at the unary/binary boundary. 'Max step' is the largest number of")
    w("LSB switched by one control change (glitch proxy: a larger step is a")
    w("larger worst-case glitch energy before retiming).")
    w("")
    w("| U | B | unary elements | decoder outputs | max step [LSB] | sigma(DNL) major carry [LSB] at sigma_u = 1 % |")
    w("|---|---|---|---|---|---|")
    n = 10
    for u in range(2, 11):
        b = n - u
        step = 2**b
        carry = math.sqrt(step + (2**b - 1))  # unary element + all binary bits
        w(f"| {u} | {b} | {2**u-1} | {2**u-1} | {step} | {0.01*carry:.3f} |")
    w("")
    w("Chosen: U = 6, B = 4 (target); U = 4, B = 4 (fallback, N = 8). The")
    w("stretch tier (N = 12) appears only in the analytic tables (sections 1")
    w("and 5); it is not segmented, simulated or sized.")
    w("")

    w("## 3. Monte Carlo INL/DNL yield (random mismatch + assumed gradient)")
    w("")
    w(f"Gradient ASSUMPTION (no PDK data): linear {GRAD_LIN*100:.2f} % and")
    w(f"quadratic {GRAD_QUAD*100:.2f} % peak-to-peak across the unary array,")
    w("random direction/sign per sample. Gradient acts on the unary sites only.")
    w("")
    sigmas = [0.0025, 0.004, 0.005, 0.0075, 0.010]
    seqs = ["raster", "centroid-pairs", "inout-pairs"]
    p = TIERS["target"]
    ub, bb = SEG["target"]
    w("### 3a. Target tier (N = 10, INL <= 0.5 LSB)")
    w("")
    w("| sigma_u [%] | gradient | sequence | INL yield [%] | max|INL| p99.7 [LSB] | max|DNL| p99.7 [LSB] |")
    w("|---|---|---|---|---|---|")
    chosen = {}
    for sg in sigmas:
        for grad, label in ((None, "none"), ((GRAD_LIN, GRAD_QUAD), "lin+quad")):
            for sq in (["raster"] if grad is None else seqs):
                r = random.Random(SEED)
                res = inl_dnl_samples(p["nbits"], ub, bb, sg, args.samples, r,
                                      grad or (0.0, 0.0), sq)
                yv = yield_pct(res, p["inl"])
                chosen[(sg, label, sq)] = yv
                w(f"| {sg*100:.2f} | {label} | {sq if grad else 'n/a'} | {yv:.2f} | "
                  f"{pct(res,0,YIELD):.3f} | {pct(res,1,YIELD):.3f} |")
    w("")
    ok = [sg for sg in sigmas if chosen[(sg, 'none', 'raster')] >= YIELD * 100]
    sig_req = max(ok) if ok else None
    w(f"Largest tabulated sigma_u meeting {YIELD*100:.1f} % with random mismatch")
    w(f"only: {sig_req*100:.2f} %." if sig_req else "none of the tabulated values.")
    both = [sg for sg in sigmas
            if chosen[(sg, 'lin+quad', 'inout-pairs')] >= YIELD * 100]
    sig_spec = max(both) if both else None
    w(f"Largest tabulated sigma_u meeting it with the assumed gradient and the")
    w(f"inout-pairs sequence: {sig_spec*100:.2f} %." if sig_spec else "none.")
    w("")

    w("### 3b. Fallback tier (N = 8, INL <= 1 LSB)")
    w("")
    p8 = TIERS["fallback"]
    ub8, bb8 = SEG["fallback"]
    w("| sigma_u [%] | gradient | sequence | INL yield [%] |")
    w("|---|---|---|---|")
    for sg in (0.01, 0.02, 0.03):
        for grad, label, sq in ((None, "none", "raster"),
                                ((GRAD_LIN, GRAD_QUAD), "lin+quad", "inout-pairs")):
            r = random.Random(SEED)
            res = inl_dnl_samples(p8["nbits"], ub8, bb8, sg, args.samples, r,
                                  grad or (0.0, 0.0), sq)
            w(f"| {sg*100:.2f} | {label} | {sq if grad else 'n/a'} | "
              f"{yield_pct(res, p8['inl']):.2f} |")
    w("")

    w("## 4. Unit-cell gate area from the PDK mismatch model")
    w("")
    sig_unit = SIGMA_SOURCE
    rest = math.sqrt(max((sig_spec or 0) ** 2 - sig_unit**2, 0.0))
    w(f"Total unit sigma_u that closes yield with the gradient (section 3a):")
    w(f"{(sig_spec or 0)*100:.2f} %. Budget for the current-source device alone:")
    w(f"{sig_unit*100:.2f} %, leaving sqrt(total^2 - source^2) = {rest*100:.2f} % in")
    w("quadrature for the cascode, switch and bias-line IR drop. Those are not")
    w("modelled here; the spec lists them as open items.")
    w("")
    w("sigma_I/I = sqrt((2/Vov * sigma_Vth)^2 + sigma_K^2); square-law")
    w("gm/Id = 2/Vov, which overstates gm/Id for short channels, so it is")
    w("conservative on the Vth term. Required Leff*Weff, per unit cell:")
    w("")
    w("| device | Vov [V] | Leff*Weff min [um^2] | e.g. square Leff=Weff [um] |")
    w("|---|---|---|---|")
    areas = {}
    for fl in PDK_MM:
        for vov in (0.2, 0.3, 0.4, 0.5):
            a, s = min_area(fl, vov, sig_unit)
            areas[(fl, vov)] = a
            w(f"| {fl} | {vov} | {a:.2f} | {s:.2f} |")
    w("")
    iu = IFS / (2**TIERS["target"]["nbits"] - 1)
    w(f"Unit current Iu = Ifs / (2^N - 1) = {IFS*1e3:.1f} mA / 1023 = {iu*1e6:.3f} uA.")
    a_pick = areas[("nfet_03v3", 0.4)]
    w(f"Array gate area at nfet_03v3, Vov = 0.4 V: 1023 x {a_pick:.2f} um^2 = "
      f"{1023*a_pick:.0f} um^2 = {1023*a_pick*1e-6:.4f} mm^2 of effective gate")
    w("area (layout area is several times this; not estimated here).")
    w("")
    w("Each unit must be a separate subcircuit instance in Monte Carlo: the")
    w("PDK draws delvto/mulu0 once per instance, so `m=N` on one instance gives")
    w("N cells the same error (probe: spec/sizing/instance-independence-probe.md).")
    w("")

    w("## 5. Output impedance for SFDR (first-order model)")
    w("")
    w("Single-ended-equivalent bound (conservative: a differential output")
    w("cancels the even-order term, but cell-to-cell mismatch of the two")
    w("halves is not modelled). Per-code current I(x) = Ifs*(x - eps*x^2),")
    w("x = code/(2^N-1), eps = RL / Z_T, Z_T = Zu / (2^N-1) (all cells on).")
    w("HD2 = eps/4, so SFDR = 20*log10(4/eps).")
    w("")
    w(f"RL = {RL:.0f} ohm per output, Ifs = {IFS*1e3:.1f} mA per output.")
    w("")
    w("| Tier | SFDR [dBc] | eps max | Z_T min [kohm] | Zu min per unit [Mohm] | f_tone [MHz] | max code-dependent output C [fF] |")
    w("|---|---|---|---|---|---|---|")
    for t, pp in TIERS.items():
        eps = 4.0 / 10 ** (pp["sfdr"] / 20)
        zt = RL / eps
        zu = zt * (2 ** pp["nbits"] - 1)
        f = F_NYQ_FRAC * pp["fs"]
        dc = eps / (2 * math.pi * f * RL)
        w(f"| {t} | {pp['sfdr']:.0f} | {eps:.5f} | {zt/1e3:.2f} | {zu/1e6:.2f} | "
          f"{f/1e6:.0f} | {dc*1e15:.0f} |")
    w("")
    w("The capacitance column replaces Z_T by 1/(j*w*C) for the code-dependent")
    w("part of the output capacitance (eps = w*RL*dC). It is a bound on the")
    w("part of the output capacitance that varies with code, not on the total.")
    w("")

    w("## 6. Power budget (arithmetic, not a simulation)")
    w("")
    vdd = 3.3
    w(f"Output stage at full scale: Ifs x VDD = {IFS*1e3:.1f} mA x {vdd} V = "
      f"{IFS*vdd*1e3:.2f} mW (complementary pair carries Ifs at all codes).")
    w("Bias, drivers and decoder are budgeted in the spec, not derived here.")
    w("")

    text = "\n".join(L) + "\n"
    if args.check:
        if not OUT.exists() or OUT.read_text() != text:
            print("sizing-output.md differs from a fresh run", file=sys.stderr)
            return 1
        print("ok")
        return 0
    OUT.write_text(text)
    print(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
