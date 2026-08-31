"""
Atmospheric Complexity Framework (ACF)

Master World Scientific Expansion Test Suite
"""

from acf.science.encyclopedia.aviation_extended import calculate_density_altitude, calculate_hydroplaning_speed_knots
from acf.science.encyclopedia.cloud_physics.wmo_cloud_taxonomy import calculate_hallett_mossop_splintering
from acf.science.encyclopedia.hydrology.surface_hydrology import (
    calculate_horton_infiltration,
    calculate_rational_peak_runoff,
)
from acf.science.encyclopedia.mathematics_advanced import calculate_cfl_number
from acf.science.encyclopedia.registry import EncyclopediaRegistry
from acf.science.encyclopedia.remote_sensing_extended import calculate_gps_ro_refractivity, calculate_radar_zdr


def test_hydrology_computations():
    """Test des fonctions de calcul hydrologique."""
    f = calculate_horton_infiltration(f0=50.0, fc=10.0, k=0.5, time_hours=2.0)
    assert 10.0 < f < 50.0

    q_peak = calculate_rational_peak_runoff(c=0.8, i_mm_h=45.0, area_km2=10.0)
    assert q_peak > 0.0


def test_cloud_taxonomy_hallett_mossop():
    """Test du mécanisme microphysique de Hallett-Mossop."""
    splinters = calculate_hallett_mossop_splintering(temp_c=-5.0, rime_rate_mg_s=0.1)
    assert splinters > 0.0

    # Inexistant en dehors de [-8, -3]
    assert calculate_hallett_mossop_splintering(temp_c=-15.0, rime_rate_mg_s=0.1) == 0.0


def test_remote_sensing_computations():
    """Test des calculs de télédétection satellitaire et radar."""
    n_refr = calculate_gps_ro_refractivity(p_hpa=1013.25, temp_k=288.15, e_hpa=12.0)
    assert n_refr > 250.0

    zdr = calculate_radar_zdr(z_h_dbz=45.0, z_v_dbz=43.0)
    assert zdr == 2.0


def test_aviation_computations():
    """Test des calculs aéronautiques."""
    da = calculate_density_altitude(pressure_alt_ft=2000.0, oat_celsius=35.0, isa_temp_celsius=11.0)
    assert da > 2000.0

    vp = calculate_hydroplaning_speed_knots(tire_pressure_psi=100.0)
    assert vp == 90.0


def test_mathematics_cfl():
    """Test du critère de stabilité CFL."""
    cfl = calculate_cfl_number(u_velocity=30.0, dt_seconds=10.0, dx_meters=1000.0)
    assert cfl == 0.3


def test_world_expansion_registry_integration():
    """Vérifie l'intégration complète de toutes les nouvelles entrées dans le registre universel."""
    all_entries = EncyclopediaRegistry.get_all_entries()
    assert len(all_entries) >= 100

    keys = [e.key for e in all_entries]
    assert "green_ampt_infiltration_model" in keys
    assert "wmo_cloud_species_classification" in keys
    assert "gps_radio_occultation_refractivity" in keys
    assert "hybrid_envar_data_assimilation" in keys
    assert "nwp_meteo_france_arpege" in keys
    assert "density_altitude_aviation" in keys
    assert "cfl_stability_condition" in keys
    assert "pinn_physics_informed_neural_network" in keys
    assert "graphcast_gnn_weather" in keys
