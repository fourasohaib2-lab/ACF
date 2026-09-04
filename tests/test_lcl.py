import pytest

from acf.science.lcl import LCL


def test_lcl():
    h = LCL.calculate(
        30.0,
        20.0,
    )

    assert h == 1250.0


def test_saturated():
    assert (
        LCL.calculate(
            20.0,
            20.0,
        )
        == 0.0
    )


def test_invalid():
    with pytest.raises(ValueError):
        LCL.calculate(
            20.0,
            25.0,
        )


def test_tolerates_a_real_floating_point_overshoot_at_exact_saturation():
    """Regression guard (2026-09-04): a genuinely saturated point can
    have a dewpoint a few ULPs above the input temperature due to real
    floating-point rounding upstream - same reasoning as
    EquivalentPotentialTemperature.lcl_temperature_bolton_1980()'s own
    identical fix. Must not raise, and must give the same real height
    as exact saturation (0.0)."""
    assert LCL.calculate(20.0, 20.0 + 1e-12) == 0.0


def test_still_rejects_a_real_meaningful_dewpoint_excess():
    with pytest.raises(ValueError):
        LCL.calculate(20.0, 20.001)


def test_bolton_close_to_espy_approximation():
    # For a typical 10 degC dewpoint depression, Bolton's physically
    # grounded height should be in the same ballpark as Espy's fixed
    # ~125 m/degC rule (within roughly 5%), not wildly different.
    espy = LCL.calculate(30.0, 20.0)
    bolton = LCL.calculate_bolton_celsius(30.0, 20.0)
    assert bolton == pytest.approx(espy, rel=0.05)


def test_bolton_saturated_air_gives_zero_height():
    h = LCL.calculate_bolton_celsius(20.0, 20.0)
    assert h == pytest.approx(0.0, abs=1e-6)


def test_bolton_kelvin_and_celsius_wrappers_agree():
    assert LCL.calculate_bolton(303.15, 293.15) == pytest.approx(LCL.calculate_bolton_celsius(30.0, 20.0))


def test_bolton_invalid_dewpoint_exceeds_temperature():
    with pytest.raises(ValueError):
        LCL.calculate_bolton_celsius(20.0, 25.0)
