"""
Tests for ACF Stability Physics Module
"""

import pytest

from acf.model4d.physics.stability import StabilityPhysics


def test_brunt_vaisala():
    value = StabilityPhysics.brunt_vaisala_frequency(0.01)

    assert round(value, 2) == 0.02


def test_static_stability():

    value = StabilityPhysics.static_stability(0.01)

    assert round(value, 4) == 0.0003


def test_richardson_number():

    value = StabilityPhysics.richardson_number(
        0.000326,
        0.01
    )

    assert round(value, 2) == 3.26


def test_stable_classification():

    result = StabilityPhysics.classify_stability(
        0.05
    )

    assert result == "stable"


def test_neutral_classification():

    result = StabilityPhysics.classify_stability(
        0.02
    )

    assert result == "neutral"


def test_unstable_classification():

    result = StabilityPhysics.classify_stability(
        0.005
    )

    assert result == "unstable"


def test_temperature_error():

    with pytest.raises(ValueError):

        StabilityPhysics.brunt_vaisala_frequency(
            0.01,
            temperature=0
        )


def test_gradient_error():

    with pytest.raises(ValueError):

        StabilityPhysics.brunt_vaisala_frequency(
            -0.01
        )


def test_zero_wind_shear():

    with pytest.raises(ValueError):

        StabilityPhysics.richardson_number(
            0.001,
            0
        )


def test_default_temperature():

    value = StabilityPhysics.brunt_vaisala_frequency(
        0.01
    )

    assert value > 0
