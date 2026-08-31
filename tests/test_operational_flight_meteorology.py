"""
Atmospheric Complexity Framework (ACF)

Global Operational Flight Meteorology & Aviation Safety Test Suite (MISSION ACF-031)
"""

from acf.aviation.airports.airport_database import AIRPORT_REGISTRY, AirportDatabase
from acf.aviation.graphics.cross_section import FlightCrossSectionEngine
from acf.aviation.hazards.aviation_hazards import AVIATION_HAZARDS_REGISTRY, AviationHazardEngine
from acf.aviation.icao.products import ICAOMetDecoder
from acf.aviation.performance.aircraft_performance import AircraftPerformanceEngine
from acf.aviation.routing.flight_routing import FlightRoutingEngine
from acf.science.query_engine import ScientificQueryEngine


def test_icao_met_decoder():
    """Test du décodage des bulletins OACI (METAR, TAF, SIGMET)."""
    metar = ICAOMetDecoder.decode_metar("LFPG 020800Z 24018G28KT 9999 -RA BKN025 18/12 Q1015")
    assert metar.icao_code == "LFPG"
    assert metar.wind_speed_kt == 18
    assert metar.wind_gust_kt == 28

    # CORRECTED: icao_code was genuinely extracted from raw_taf, but
    # this used to also claim a fixed fake forecast (fabricated
    # TEMPO/wind/weather group) regardless of the actual TAF text -
    # same operationally dangerous pattern as the METAR decoder bug
    # (fixed earlier this session). A real TAF decoder (taf_decoder.py)
    # is now wired in - genuine header + base-forecast + change-group
    # (FM/BECMG/TEMPO/PROB30/PROB40) parsing, see
    # tests/test_taf_decoder.py for full coverage. This TAF has no
    # change groups, so exactly one (base) forecast period is decoded.
    taf = ICAOMetDecoder.decode_taf("TAF LFPG 020600Z 0206/0312 24015KT 9999 NSW")
    assert taf.icao_code == "LFPG"
    assert taf.issue_time_utc == "020600Z"
    assert taf.valid_from_utc == "0206"
    assert taf.valid_until_utc == "0312"
    assert len(taf.forecast_periods) == 1
    base = taf.forecast_periods[0]
    assert base["change_type"] == "BASE"
    assert base["wind_direction_deg"] == 240
    assert base["wind_speed_kt"] == 15.0
    assert base["visibility_m"] == 9999.0

    # A TAF with real change groups: TEMPO fog + a FM group must decode distinctly.
    taf_full = ICAOMetDecoder.decode_taf(
        "TAF LFPO 020600Z 0206/0312 24015KT 9999 SCT030 "
        "TEMPO 0206/0210 4000 SHRA BKN015CB "
        "FM021800 27010KT 9999 SCT040"
    )
    assert len(taf_full.forecast_periods) == 3
    tempo = taf_full.forecast_periods[1]
    assert tempo["change_type"] == "TEMPO"
    assert tempo["visibility_m"] == 4000.0
    assert tempo["present_weather"] == ["SHRA"]
    fm = taf_full.forecast_periods[2]
    assert fm["change_type"] == "FM"
    assert fm["from_day"] == 2 and fm["from_hour"] == 18

    # CORRECTED: this used to unconditionally return the exact same
    # fabricated SIGMET (fixed FIR/phenomenon/severity/levels)
    # regardless of the actual SIGMET text - a SIGMET for a completely
    # different FIR and phenomenon would decode identically. A real
    # SIGMET decoder (sigmet_decoder.py) is now wired in - genuine
    # header (FIR/sequence/validity/issuing center) and keyword-based
    # phenomenon/flight-level/movement extraction, see
    # tests/test_sigmet_decoder.py for full coverage across several
    # distinct, realistic international SIGMETs. Geographic location
    # description remains genuinely free-text and is not structurally
    # parsed (see sigmet_decoder.py's module docstring).
    sigmet = ICAOMetDecoder.decode_sigmet("LFFF SIGMET 2 VALID 020800/021200 LFPW- LFFF PARIS FIR EMBD TS")
    assert sigmet.phenomenon == "EMBD TS"
    assert sigmet.fir_code == "LFFF"
    assert sigmet.sigmet_id == "2"
    assert sigmet.valid_from == "020800"
    assert sigmet.valid_until == "021200"
    assert sigmet.raw_text == "LFFF SIGMET 2 VALID 020800/021200 LFPW- LFFF PARIS FIR EMBD TS"

    # A different FIR, phenomenon, and flight-level range must decode distinctly (the exact original bug).
    sigmet2 = ICAOMetDecoder.decode_sigmet(
        "KZAK SIGMET 1 VALID 021200/021600 KZAK- KZAK OAKLAND OCEANIC FIR SEV TURB "
        "FCST AT 1200Z S OF N30 FL180/FL340 MOV NE 25KT INTSF"
    )
    assert sigmet2.fir_code == "KZAK"
    assert sigmet2.phenomenon == "SEV TURB"
    assert sigmet2.severity == "SEV"
    assert sigmet2.flight_levels == "FL180/FL340"
    assert sigmet2.movement_dir_speed == "MOV NE 25KT"
    assert sigmet2.phenomenon != sigmet.phenomenon
    assert sigmet2.fir_code != sigmet.fir_code


