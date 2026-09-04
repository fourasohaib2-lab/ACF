import pytest

from acf.science.equivalent_potential_temperature import (
    EquivalentPotentialTemperature,
)


def test_thetae():
    thetae = EquivalentPotentialTemperature.calculate(
        300.0,
        0.010,
    )

    assert thetae > 300.0


def test_zero_humidity():
    thetae = EquivalentPotentialTemperature.calculate(
        300.0,
        0.0,
    )

    assert thetae == 300.0


def test_invalid_temperature():
    with pytest.raises(ValueError):
        EquivalentPotentialTemperature.calculate(
            0.0,
            0.01,
        )


def test_invalid_humidity():
    with pytest.raises(ValueError):
        EquivalentPotentialTemperature.calculate(
            300.0,
            -0.1,
        )


def test_bolton_1980_warmer_than_temperature():
    # A moist parcel's theta_e must exceed its actual temperature
    # (latent heat content raises the equivalent temperature).
    thetae = EquivalentPotentialTemperature.calculate_bolton_1980(
        temperature_k=300.0,
        dewpoint_k=290.0,
        pressure_hpa=1000.0,
    )
    assert thetae > 300.0
    # Sanity range for a fairly moist mid-latitude summer profile.
    assert 300.0 < thetae < 360.0


def test_bolton_1980_dry_air_close_to_potential_temperature():
    # Very dry air (large T-Td spread): theta_e should be close to
    # (but not below) the dry potential temperature at the same level.
    from acf.science.potential_temperature import PotentialTemperature

    theta = PotentialTemperature.calculate(300.0, 1000.0)
    thetae = EquivalentPotentialTemperature.calculate_bolton_1980(
        temperature_k=300.0,
        dewpoint_k=250.0,
        pressure_hpa=1000.0,
    )
    assert thetae >= theta - 1.0  # allow tiny numerical slack


def test_bolton_1980_invalid_dewpoint_exceeds_temperature():
    with pytest.raises(ValueError):
        EquivalentPotentialTemperature.calculate_bolton_1980(
            temperature_k=290.0,
            dewpoint_k=295.0,
            pressure_hpa=1000.0,
        )


def test_bolton_1980_tolerates_a_real_floating_point_overshoot_at_exact_saturation():
    """Regression guard (2026-09-04, found smoke-testing the ACF
    Scientific Workstation's real level-slider sweep): a genuinely
    saturated point (relative humidity clipped to exactly 100%) can
    round-trip through the Magnus-Tetens dewpoint inversion a few ULPs
    ABOVE the input temperature (~1.8e-15 K verified on a real solver
    column) - a real IEEE-754 rounding artifact, not a genuine physical
    violation. Must not raise."""
    result = EquivalentPotentialTemperature.calculate_bolton_1980(
        temperature_k=283.5012090757036,
        dewpoint_k=283.5012090757036 + 1e-15,
        pressure_hpa=1013.25,
    )
    assert result > 0.0


def test_bolton_1980_still_rejects_a_real_meaningful_dewpoint_excess():
    """The real floating-point tolerance must not mask a genuine
    caller-input error - an excess many orders of magnitude larger
    than realistic floating-point noise still raises."""
    with pytest.raises(ValueError):
        EquivalentPotentialTemperature.calculate_bolton_1980(
            temperature_k=290.0,
            dewpoint_k=290.001,
            pressure_hpa=1000.0,
        )


def test_bolton_1980_invalid_temperature():
    with pytest.raises(ValueError):
        EquivalentPotentialTemperature.calculate_bolton_1980(
            temperature_k=0.0,
            dewpoint_k=-1.0,
            pressure_hpa=1000.0,
        )


def test_bolton_1980_invalid_pressure():
    with pytest.raises(ValueError):
        EquivalentPotentialTemperature.calculate_bolton_1980(
            temperature_k=300.0,
            dewpoint_k=290.0,
            pressure_hpa=0.0,
        )
