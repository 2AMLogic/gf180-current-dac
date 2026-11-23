"""cocotb regression for `dac_digital`, run through `klt functional-verification`.

Ports the four checks of `verification/rtl/tb_dac_digital.v` (which stays in
place as the item-1 design sanity check) to the cocotb path, because T1 items 5
and 7 accept a `klt functional-verification` JSON report and only this path
produces one. The same module runs against the RTL (`rtl/`), against the
synthesized gate-level netlist (`synth/out/dac_digital/dac_digital_synth.v`),
and against the routed as-built netlist with SDF back-annotation
(`layout/pnr/dac_digital.asbuilt.v`); the requests differ only in `sources`
and, for the annotated one, in `options.sdf` and `env`.

The checks, over all 1024 input codes:

  1. `t_q[i] == (din[9:4] > i)` for i in 0..62 and `b_q == din[3:0]`, read in
     the same cycle (`test_thermometer_and_binary_all_codes`).
  2. at each of the 63 major carries (`din[3:0] == 0`, `din >= 16`),
     `t_q ^ prev_t` is exactly `1 << (din[9:4] - 1)`
     (`test_major_carry_flips_one_line`).
  3. outputs lag `din` by exactly one clock edge, never the same edge
     (`test_one_cycle_latency`).
  4. codes 0 and 1023 against literal expectations, independent of the
     `expected_*` helpers (`test_boundary_codes`).

Two timing schedules, selected by the request's top-level `env` field
(`DAC_TB_TIMING`, forwarded by `klt functional-verification` into the test
process's environment):

- unset (`zero-delay`, the RTL and synthesized-netlist requests): no SDF is
  annotated, no timing is checked, and no signoff-manifest item is cited. See
  `verification/README.md`.
- `dr0008` (the as-built request, T1 item 7 digital): the drive/sample
  schedule of DR-0008, the proposed I/O timing budget
  (`spec/decision-records/0008-digital-io-timing-budget.md`). On consecutive
  10.0 ns cycles the next code is driven at +3.0 ns after each rising edge,
  and the code captured at that edge is checked at +7.0 ns after it -- one
  code per cycle, so throughput is unchanged and the one-edge latency is
  exercised while the next code is already present at the inputs (drive A at
  3 ns, capture A at 10 ns, drive B at 13 ns, check A at 17 ns, capture B at
  20 ns, check B at 27 ns).

Sampling discipline (a real failure observed while building this suite): the
flop bank has no reset -- at gate level the 67 `dffq_1` flops are reset-less by
construction -- so `t_q`/`b_q` are X until the first settled capturing edge.
Every test therefore starts with `_bringup()`, which runs past the first edges
with a known `din`, and in zero-delay mode drives `din` on the falling edge so
it is stable across the rising edge that captures it.
"""

import os

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import FallingEdge, ReadOnly, RisingEdge, Timer
from cocotb.utils import get_sim_time

CODES = 1024
N_THERMO = 63
CLK_PERIOD_NS = 10
SETTLE_NS = 1

# DR-0008 (proposed) I/O budget: input arrival +3.0 ns after the launching
# edge, outputs valid +7.0 ns after the capturing edge. Selected by the
# request's `env` field; the default (unset) keeps the zero-delay schedule.
DR0008 = os.environ.get("DAC_TB_TIMING", "") == "dr0008"
DR0008_DRIVE_NS = 3.0
DR0008_CHECK_NS = 7.0


def expected_thermo(code):
    """Thermometer word for `code`: bit i set iff `code[9:4] > i`."""
    unary = (code >> 4) & 0x3F
    word = 0
    for i in range(N_THERMO):
        if unary > i:
            word |= 1 << i
    return word


def expected_binary(code):
    """Binary LSB path: `code[3:0]`."""
    return code & 0xF


def _read(sig, name, context):
    """Read `sig` as an int, failing loudly if any bit is X or Z.

    Goes through `str()` rather than a version-specific `.integer` /
    `.is_resolvable` accessor so an unresolved bit is reported as the bit
    pattern that was actually sampled instead of raising an opaque conversion
    error.
    """
    text = str(sig.value)
    assert set(text) <= {"0", "1"}, f"{name} is not resolvable ({text}) {context}"
    return int(text, 2)


