"""
Atmospheric Complexity Framework (ACF)

Master Earth System Library & Query Engine Expansion Test Suite (MISSION ACF-024)
"""

from acf.science.encyclopedia.registry import EncyclopediaRegistry
from acf.science.encyclopedia.chemistry_extended import calculate_leighton_ozone_photoequilibrium, calculate_dry_deposition_velocity
from acf.science.encyclopedia.severe_weather_library import calculate_ehi_index, calculate_integrated_vapor_transport_ivt
from acf.science.encyclopedia.radar_meteorology_library import calculate_specific_differential_phase_kdp
from acf.science.query_engine import ScientificQueryEngine, ask


def test_chemistry_computations():
    """Test des calculs de chimie et dépôts d'aérosols."""
    o3_ppb = calculate_leighton_ozone_photoequilibrium(j_no2=8e-3, no2_ppb=20.0, no_ppb=5.0, k_o3_no=1.8e-14)
    assert o3_ppb > 0.0

    vd = calculate_dry_deposition_velocity(ra_s_m=50.0, rb_s_m=20.0, rc_s_m=100.0)
    assert 0.001 < vd < 0.05


def test_severe_weather_computations():
    """Test des calculs de temps violent et rivières atmosphériques."""
    ehi = calculate_ehi_index(cape_j_kg=2500.0, sreh_m2_s2=250.0)
    assert ehi > 3.0

    ivt = calculate_integrated_vapor_transport_ivt(q_kg_kg=0.012, u_ms=25.0, v_ms=10.0, dp_pa=70000.0)
    assert ivt > 200.0


def test_radar_computations():
    """Test des calculs de météoro-radar polari-métrique."""
    kdp = calculate_specific_differential_phase_kdp(phidp_far_deg=45.0, phidp_near_deg=35.0, distance_km=5.0)
    assert kdp == 1.0


def test_query_engine_phase14_questions():
    """Test le ScientificQueryEngine sur l'ensemble des questions complexes de la mission ACF-024."""
    engine = ScientificQueryEngine()

    # 1. Explain why CAPE increases
    r1 = engine.ask("Explain why CAPE increases")
    assert "CAPE" in r1["parameter_key"]
    assert "Theta_e" in r1["causal_chain"]

    # 2. Which microphysics schemes predict graupel?
    r2 = engine.ask("Which microphysics schemes predict graupel?")
    assert "microphysics_schemes" in r2
    assert any("Thompson" in s for s in r2["microphysics_schemes"])

    # 3. Compare Thompson and Morrison
    r3 = engine.ask("Compare Thompson and Morrison")
    assert "comparison_table" in r3
    assert "Thompson" in r3["comparison_table"]

    # 4. Which satellite detects volcanic ash?
    r4 = engine.ask("Which satellite detects volcanic ash?")
    assert "satellite_sensors" in r4
    assert any("SEVIRI" in s for s in r4["satellite_sensors"])

    # 5. Explain Bergeron process
    r5 = engine.ask("Explain Bergeron process")
    assert "governing_inequality" in r5

    # 6. Explain Richardson number
    r6 = engine.ask("Explain Richardson number")
    assert "critical_value" in r6

    # 7. List every model using ICE4
    r7 = engine.ask("List every model using ICE4")
    assert "nwp_models" in r7
    assert any("AROME" in m for m in r7["nwp_models"])

    # 8. Explain every cloud producing hail
    r8 = engine.ask("Explain every cloud producing hail")
    assert "cloud_types" in r8
    assert any("Cumulonimbus" in c for c in r8["cloud_types"])


def test_global_registry_completeness():
    """Vérifie que l'encyclopédie répertorie plus de 110 entrées scientifiques enregistrées."""
    all_entries = EncyclopediaRegistry.get_all_entries()
    assert len(all_entries) >= 110

    keys = [e.key for e in all_entries]
    assert "thompson_microphysics_scheme" in keys
    assert "leighton_photoequilibrium_ozone" in keys
    assert "tornado_ehi_helicity_index" in keys
    assert "eumetsat_mtg_fci_li" in keys
    assert "radar_specific_differential_phase_kdp" in keys
    assert "discontinuous_galerkin_method_dg" in keys
    assert "earth_system_coupled_model" in keys
