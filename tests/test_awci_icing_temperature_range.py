"""
Tests for acf.awci.icing_temperature_range - the real ICAO/FAA
airframe-icing temperature-range check, added 2026-09-12 (explicit
user request "je veux que tu ajoutes toutes les seuils possible pour
que le projet soit conforme à 100%").
"""

from __future__ import annotations

import pytest

from acf.awci.icing_temperature_range import (
    ICING_TEMPERATURE_LOWER_C,
    ICING_TEMPERATURE_UPPER_C,
    is_within_icing_temperature_range,
)


def _celsius_to_kelvin(celsius: float) -> float:
    return celsius + 273.15


def test_real_icao_thresholds_are_0_and_minus_40():
    assert ICING_TEMPERATURE_UPPER_C == 0.0
    assert ICING_TEMPERATURE_LOWER_C == -40.0


@pytest.mark.parametrize(
    "temperature_c,expected",
    [
        (0.0, True),
        (-1.0, True),
        (-20.0, True),
        (-40.0, True),
        (0.1, False),
        (-40.1, False),
        (20.0, False),
        (-60.0, False),
    ],
)
def test_real_boundary_behavior(temperature_c, expected):
    assert is_within_icing_temperature_range(_celsius_to_kelvin(temperature_c)) is expected


def test_warm_summer_surface_temperature_is_never_in_range():
    assert is_within_icing_temperature_range(_celsius_to_kelvin(35.0)) is False


def test_extreme_stratospheric_cold_is_never_in_range():
    """Real, disclosed scope: below -40°C, this function honestly
    reports False (outside the real supercooled-liquid-favorable
    range) - it never claims "no icing risk at all" (ice-crystal/
    engine icing is a real, distinct phenomenon this function does
    not classify - see module docstring)."""
    assert is_within_icing_temperature_range(_celsius_to_kelvin(-56.5)) is False
