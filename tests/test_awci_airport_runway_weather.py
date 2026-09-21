"""Tests for the new awci.airport.runway/weather modules, built while
working through the full remaining-gaps list ("On les attaque toutes
un par un") - the runway.py/weather.py files named in
docs/architecture/awci_reference_architecture.md section 12 ("Airport
Operations... Chain: Weather -> Airport -> Runway -> Operation").

Both modules are real, thin compositions of already-real formulas/
systems (AircraftPerformanceEngine.wind_components(),
parse_runway_heading_magnetic_deg(), ObservationsHub,
classify_ceiling_category(), the real METAR present-weather grammar) -
no new physics or classification scheme is introduced by either
module, verified here against known, hand-computed real values.
"""

from __future__ import annotations

import pytest

from awci.airport.runway import (
    RunwayWindAssessment,
    assess_airport_runways_wind,
    assess_runway_end_wind,
    best_runway_end_for_wind,
)
from awci.airport.weather import (
    AirportWeatherSnapshot,
    build_weather_snapshot,
    describe_present_weather_code,
    real_ceiling_height_ft,
)
from awci.knowledge.icao.live_source import LiveReport, LiveStationBundle
from awci.knowledge.icao.metar_decoder import METARDecoder

# --------------------------------------------------------------------- runway.py


def test_assess_runway_end_wind_direct_headwind():
    """Wind blowing exactly down runway 08 (heading 080) - a real,
    hand-verifiable case: pure headwind, zero crosswind."""
    assessment = assess_runway_end_wind("08", wind_dir_deg=80.0, wind_speed_kt=20.0)
    assert isinstance(assessment, RunwayWindAssessment)
    assert assessment.runway_heading_magnetic_deg == 80.0
    assert assessment.headwind_kt == pytest.approx(20.0, abs=1e-6)
    assert assessment.crosswind_kt == pytest.approx(0.0, abs=1e-6)


def test_assess_runway_end_wind_direct_tailwind():
    assessment = assess_runway_end_wind("08", wind_dir_deg=260.0, wind_speed_kt=20.0)
    assert assessment.headwind_kt == pytest.approx(-20.0, abs=1e-6)


def test_assess_runway_end_wind_pure_crosswind():
    """Wind 90 degrees off runway heading - pure crosswind, zero
    headwind."""
    assessment = assess_runway_end_wind("08", wind_dir_deg=170.0, wind_speed_kt=15.0)
    assert assessment.headwind_kt == pytest.approx(0.0, abs=1e-6)
    assert assessment.crosswind_kt == pytest.approx(15.0, abs=1e-6)
    assert assessment.crosswind_direction == "RIGHT"


def test_assess_runway_end_wind_parses_the_real_runway_heading():
    assessment = assess_runway_end_wind("26L", wind_dir_deg=260.0, wind_speed_kt=10.0)
    assert assessment.runway_heading_magnetic_deg == 260.0


def test_assess_runway_end_wind_rejects_a_malformed_identifier():
    with pytest.raises(ValueError):
        assess_runway_end_wind("XX", wind_dir_deg=100.0, wind_speed_kt=10.0)


def test_assess_airport_runways_wind_covers_every_real_runway_end():
    from awci.knowledge.airports.airport_database import AirportDatabase

    airport = AirportDatabase.get_airport("LFPG")
    expected_ends = {end for runway in airport.runways for end in runway["identifier"].split("/")}
    results = assess_airport_runways_wind("LFPG", wind_dir_deg=250.0, wind_speed_kt=20.0)
    assert set(results) == expected_ends


def test_assess_airport_runways_wind_rejects_an_unknown_airport():
    with pytest.raises(ValueError):
        assess_airport_runways_wind("ZZZZ", wind_dir_deg=100.0, wind_speed_kt=10.0)


def test_best_runway_end_for_wind_picks_the_real_highest_headwind():
    best = best_runway_end_for_wind("LFPG", wind_dir_deg=250.0, wind_speed_kt=20.0)
    all_assessments = assess_airport_runways_wind("LFPG", wind_dir_deg=250.0, wind_speed_kt=20.0)
    assert best.headwind_kt == max(a.headwind_kt for a in all_assessments.values())


def test_reciprocal_runway_ends_have_opposite_headwind_and_equal_crosswind():
    results = assess_airport_runways_wind("LFPG", wind_dir_deg=250.0, wind_speed_kt=20.0)
    a08 = results["08L"]
    a26 = results["26R"]
    assert a08.headwind_kt == pytest.approx(-a26.headwind_kt, abs=1e-6)
    assert a08.crosswind_kt == pytest.approx(a26.crosswind_kt, abs=1e-6)


# --------------------------------------------------------------------- weather.py


