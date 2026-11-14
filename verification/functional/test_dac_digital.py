"""cocotb regression for `dac_digital`, run through `klt functional-verification`.

Ports the four checks of `verification/rtl/tb_dac_digital.v` (which stays in
place as the item-1 design sanity check) to the cocotb path, because T1 items 5
and 7 accept a `klt functional-verification` JSON report and only this path
produces one. The same module runs against the RTL (`rtl/`) and against the
synthesized gate-level netlist (`synth/out/dac_digital/dac_digital_synth.v`);
the two requests differ only in `sources`.

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

This is a **zero-delay functional run**: no SDF is annotated, no timing is
checked, and no signoff-manifest item is cited. See `verification/README.md`.

Sampling discipline (a real failure observed while building this suite): the
flop bank has no reset -- at gate level the 67 `dffq_1` flops are reset-less by
construction -- so `t_q`/`b_q` are X until the first settled capturing edge.
Every test therefore starts with `_bringup()`, which runs past the first edges
with a known `din`, and drives `din` on the falling edge so it is stable across
the rising edge that captures it.
"""

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import FallingEdge, RisingEdge, Timer

CODES = 1024
N_THERMO = 63
CLK_PERIOD_NS = 10
SETTLE_NS = 1


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
    """Start the clock and leave the DUT settled, just after a falling edge.

    Runs two rising edges with `din = 0` held: the first clocks the flop bank
    out of its reset-less X state, the second captures a known `din`. Returning
    on the falling edge means every caller can write `din` and have it stable
    well before the rising edge that captures it.
    """
    cocotb.start_soon(Clock(dut.clk, CLK_PERIOD_NS, units="ns").start())
    dut.din.value = 0
    await RisingEdge(dut.clk)
    await RisingEdge(dut.clk)
    await FallingEdge(dut.clk)
    await Timer(SETTLE_NS, units="ns")


async def _apply(dut, code):
    """Present `code`, clock it in, and return just after it has settled."""
    dut.din.value = code
    await RisingEdge(dut.clk)
    await Timer(SETTLE_NS, units="ns")


@cocotb.test()
async def test_thermometer_and_binary_all_codes(dut):
    """All 1024 codes: thermometer value and binary bits, read in one cycle."""
    await _bringup(dut)
    for code in range(CODES):
        await _apply(dut, code)
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
        await FallingEdge(dut.clk)


@cocotb.test()
async def test_major_carry_flips_one_line(dut):
    """Each major carry flips exactly one thermometer line.

    Sweeps in code order so `prev_t` is the previous code's settled value, as
    the Verilog bench's loop does.
    """
    await _bringup(dut)
    prev_t = None
    carries = 0
    for code in range(CODES):
        await _apply(dut, code)
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
        await FallingEdge(dut.clk)
    assert carries == 63, f"expected 63 major carries, exercised {carries}"


@cocotb.test()
async def test_one_cycle_latency(dut):
    """Outputs change on the edge *after* `din`, never the same edge."""
    await _bringup(dut)
    # Each pair changes both the thermometer word and the binary bits, so a
    # zero-cycle (combinational) or two-cycle path is visible in both fields.
    for first, second in ((0, 1023), (1023, 0), (0x00F, 0x010), (0x3F0, 0x00F)):
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


@cocotb.test()
async def test_boundary_codes(dut):
    """Codes 0 and 1023 against literal expectations.

    Deliberately does not call `expected_thermo` / `expected_binary`: a bug in
    those helpers would hide in the sweeping tests but not here.
    """
    await _bringup(dut)
    for code, want_t, want_b in (
        (0, 0, 0),
        (1023, (1 << N_THERMO) - 1, 15),
    ):
        await _apply(dut, code)
        where = f"at boundary code {code}"
        got_t = _read(dut.t_q, "t_q", where)
        got_b = _read(dut.b_q, "b_q", where)
        assert got_t == want_t, (
            f"t_q mismatch {where}: got {got_t:#018x}, want {want_t:#018x}"
        )
        assert got_b == want_b, f"b_q mismatch {where}: got {got_b}, want {want_b}"
        await FallingEdge(dut.clk)
