"""
Atmospheric Complexity Framework (ACF)

Test suite for acf.science.parcel_ascent.ParcelAscentEngine.

Fills the gap explicitly flagged in radiosonde.py's SoundingProfile
docstring: CAPE/CIN require a real parcel-ascent model, not a naive
buoyancy integral against the environmental trace. These tests verify
the MetPy-backed parcel ascent against known physical behavior: an
unstable spring-severe-weather-type sounding must produce substantial
positive CAPE and a real LFC/EL, while a stable sounding must produce
exactly zero CAPE and no LFC/EL at all (not a fabricated small number).
"""

from acf.science.parcel_ascent import ParcelAscentEngine
from acf.science.radiosonde import SoundingLevel, SoundingProfile


def _unstable_sounding() -> SoundingProfile:
    """A synthetic but physically realistic unstable (severe-weather-type) sounding."""
    levels = [
        SoundingLevel(1000, 100, 24.0, 20.0),
        SoundingLevel(925, 750, 20.0, 16.0),
        SoundingLevel(850, 1500, 16.0, 12.0),
        SoundingLevel(700, 3000, 8.0, 2.0),
        SoundingLevel(500, 5800, -8.0, -20.0),
        SoundingLevel(400, 7200, -20.0, -35.0),
        SoundingLevel(300, 9200, -40.0, -50.0),
        SoundingLevel(250, 10400, -52.0, -60.0),
        SoundingLevel(200, 11800, -56.0, -65.0),
        SoundingLevel(150, 13600, -58.0, -68.0),
        SoundingLevel(100, 16200, -56.0, -70.0),
    ]
    return SoundingProfile(levels)


def _stable_sounding() -> SoundingProfile:
    """A synthetic stable, dry sounding with no instability anywhere."""
    levels = [
        SoundingLevel(1000, 100, 10.0, 8.0),
        SoundingLevel(925, 750, 8.0, 5.0),
        SoundingLevel(850, 1500, 5.0, 1.0),
        SoundingLevel(700, 3000, -2.0, -8.0),
        SoundingLevel(500, 5800, -18.0, -28.0),
        SoundingLevel(300, 9200, -45.0, -55.0),
    ]
    return SoundingProfile(levels)


def test_surface_based_cape_cin_unstable_sounding():
    result = ParcelAscentEngine.surface_based_cape_cin(_unstable_sounding())
    # A classic moderately-unstable spring severe-weather sounding: real
    # SBCAPE values for such profiles are typically in the hundreds to
    # low thousands of J/kg.
    assert 500.0 < result["cape_j_kg"] < 3000.0
    assert result["cin_j_kg"] < 0.0


def test_surface_based_cape_cin_stable_sounding_is_genuinely_zero():
    """A stable sounding must report exactly 0 CAPE - not a small fabricated positive number."""
    result = ParcelAscentEngine.surface_based_cape_cin(_stable_sounding())
    assert result["cape_j_kg"] == 0.0
    assert result["cin_j_kg"] == 0.0


def test_lfc_and_el_present_for_unstable_sounding():
    result = ParcelAscentEngine.lfc_and_el(_unstable_sounding())
    assert result["lfc_pressure_hpa"] is not None
    assert result["el_pressure_hpa"] is not None
    # LFC must be below (higher pressure than) the EL in the atmosphere.
    assert result["lfc_pressure_hpa"] > result["el_pressure_hpa"]


def test_lfc_and_el_absent_for_stable_sounding():
    """No LFC/EL exists for a sounding with no positive buoyancy anywhere - honestly None, not a guess."""
    result = ParcelAscentEngine.lfc_and_el(_stable_sounding())
    assert result["lfc_pressure_hpa"] is None
    assert result["el_pressure_hpa"] is None


def test_mixed_layer_cape_is_less_than_surface_based_for_this_sounding():
    """
    Mixing in drier/cooler air from just above the surface should
    reduce buoyancy relative to using the single surface observation
    directly, for a sounding with a moist, well-mixed-looking surface
    layer like this one.
    """
    profile = _unstable_sounding()
    sbcape = ParcelAscentEngine.surface_based_cape_cin(profile)["cape_j_kg"]
    mlcape = ParcelAscentEngine.mixed_layer_cape_cin(profile)["mlcape_j_kg"]
    assert 0.0 < mlcape < sbcape


def test_severe_weather_indices_are_physically_ordered():
    """
    For this classic unstable-sounding shape: K-Index and Total Totals
    should read as significant-severe-weather-favorable (K-Index > 25,
    Total Totals > 40 per the standard AMS/NOAA thresholds), and the
    Showalter/Lifted indices should be negative-to-near-zero
    (indicating instability), consistent with the real positive SBCAPE
    computed above for the same sounding.
    """
    result = ParcelAscentEngine.severe_weather_indices(_unstable_sounding())
    assert result["k_index_c"] > 25.0
    assert result["total_totals_c"] > 40.0
    assert result["lifted_index_c"] < 0.0


def test_full_report_combines_all_diagnostics():
    report = ParcelAscentEngine.full_report(_unstable_sounding())
    for key in (
        "cape_j_kg",
        "cin_j_kg",
        "lfc_pressure_hpa",
        "el_pressure_hpa",
        "mucape_j_kg",
        "mlcape_j_kg",
        "k_index_c",
        "total_totals_c",
    ):
        assert key in report