_REAL_KJFK_METAR = "KJFK 211251Z 27015G25KT 3SM -RA BKN008 OVC015 12/10 A2985"


def test_real_ceiling_height_ft_picks_the_lowest_bkn_ovc_layer():
    report = METARDecoder.decode(_REAL_KJFK_METAR)
    assert real_ceiling_height_ft(report) == 800.0


def test_real_ceiling_height_ft_ignores_few_and_sct_layers():
    report = METARDecoder.decode("KJFK 211251Z 27015KT 10SM FEW030 SCT060 12/10 A2985")
    assert real_ceiling_height_ft(report) is None


def test_real_ceiling_height_ft_none_when_no_cloud_layers_at_all():
    report = METARDecoder.decode("KJFK 211251Z 27015KT 10SM CAVOK 12/10 A2985")
    assert real_ceiling_height_ft(report) is None


@pytest.mark.parametrize(
    "code,expected_substrings",
    [
        ("-RA", ["Light", "Rain"]),
        ("+TSRA", ["Thunderstorm", "Rain"]),
        ("BR", ["Mist"]),
        ("FZFG", ["Freezing", "Fog"]),
    ],
)
def test_describe_present_weather_code_matches_the_real_wmo_meanings(code, expected_substrings):
    description = describe_present_weather_code(code)
    for substring in expected_substrings:
        assert substring in description


def test_describe_present_weather_code_omits_the_moderate_intensity_word():
    """Moderate has no real prefix character and no real display word
    (present_weather_codes.py's own convention) - a bare "RA" should
    read as just "Rain", not "Moderate, Rain"."""
    assert describe_present_weather_code("RA") == "Rain"


def test_describe_present_weather_code_returns_verbatim_for_unparseable_input():
    assert describe_present_weather_code("NOT-A-REAL-CODE") == "NOT-A-REAL-CODE"


class _FakeHub:
    def __init__(self, bundle: LiveStationBundle) -> None:
        self._bundle = bundle
        self.calls: list[tuple[str, float]] = []

    def fetch_station(self, icao_code: str, timeout: float = 8.0) -> LiveStationBundle:
        self.calls.append((icao_code, timeout))
        return self._bundle


def test_build_weather_snapshot_composes_a_real_decoded_metar():
    report = METARDecoder.decode(_REAL_KJFK_METAR)
    bundle = LiveStationBundle(icao_code="KJFK")
    bundle.metar = LiveReport(raw_text=_REAL_KJFK_METAR, decoded=report)
    hub = _FakeHub(bundle)

    snapshot = build_weather_snapshot("KJFK", hub=hub)
    assert isinstance(snapshot, AirportWeatherSnapshot)
    assert hub.calls == [("KJFK", 8.0)]
    assert snapshot.is_real_data is True
    assert snapshot.ceiling_height_ft == 800.0
    assert snapshot.ceiling_category == "IFR"
    assert snapshot.visibility_m == report.visibility_m
    assert snapshot.present_weather_descriptions == ("Light, Rain",)
    assert snapshot.raw_metar == _REAL_KJFK_METAR


def test_build_weather_snapshot_honestly_reports_a_real_fetch_failure():
    bundle = LiveStationBundle(icao_code="KJFK")
    bundle.metar = LiveReport(error="METAR fetch for KJFK failed: network error")
    hub = _FakeHub(bundle)

    snapshot = build_weather_snapshot("KJFK", hub=hub)
    assert snapshot.is_real_data is False
    assert "network error" in snapshot.status
    assert snapshot.ceiling_height_ft is None
    assert snapshot.ceiling_category is None
    assert snapshot.present_weather_descriptions == ()


def test_build_weather_snapshot_constructs_a_real_default_hub_when_none_supplied(monkeypatch):
    import awci.airport.weather as weather_module

    report = METARDecoder.decode(_REAL_KJFK_METAR)
    bundle = LiveStationBundle(icao_code="KJFK")
    bundle.metar = LiveReport(raw_text=_REAL_KJFK_METAR, decoded=report)
    fake_hub = _FakeHub(bundle)
    monkeypatch.setattr(weather_module, "ObservationsHub", lambda: fake_hub)

    snapshot = weather_module.build_weather_snapshot("KJFK")
    assert snapshot.is_real_data is True
    assert fake_hub.calls == [("KJFK", 8.0)]


# --------------------------------------------------------------------- discipline


def test_weather_module_never_fabricates_a_precipitation_rate():
    """Discipline check: no real classify_precipitation_intensity
    import anywhere in weather.py's actual code - METAR gives no real
    mm/h rate to feed it, and this module's own docstring discloses
    why (that docstring text is what a naive text search would also
    match, so this checks the real module namespace instead)."""
    import awci.airport.weather as weather_module

    assert not hasattr(weather_module, "classify_precipitation_intensity")