async def _bringup(dut):
    """Start the clock and leave the DUT settled.

    Runs two rising edges with `din = 0` held: the first clocks the flop bank
    out of its reset-less X state, the second captures a known `din`. Returning
    on the falling edge means every caller can write `din` and have it stable
    well before the rising edge that captures it (zero-delay mode). In DR-0008
    mode it instead returns exactly on the next rising edge, so the first
    +3 ns drive is anchored to an edge.
    """
    global _clk_origin_ns
    _clk_origin_ns = get_sim_time("ns")  # the clock's first (rising) edge
    cocotb.start_soon(Clock(dut.clk, CLK_PERIOD_NS, units="ns").start())
    dut.din.value = 0
    await RisingEdge(dut.clk)
    await RisingEdge(dut.clk)
    await FallingEdge(dut.clk)
    await Timer(SETTLE_NS, units="ns")
    if DR0008:
        # DR-0008 anchors every drive/sample on a rising edge: return exactly
        # on one, so the first +3 ns drive lands 3 ns after an edge.
        await RisingEdge(dut.clk)


# Sim time of this test's first rising edge (set by `_bringup`; each test
# restarts the clock, so absolute sim time is not a multiple of the period).
_clk_origin_ns = 0.0
# Sim-time tolerance for the edge-relative checks (timescale rounding).
PHASE_TOL_NS = 0.01


def _drive_dr0008(dut, code, last_ns):
    """Drive `code` now (must be +3 ns after a rising edge) and check spacing.

    `last_ns` is the sim time of the previous +3 ns drive in the same run of
    consecutive cycles, or None. Returns this drive's sim time in ns.
    """
    now_ns = get_sim_time("ns")
    phase = (now_ns - _clk_origin_ns) % CLK_PERIOD_NS
    assert abs(phase - DR0008_DRIVE_NS) < PHASE_TOL_NS, (
        f"DR-0008 drive of code {code} at {now_ns} ns is {phase} ns after a "
        f"rising edge, want {DR0008_DRIVE_NS}"
    )
    if last_ns is not None:
        assert abs(now_ns - last_ns - CLK_PERIOD_NS) < PHASE_TOL_NS, (
            f"DR-0008 drives {now_ns - last_ns} ns apart, want {CLK_PERIOD_NS}"
        )
    dut.din.value = code
    return now_ns


async def _apply(dut, code):
    """Present `code`, clock it in, and return just after it has settled."""
    dut.din.value = code
    await RisingEdge(dut.clk)
    await Timer(SETTLE_NS, units="ns")


async def _iter_codes(dut, codes):
    """Yield each code at the point where its captured outputs are checkable.

    Zero-delay mode: `_apply` drives `din` on the falling edge and yields just
    after the capturing rising edge has settled -- the original schedule, and
    the two committed zero-delay reports' behavior is unchanged.

    DR-0008 mode: anchored just after a rising edge, the next code is driven
    at +3.0 ns, and the code captured at the anchor edge is yielded at +7.0 ns
    -- with the next code already presented, exactly the budget the annotated
    run must meet. The caller reads only `t_q`/`b_q` at the yield point.
    """
    if not DR0008:
        for code in codes:
            await _apply(dut, code)
            yield code
            await FallingEdge(dut.clk)
        return
    prev = None
    last_drive = None
    for code in codes:
        await Timer(DR0008_DRIVE_NS, units="ns")
        last_drive = _drive_dr0008(dut, code, last_drive)
        await Timer(DR0008_CHECK_NS - DR0008_DRIVE_NS, units="ns")
        # Sample in the read-only phase of the +7 ns timestep, after every
        # update scheduled at that timestamp (e.g. `<= #7`) has settled.
        await ReadOnly()
        if prev is not None:
            yield prev
        prev = code
        await RisingEdge(dut.clk)
    await Timer(DR0008_CHECK_NS, units="ns")
    await ReadOnly()
    yield prev


@cocotb.test()
async def test_thermometer_and_binary_all_codes(dut):
    """All 1024 codes: thermometer value and binary bits, read in one cycle."""
    await _bringup(dut)
    async for code in _iter_codes(dut, range(CODES)):
        where = f"at code {code}"
        got_t = _read(dut.t_q, "t_q", where)
        got_b = _read(dut.b_q, "b_q", where)
        want_t = expected_thermo(code)
        want_b = expected_binary(code)
        assert got_t == want_t, (
            f"t_q mismatch {where}: got {got_t:#018x}, want {want_t:#018x}"
        )
        assert got_b == want_b, (
            f"b_q mismatch {where}: got {got_b}, want {want_b}"
        )


@cocotb.test()
async def test_major_carry_flips_one_line(dut):
    """Each major carry flips exactly one thermometer line.

    Sweeps in code order so `prev_t` is the previous code's settled value, as
    the Verilog bench's loop does.
    """
    await _bringup(dut)
    prev_t = None
    carries = 0
    async for code in _iter_codes(dut, range(CODES)):
        got_t = _read(dut.t_q, "t_q", f"at code {code}")
        if code >= 16 and (code & 0xF) == 0:
            want_flip = 1 << ((code >> 4) - 1)
            got_flip = got_t ^ prev_t
            assert got_flip == want_flip, (
                f"major carry at code {code}: t_q flipped {got_flip:#018x}, "
                f"want exactly one line {want_flip:#018x}"
            )
            carries += 1
        prev_t = got_t
    assert carries == 63, f"expected 63 major carries, exercised {carries}"


