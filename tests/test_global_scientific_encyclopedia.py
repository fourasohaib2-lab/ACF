"""
Atmospheric Complexity Framework (ACF)

Global Scientific Encyclopedia Expansion Test Suite (MISSION ACF-022)
"""

import pytest

from acf.science.encyclopedia.aerodynamics.isa_atmosphere import (
    calculate_isa_pressure,
    calculate_isa_temperature,
    calculate_mach_number,
    calculate_speed_of_sound,
)
from acf.science.encyclopedia.boundary_layer import (
    calculate_bulk_richardson_number,
    calculate_log_wind_profile,
    calculate_obukhov_length,
)
from acf.science.encyclopedia.dynamics import (
    calculate_coriolis_parameter,
    calculate_ertel_potential_vorticity,
    calculate_geostrophic_wind_speed,
    calculate_rossby_number,
)
from acf.science.encyclopedia.knowledge_graph.graph_engine import KnowledgeGraphEngine
from acf.science.encyclopedia.knowledge_sources.sources_indexer import KnowledgeSourcesIndexer
from acf.science.encyclopedia.physical_laws.thermodynamics_laws import (
    calculate_clausius_clapeyron_es,
    calculate_equivalent_potential_temperature,
    calculate_ideal_gas_pressure,
    calculate_mixing_ratio,
    calculate_potential_temperature,
    calculate_relative_humidity,
    calculate_specific_humidity,
    calculate_virtual_temperature,
)
from acf.science.encyclopedia.precipitation import (
    calculate_hailstone_density,
    calculate_marshall_palmer_nd,
    calculate_raindrop_terminal_velocity,
)
from acf.science.encyclopedia.radar_extended import calculate_nyquist_velocity
from acf.science.encyclopedia.radiation import (
    calculate_beer_lambert_attenuation,
    calculate_planck_radiance,
    calculate_stefan_boltzmann_flux,
)
from acf.science.encyclopedia.registry import EncyclopediaRegistry
from acf.science.query_engine import ask


def test_registry_initialization_and_entry_count():
    """Vérifie que la totalité des entrées de l'encyclopédie sont chargées."""
    all_entries = EncyclopediaRegistry.get_all_entries()
    assert len(all_entries) >= 70, f"Expected at least 70 entries, got {len(all_entries)}"


def test_thermodynamic_calculations():
    """Test les calculs thermodynamiques fondamentaux."""
    # Ideal gas
    p = calculate_ideal_gas_pressure(1.2, 288.15)
    assert 98000.0 < p < 101000.0

    # Virtual temperature
    tv = calculate_virtual_temperature(290.0, 0.01)
    assert tv > 290.0

    # Potential temperature
    theta = calculate_potential_temperature(280.0, 850.0)
    assert theta > 280.0

    # Equivalent potential temperature
    theta_e = calculate_equivalent_potential_temperature(288.15, 1000.0, 0.01)
    assert theta_e > 288.15

    # Clausius-Clapeyron
    es = calculate_clausius_clapeyron_es(288.15)
    assert 1600.0 < es < 1800.0

    # Humidity metrics
    w = calculate_mixing_ratio(1000.0, 101325.0)
    assert w > 0.0
    q = calculate_specific_humidity(1000.0, 101325.0)
    assert q > 0.0
    rh = calculate_relative_humidity(1000.0, 1700.0)
    assert 50.0 < rh < 65.0


def test_dynamics_and_vorticity():
    """Test les calculs de dynamique et de vorticité d'Ertel."""
    f = calculate_coriolis_parameter(45.0)
    assert 1e-4 < f < 1.1e-4

    vg = calculate_geostrophic_wind_speed(0.001, 1.2, 45.0)
    assert vg > 0.0

    pv = calculate_ertel_potential_vorticity(1e-4, 0.005, 1.2)
    assert pv > 0.0

    ro = calculate_rossby_number(20.0, 1e6, 45.0)
    assert 0.0 < ro < 1.0