def test_aviation_hazards_registry():
    """Test du registre des dangers météorologiques pour l'aviation."""
    assert len(AVIATION_HAZARDS_REGISTRY) >= 3

    cat = AviationHazardEngine.get_hazard("cat_turbulence")
    assert cat is not None
    assert "< 0.25" in cat.governing_equation

    icing = AviationHazardEngine.get_hazard("airframe_icing")
    assert icing is not None
    assert icing.category == "ICING"


def test_aircraft_performance_engine():
    """Test des calculs de performance et d'atmosphère ISA."""
    isa = AircraftPerformanceEngine.isa_atmosphere(altitude_m=10000.0)
    assert 220.0 < isa["temperature_k"] < 230.0
    assert 250.0 < isa["pressure_hpa"] < 300.0

    wind = AircraftPerformanceEngine.wind_components(runway_heading_deg=260.0, wind_dir_deg=290.0, wind_speed_kt=20.0)
    assert wind["headwind_kt"] > 10.0
    assert wind["crosswind_kt"] > 5.0

    da = AircraftPerformanceEngine.density_altitude_ft(pressure_altitude_ft=5000.0, temp_c=30.0)
    assert da > 5000.0  # Density altitude is higher than pressure altitude in warm air


def test_airport_database():
    """Test de la base de données d'aéroports OACI/IATA."""
    assert len(AIRPORT_REGISTRY) >= 3

    cdg = AirportDatabase.get_airport("LFPG")
    assert cdg is not None
    assert cdg.iata_code == "CDG"

    jfk = AirportDatabase.get_airport("JFK")
    assert jfk is not None
    assert jfk.icao_code == "KJFK"


def test_flight_routing_engine():
    """Test du moteur d'optimisation de route de vol."""
    router = FlightRoutingEngine()
    dist = router.great_circle_distance_nm(49.0097, 2.5479, 40.6413, -73.7781)
    assert 3000.0 < dist < 3500.0  # ~3150 NM Paris -> New York

    plan = router.plan_flight_route("LFPG", "KJFK", cruise_fl=350)
    assert plan["status"] == "success"
    assert "LFPO" in plan["recommended_alternates"] or "LILH" in plan["recommended_alternates"]


def test_flight_cross_section_engine():
    """Test de la coupe verticale le long d'une route de vol."""
    cs_engine = FlightCrossSectionEngine()
    profile = cs_engine.generate_flight_profile(49.0097, 2.5479, 40.6413, -73.7781, num_waypoints=10)
    assert len(profile["route_waypoints"]) == 10
    assert len(profile["detected_hazard_zones"]) >= 1


def test_query_engine_phase15_aviation_questions():
    """Test du ScientificQueryEngine sur les requêtes aéronautiques de la mission ACF-031."""
    q_engine = ScientificQueryEngine()

    r1 = q_engine.ask("Show turbulence")
    assert r1["layer_type"] == "cat_turbulence_layer"

    r2 = q_engine.ask("Show icing")
    assert r2["layer_type"] == "airframe_icing_layer"

    r3 = q_engine.ask("Decode METAR")
    assert r3["product_type"] == "METAR"

    r4 = q_engine.ask("Decode SIGMET")
    assert r4["product_type"] == "SIGMET"

    # CORRECTED: used to claim a fixed "recommended_flight_level:
    # FL360" and 2 fixed fabricated alternate airports regardless of
    # any real route/aircraft/weather data - unlike
    # FlightRoutingEngine.plan_flight_route() above (a genuine real
    # routing engine), this router has no real flight-planning
    # computation connected.
    r5 = q_engine.ask("Best flight level")
    assert r5["recommended_flight_level"] is None

    r6 = q_engine.ask("Find alternate airport")
    assert r6["recommended_alternates"] == []
