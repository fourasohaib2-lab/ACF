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


def test_specific_humidity_from_relative_humidity_round_trips_with_the_forward_chain():
    """Real inverse-function check: convert q -> RH (existing chain),
    then RH -> q (new chain, added 2026-09-04 for
    acf.awci.archive_field's RESTOR RH-only real fields) and recover
    the same q - both compose the same underlying primitives, just in
    opposite order."""
    q = 0.008
    pressure_hpa = 850.0
    temperature_k = 288.0

    rh_fraction = Moisture.relative_humidity_from_temperature(q, pressure_hpa, temperature_k)
    q_back = Moisture.specific_humidity_from_relative_humidity(rh_fraction * 100.0, pressure_hpa, temperature_k)

    assert q_back == pytest.approx(q, rel=1e-6)


def test_specific_humidity_from_relative_humidity_is_bounded_and_positive():
    q = Moisture.specific_humidity_from_relative_humidity(
        relative_humidity_percent=55.0, pressure_hpa=700.0, temperature_k=280.0
    )
    assert 0.0 < q < 1.0


def test_specific_humidity_from_relative_humidity_increases_with_rh():
    q_low = Moisture.specific_humidity_from_relative_humidity(20.0, 850.0, 290.0)
    q_high = Moisture.specific_humidity_from_relative_humidity(80.0, 850.0, 290.0)
    assert q_high > q_low
