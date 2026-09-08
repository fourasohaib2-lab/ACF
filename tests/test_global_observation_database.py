"""
Atmospheric Complexity Framework (ACF)

Global Observation Database, WMO Standards & Forward Operators Test Suite (MISSION ACF-025)
"""

import pytest

from acf.science.encyclopedia.registry import EncyclopediaRegistry
from acf.science.observations.forward_operators import (
    observe_gnss_zenith_wet_delay_zwd,
    observe_radar_doppler_radial_velocity,
    observe_radar_reflectivity_zh,
    observe_temperature_2m,
)
from acf.science.observations.quality_control import (
    ObservationQCFlags,
    background_check,
    buddy_check,
    gross_error_check,
    range_check,
    temporal_consistency_check,
)
from acf.science.observations.wmo_code_tables import decode_metar_visibility, decode_wmo_present_weather
from acf.science.query_engine import ScientificQueryEngine


def test_quality_control_algorithms():
    """Test des algorithmes de contrôle qualité d'observation WMO/NWP."""
    assert gross_error_check(295.15, 180.0, 330.0) == ObservationQCFlags.PASSED
    assert gross_error_check(350.0, 180.0, 330.0) == ObservationQCFlags.FAILED

    assert range_check(295.15, 200.0, 320.0) == ObservationQCFlags.PASSED
    assert range_check(330.0, 200.0, 320.0) == ObservationQCFlags.SUSPECT

    assert temporal_consistency_check(295.0, 290.0, 3600.0, 0.002) == ObservationQCFlags.PASSED
    assert temporal_consistency_check(310.0, 290.0, 60.0, 0.01) == ObservationQCFlags.FAILED

    flag, innov = background_check(obs_val=295.0, model_bg_val=294.0, obs_error=1.0, bg_error=1.0, threshold_sigma=3.0)
    assert flag == ObservationQCFlags.PASSED
    assert innov == 1.0

    assert buddy_check(295.0, [294.5, 295.2, 294.8, 295.1]) == ObservationQCFlags.PASSED


def test_forward_operators():
    """Test des opérateurs d'observation H(x)."""
    t2m = observe_temperature_2m(surface_temp_k=300.0, height_m=2.0)
    assert 299.9 < t2m < 300.0

    zh = observe_radar_reflectivity_zh(q_r_kg_kg=0.002)
    assert zh > 30.0

    vr = observe_radar_doppler_radial_velocity(u_ms=10.0, v_ms=0.0, w_ms=0.0, azimuth_deg=90.0, elevation_deg=0.0)
    assert abs(vr - 10.0) < 1e-4

    zwd = observe_gnss_zenith_wet_delay_zwd(pwv_mm=30.0)
    assert 0.15 < zwd < 0.25


def test_wmo_decoders():
    """Test des décodeurs de tables de codes WMO/METAR."""
    w95 = decode_wmo_present_weather(95)
    assert "Orage" in w95 or "Thunderstorm" in w95

    v9999 = decode_metar_visibility("9999")
    assert v9999 == 10000.0

    v10sm = decode_metar_visibility("10SM")
    assert v10sm > 16000.0

    v0500 = decode_metar_visibility("0500")
    assert v0500 == 500.0

    # An unparseable code must never be silently reported as "10km+
    # visibility" (a plausible-but-fabricated value) - it must raise.
    with pytest.raises(ValueError):
        decode_metar_visibility("GARBAGE")

    with pytest.raises(ValueError):
        decode_metar_visibility("ABCSM")


def test_query_engine_phase14_observation_questions():
    """Test le ScientificQueryEngine sur les questions d'observation de la mission ACF-025."""
    engine = ScientificQueryEngine()

    # 1. Which observations measure humidity?
    r1 = engine.ask("Which observations measure humidity?")
    assert "observing_systems" in r1
    assert any("Radiosondages" in s or "GNSS" in s for s in r1["observing_systems"])

    # 2. Which radar variables detect hail?
    r2 = engine.ask("Which radar variables detect hail?")
    assert "polarimetric_radar_signatures" in r2
    assert "Reflectivity Z_H" in r2["polarimetric_radar_signatures"]

    # 3. Which observations are assimilated by IFS?
    r3 = engine.ask("Which observations are assimilated by IFS?")
    assert "assimilated_observation_types" in r3
    assert any("Radiance" in s or "AMDAR" in s for s in r3["assimilated_observation_types"])

    # 4. How is METAR visibility encoded?
    r4 = engine.ask("How is METAR visibility encoded?")
    assert "examples" in r4
    assert "9999" in r4["examples"]

    # 5. Which observations provide CAPE inputs?
    r5 = engine.ask("Which observations provide CAPE inputs?")
    assert "input_observations" in r5
    assert any("Radiosondages" in s for s in r5["input_observations"])

    # 6. Explain radiosonde quality control
    r6 = engine.ask("Explain radiosonde quality control")
    assert "qc_steps" in r6
    assert "Hydrostatic test" in r6["qc_steps"]


def test_global_registry_observation_entries():
    """Vérifie que l'encyclopédie répertorie les nouveaux systèmes d'observation."""
    all_entries = EncyclopediaRegistry.get_all_entries()
    keys = [e.key for e in all_entries]

    assert "synop_surface_observation" in keys
    assert "ship_buoy_surface_observation" in keys
    assert "metar_speci_aviation_observation" in keys
    assert "amdar_acars_aircraft_observation" in keys
    assert "radiosonde_temp_observation" in keys
    assert "gps_radio_occultation_gnss_pwv" in keys
