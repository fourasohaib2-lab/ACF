"""
Atmospheric Complexity Framework (ACF)

Global Planetary Resilience, Cosmic Hazard & Interplanetary Observation Platform Test Suite (MISSION ACF-039)
"""

from acf.planetary.astrobiology import HabitabilityAssessment, HabitabilityEngine
from acf.planetary.awci_planetary_dashboard import PlanetaryDefenseDashboard
from acf.planetary.cosmic_hazards import CosmicHazardEngine
from acf.planetary.exoplanets import ExoplanetDatabase
from acf.planetary.impact_engine import ImpactEngine, ImpactSeverity
from acf.planetary.impact_tsunami import ImpactTsunamiEngine
from acf.planetary.orbital_mechanics import OrbitalMechanicsEngine
from acf.planetary.planetary_ai import PlanetaryReasoningEngine
from acf.planetary.planetary_atmospheres import PlanetaryAtmosphereEngine
from acf.planetary.planetary_climate import PlanetaryClimateEngine
from acf.planetary.planetary_database import PlanetaryDatabase, PlanetaryDefenseRegistry, PotentialHazard
from acf.planetary.space_observatories import ObservatoryRegistry
from acf.science.query_engine import ScientificQueryEngine


def test_planetary_database_and_neo_registry():
    """Test du registre d'objets géocroiseurs (Apophis, Bennu, Chicxulub)."""
    neo = PlanetaryDefenseRegistry.get_neo("bennu")
    assert neo is not None
    assert neo.name == "101955 Bennu"
    assert neo.diameter_m == 492.0
    assert neo.is_potentially_hazardous is True

    hazard = PlanetaryDatabase.get_sample_hazard("bennu")
    assert isinstance(hazard, PotentialHazard)
    assert hazard.torino_scale_level == 1

    # CORRECTED: any key other than "bennu" used to silently return
    # Bennu's hazard numbers mislabeled as the requested object's -
    # e.g. Apophis (whose own registry entry documents
    # impact_probability=0.0, "Éliminé pour 2029/2036/2068") would get
    # Bennu's Torino level 1 / 2182 close-approach data. See
    # planetary_database.py.
    assert PlanetaryDatabase.get_sample_hazard("apophis") is None


def test_orbital_mechanics_engine():
    """Test du moteur de mécanique céleste et orbitale (Vis-Viva, Kepler, Lagrange L1)."""
    v_orb = OrbitalMechanicsEngine.vis_viva_velocity(r_m=1.496e11, a_m=1.496e11)
    assert 29000.0 < v_orb < 31000.0  # Vitesse de la Terre ~ 29.78 km/s

    period_sec = OrbitalMechanicsEngine.orbital_period(a_m=1.496e11)
    period_days = period_sec / 86400.0
    assert 360.0 < period_days < 370.0  # 365.25 jours

    E_rad = OrbitalMechanicsEngine.solve_kepler_equation(M_rad=0.5, e=0.2)
    assert E_rad > 0.5

    l1_dist = OrbitalMechanicsEngine.lagrange_l1_distance(1.496e11)
    assert 1.4e9 < l1_dist < 1.6e9  # ~1.5 million km


def test_impact_engine_and_tsunami_hydrodynamics():
    """Test de la simulation d'impact cosmique (Chicxulub) et tsunami d'impact."""
    impact = ImpactEngine.simulate_impact(diameter_m=10000.0, velocity_km_s=20.0, mass_kg=1.0e15)
    assert isinstance(impact, ImpactSeverity)
    assert impact.is_global_extinction_event is True
    assert impact.megatons_tnt > 1.0e7

    tsunami = ImpactTsunamiEngine.simulate_ocean_impact_tsunami(
        impactor_diameter_m=1000.0, distance_from_impact_km=500.0
    )
    assert tsunami["initial_deep_water_wave_height_m"] > 10.0
    assert tsunami["coastal_runup_height_m"] > tsunami["deep_water_height_at_target_m"]


def test_planetary_atmospheres_and_climate():
    """Test des atmosphères planétaires et du climat comparé (Earth, Mars, Venus, Titan)."""
    venus = PlanetaryAtmosphereEngine.get_atmosphere("venus")
    assert venus is not None
    assert venus.surface_pressure_pa > 9.0e6
    assert venus.mean_temperature_k > 700.0

    scale_h = PlanetaryAtmosphereEngine.calculate_scale_height_km(288.15, 0.02897, 9.80665)
    assert 8.0 < scale_h < 9.0  # ~8.5 km sur Terre

    climate = PlanetaryClimateEngine.compare_climates()
    assert "Venus" in climate
    assert climate["Venus"]["greenhouse_warming_k"] == 500.0


