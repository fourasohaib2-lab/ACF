import math

from acf.science.saturation_vapor_pressure import SaturationVaporPressure


def test_tetens_0c():
    # At 0°C, es should be ≈ 6.112 hPa
    es = SaturationVaporPressure.calculate_tetens(273.15, is_kelvin=True)
    assert round(es, 3) == 6.112


def test_tetens_20c():
    # At 20°C, es should be ≈ 23.37 hPa
    es = SaturationVaporPressure.calculate_tetens(293.15, is_kelvin=True)
    assert round(es, 2) == 23.37


def test_tetens_celsius():
    # At 20°C directly
    es = SaturationVaporPressure.calculate_tetens(20.0, is_kelvin=False)
    assert round(es, 2) == 23.37


def test_goff_gratch_no_longer_a_disguised_tetens_alias():
    """
    CORRECTED: calculate_golf() used to just call calculate() (Tetens)
    again - not Goff-Gratch at all, despite its name and its own
    docstring's "more accurate for low temperatures" claim. Now a real,
    distinct implementation - must differ numerically from Tetens.
    """
    tetens = SaturationVaporPressure.calculate(-40.0, is_kelvin=False)
    goff_gratch = SaturationVaporPressure.calculate_golf(-40.0, is_kelvin=False)
    assert not math.isclose(tetens, goff_gratch, rel_tol=1e-9)


def test_goff_gratch_exact_at_steam_point():
    """At the defining steam-point temperature (373.15 K), es must equal exactly 1013.25 hPa."""
    es = SaturationVaporPressure.calculate_golf(373.15, is_kelvin=True)
    assert math.isclose(es, 1013.25, rel_tol=1e-9)


def test_goff_gratch_matches_known_reference_values():
    # Standard reference values (WMO Goff-Gratch / CIMO Guide), hPa.
    assert round(SaturationVaporPressure.calculate_golf(0.0, is_kelvin=False), 2) == 6.11
    assert round(SaturationVaporPressure.calculate_golf(20.0, is_kelvin=False), 2) == 23.37


def test_goff_gratch_accepts_kelvin_and_celsius_consistently():
    from_kelvin = SaturationVaporPressure.calculate_golf(293.15, is_kelvin=True)
    from_celsius = SaturationVaporPressure.calculate_golf(20.0, is_kelvin=False)
    assert math.isclose(from_kelvin, from_celsius, rel_tol=1e-9)