def test_boundary_layer_and_monin_obukhov():
    """Test les calculs de couche limite et de stabilité."""
    l_ob = calculate_obukhov_length(0.3, 0.05)
    assert l_ob < 0.0  # Convectif / instable

    rib = calculate_bulk_richardson_number(290.0, 288.0, 100.0, 10.0, 10.0, 0.0)
    assert rib > 0.0

    u_z = calculate_log_wind_profile(0.3, 10.0, 0.01)
    assert u_z > 0.0


def test_radiation_laws():
    """Test les lois de rayonnement et de Planck."""
    planck = calculate_planck_radiance(10e-6, 300.0)
    assert planck > 0.0

    flux = calculate_stefan_boltzmann_flux(288.15)
    assert 380.0 < flux < 400.0

    i_trans = calculate_beer_lambert_attenuation(100.0, 0.5)
    assert 0.0 < i_trans < 100.0


def test_radar_nyquist_velocity():
    """
    Test de la vitesse de Nyquist radar Doppler.

    CORRECTED: the "doppler_velocity_dealiasing" encyclopedia entry
    used to be registered with a compute_func (calculate_doppler_radial_velocity,
    a real but unrelated wind-projection formula) that didn't match its
    own documented equation ("V_max (Nyquist) = lambda * PRF / 4") -
    found via literature verification, not the earlier fake-data hunt.
    Now registered with calculate_nyquist_velocity, which genuinely
    implements that formula.
    """
    # 10 GHz radar (wavelength = c/f = 3e8/10e9 = 0.03 m), PRF 10 kHz
    # -> 75 m/s (270 km/h), a standard textbook example.
    v_nyquist = calculate_nyquist_velocity(wavelength_m=0.03, prf_hz=10000.0)
    assert v_nyquist == pytest.approx(75.0)

    entry = EncyclopediaRegistry.get("doppler_velocity_dealiasing")
    assert entry is not None
    assert entry.calculate(wavelength_m=0.03, prf_hz=10000.0) == pytest.approx(75.0)


def test_precipitation_microphysics():
    """Test les équations de précipitation et microphysique."""
    n_d = calculate_marshall_palmer_nd(8000.0, 2.0, 1.0)
    assert n_d > 0.0

    v_t = calculate_raindrop_terminal_velocity(0.002)
    assert 5.0 < v_t < 9.0

    rho_h = calculate_hailstone_density(wet_growth=True)
    assert rho_h == 900.0


def test_aerodynamics_and_isa():
    """Test les équations ISA et aérodynamiques."""
    t_isa = calculate_isa_temperature(5000.0)
    assert t_isa < 288.15

    p_isa = calculate_isa_pressure(5000.0)
    assert p_isa < 101325.0

    sound_speed = calculate_speed_of_sound(288.15)
    assert 330.0 < sound_speed < 350.0

    mach = calculate_mach_number(250.0, 288.15)
    assert 0.7 < mach < 0.8


def test_knowledge_graph_causal_chains():
    """Test le moteur de graphe de connaissances et les chaînes causales."""
    graph = KnowledgeGraphEngine()
    chain = graph.explain_chain("cumulonimbus", "grêle")
    assert chain["connected"] is True
    assert len(chain["path"]) >= 2
    assert "cumulonimbus" in chain["path"]


def test_knowledge_sources_indexer():
    """Test l'indexeur des sources de la littérature scientifique."""
    sources = KnowledgeSourcesIndexer.list_sources()
    assert len(sources) >= 15
    wmo_sources = KnowledgeSourcesIndexer.search_sources("WMO")
    assert len(wmo_sources) >= 3


def test_scientific_query_engine_ask():
    """Test le moteur de requêtes scientifique et la réponse complète."""
    res = ask("Pourquoi un cumulonimbus produit de la grêle ?")
    assert "question" in res
    assert "physical_explanation" in res
    assert "causal_chain" in res
    assert "equations" in res
    assert "parameters" in res
    assert "references" in res
    assert len(res["equations"]) >= 1
    assert len(res["references"]) >= 1