def test_exoplanets_and_astrobiology():
    """Test du catalogue d'exoplanètes (TRAPPIST-1 e) et du moteur d'habitabilité."""
    exo = ExoplanetDatabase.get_exoplanet("trappist1_e")
    assert exo is not None
    assert exo.is_in_habitable_zone is True
    assert exo.esi_score > 0.8

    # CORRECTED: get_exoplanet() used to only match the internal dict
    # key exactly - none of the catalog's own entries were findable by
    # their own display name. See exoplanets.py.
    exo_by_display_name = ExoplanetDatabase.get_exoplanet("TRAPPIST-1 e")
    assert exo_by_display_name is exo

    # CORRECTED: evaluate_habitability() used to unconditionally claim
    # a DETECTION of O2/O3/CH4/H2O biosignatures with is_habitable=True
    # regardless of target_name - no real spectroscopic pipeline is
    # connected. Now genuinely derived from ExoplanetDatabase's real
    # per-object ESI score and habitable-zone flag, with an honestly
    # empty biosignature list. See astrobiology.py.
    assessment = HabitabilityEngine.evaluate_habitability("TRAPPIST-1 e")
    assert isinstance(assessment, HabitabilityAssessment)
    assert assessment.is_habitable is True
    assert assessment.habitability_index_pct == round(exo.esi_score * 100.0, 1)
    assert assessment.detected_biosignatures == []

    assert HabitabilityEngine.evaluate_habitability("Not A Real Planet XYZ") is None


def test_space_observatories_and_cosmic_hazards():
    """Test du registre des observatoires spatiaux et du moteur de risques cosmiques."""
    jwst = ObservatoryRegistry.get_observatory("jwst")
    assert jwst is not None
    assert jwst.orbit_type == "Sun-Earth L2 Halo Orbit"

    threats = CosmicHazardEngine.evaluate_threats()
    assert len(threats) >= 3
    assert threats[0].hazard_type.startswith("Near-Earth Asteroid")


def test_planetary_ai_and_dashboard():
    """Test du moteur de raisonnement IA planétaire et du tableau de bord AWCI."""
    # CORRECTED: every field used to be a fixed narrative (including a
    # specific fabricated "Planetary Defense Briefing PDCO-2026-039
    # Validated") identical no matter what object_name was requested.
    # Now genuinely looks up the object in PlanetaryDefenseRegistry and
    # is honest about what an unknown object or an uncomputed
    # long-horizon claim looks like. See planetary_ai.py.
    reasoning = PlanetaryReasoningEngine.run_planetary_reasoning_chain("Bennu")
    assert reasoning["target_object"] == "101955 Bennu"
    assert reasoning["4_hazard_assessment"]["torino_scale_level"] == 1
    assert reasoning["7_scientific_report"] is None  # not fabricated

    unknown = PlanetaryReasoningEngine.run_planetary_reasoning_chain("2024 XY1 (not in registry)")
    assert unknown["status"] == "UNKNOWN_OBJECT_NOT_IN_REGISTRY"
    assert unknown["is_real_data"] is False

    meta = PlanetaryDefenseDashboard.get_dashboard_metadata()
    assert meta["workspace_name"] == "PLANETARY DEFENSE & INTERPLANETARY CENTER"


def test_query_engine_planetary_queries():
    """Test des requêtes du ScientificQueryEngine pour la défense et les sciences planétaires."""
    q_engine = ScientificQueryEngine()

    r1 = q_engine.ask("Show Asteroids")
    assert r1["workspace_name"] == "PLANETARY DEFENSE & INTERPLANETARY CENTER"

    r2 = q_engine.ask("Show Impact")
    assert r2["widget_type"] == "CosmicImpactSimulator"

    r3 = q_engine.ask("Show Mars")
    assert r3["widget_type"] == "PlanetaryAtmosphereViewer"

    r4 = q_engine.ask("Show Exoplanets")
    assert r4["widget_type"] == "AstrobiologyHabitabilityViewer"

    r5 = q_engine.ask("Explain Kepler")
    assert r5["references"] == ["Kepler (1609, 1619)", "Newton (1687) Principia"]