@cocotb.test()
async def test_one_cycle_latency(dut):
    """Outputs change on the edge *after* `din`, never the same edge."""
    await _bringup(dut)
    # Each pair changes both the thermometer word and the binary bits, so a
    # zero-cycle (combinational) or two-cycle path is visible in both fields.
    for first, second in ((0, 1023), (1023, 0), (0x00F, 0x010), (0x3F0, 0x00F)):
        if not DR0008:
            await _apply(dut, first)
            where = f"after clocking in code {first}"
            assert _read(dut.t_q, "t_q", where) == expected_thermo(first), where
            assert _read(dut.b_q, "b_q", where) == expected_binary(first), where

            # Present the next code and wait inside the same cycle. The outputs
            # must still hold the previous code: a combinational path would have
            # followed `din` already.
            await FallingEdge(dut.clk)
            dut.din.value = second
            await Timer(SETTLE_NS, units="ns")
            where = f"with code {second} presented but not yet clocked"
            assert _read(dut.t_q, "t_q", where) == expected_thermo(first), (
                f"t_q followed din within the same cycle {where}"
            )
            assert _read(dut.b_q, "b_q", where) == expected_binary(first), (
                f"b_q followed din within the same cycle {where}"
            )

            # One edge later -- and only one -- the outputs are the new code.
            await RisingEdge(dut.clk)
            await Timer(SETTLE_NS, units="ns")
            where = f"one edge after presenting code {second}"
            assert _read(dut.t_q, "t_q", where) == expected_thermo(second), (
                f"t_q did not update one edge after din {where}"
            )
            assert _read(dut.b_q, "b_q", where) == expected_binary(second), (
                f"b_q did not update one edge after din {where}"
            )
            await FallingEdge(dut.clk)
        else:
            # DR-0008 schedule: drive `first` at +3 ns, it is captured by the
            # next edge; drive `second` at that edge +3 ns and check `first`
            # at +7 ns -- `second` is already presented, so a combinational
            # path would have followed it; one further edge later `second`
            # has been captured and is checked in turn.
            await Timer(DR0008_DRIVE_NS, units="ns")
            t_first = _drive_dr0008(dut, first, None)
            await RisingEdge(dut.clk)
            await Timer(DR0008_DRIVE_NS, units="ns")
            _drive_dr0008(dut, second, t_first)
            await Timer(DR0008_CHECK_NS - DR0008_DRIVE_NS, units="ns")
            await ReadOnly()
            where = f"with code {second} presented but not yet captured (first {first})"
            assert _read(dut.t_q, "t_q", where) == expected_thermo(first), (
                f"t_q followed din within the same cycle {where}"
            )
            assert _read(dut.b_q, "b_q", where) == expected_binary(first), (
                f"b_q followed din within the same cycle {where}"
            )
            await RisingEdge(dut.clk)
            await Timer(DR0008_CHECK_NS, units="ns")
            await ReadOnly()
            where = f"one edge after presenting code {second} (first {first})"
            assert _read(dut.t_q, "t_q", where) == expected_thermo(second), (
                f"t_q did not update one edge after din {where}"
            )
            assert _read(dut.b_q, "b_q", where) == expected_binary(second), (
                f"b_q did not update one edge after din {where}"
            )
            # Re-anchor on the next edge so the following pair's +3 ns drive
            # stays clear of a rising edge.
            await RisingEdge(dut.clk)


@cocotb.test()
async def test_boundary_codes(dut):
    """Codes 0 and 1023 against literal expectations.

    Deliberately does not call `expected_thermo` / `expected_binary`: a bug in
    those helpers would hide in the sweeping tests but not here.
    """
    await _bringup(dut)
    # Literal expectations keyed by code, deliberately not computed by the
    # `expected_*` helpers.
    literals = {0: (0, 0), 1023: ((1 << N_THERMO) - 1, 15)}
    async for code in _iter_codes(dut, (0, 1023)):
        want_t, want_b = literals[code]
        where = f"at boundary code {code}"
        got_t = _read(dut.t_q, "t_q", where)
        got_b = _read(dut.b_q, "b_q", where)
        assert got_t == want_t, (
            f"t_q mismatch {where}: got {got_t:#018x}, want {want_t:#018x}"
        )
        assert got_b == want_b, f"b_q mismatch {where}: got {got_b}, want {want_b}"
