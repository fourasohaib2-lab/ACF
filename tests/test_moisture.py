"""
Tests for acf.science.moisture.Moisture (facade over existing,
individually-tested moisture modules — no new formulas here).
"""

import pytest

from acf.science.moisture import Moisture


def test_saturation_vapor_pressure_matches_underlying_module():
    from acf.science.saturation_vapor_pressure import SaturationVaporPressure

    assert Moisture.saturation_vapor_pressure(300.0) == SaturationVaporPressure.calculate(300.0)


def test_relative_humidity_bounded():
    rh = Moisture.relative_humidity(vapor_pressure_hpa=10.0, saturation_vapor_pressure_hpa=20.0)
    assert rh == pytest.approx(0.5)


def test_mixing_ratio_and_specific_humidity_round_trip():
    q = 0.01
    w = Moisture.mixing_ratio(q)
    q_back = Moisture.specific_humidity(w)
    assert q_back == pytest.approx(q, rel=1e-6)


def test_dewpoint_below_temperature():
    td = Moisture.dewpoint(temperature_c=25.0, relative_humidity_percent=60.0)
    assert td < 25.0


def test_relative_humidity_from_temperature_chain():
    rh = Moisture.relative_humidity_from_temperature(
        specific_humidity=0.01, pressure_hpa=1000.0, temperature_k=300.0
    )
    assert 0.0 <= rh <= 1.0


def test_saturation_mixing_ratio_positive():
    from acf.science.saturation_vapor_pressure import SaturationVaporPressure

    es = SaturationVaporPressure.calculate(290.0)
    ws = Moisture.saturation_mixing_ratio(es, 1000.0)
    assert ws > 0.0
