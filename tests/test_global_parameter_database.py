"""
Atmospheric Complexity Framework (ACF)

Global Parameter Database & Scientific Reasoning Test Suite (MISSION ACF-023)
"""

from acf.science.parameters.physical_parameter import PhysicalParameter
from acf.science.parameters.engine import ParameterEngine
from acf.science.query_engine import ScientificQueryEngine, ask
from acf.science.encyclopedia.knowledge_graph.graph_engine import KnowledgeGraphEngine


def test_physical_parameter_metadata():
    """Vérifie la présence et la structure des métadonnées du paramètre physique."""
    param = PhysicalParameter(
        key="test_param",
        name="Test Parameter",
        symbol="Tp",
        domain="Test Domain",
        unit="m",
        description="Description test",
        physical_meaning="Sens physique test",
        cf_standard_name="test_standard_name",
        grib2_code="0,0,0",
        bufr_code="0 00 000",
        netcdf_name="tp",
        references=["WMO Test Reference"],
    )
    s = param.summary()
    assert s["key"] == "test_param"
    assert s["cf_standard_name"] == "test_standard_name"
    assert s["grib2_code"] == "0,0,0"
    assert s["netcdf_name"] == "tp"


def test_parameter_engine_queries():
    """Test les capacités du ParameterEngine."""
    engine = ParameterEngine()
    p_cape = engine.get("CAPE")
    assert p_cape is not None
    assert p_cape.symbol == "CAPE"
    assert p_cape.cf_standard_name == "atmosphere_convective_available_potential_energy"

    # Test dépendances
    deps = engine.dependencies("virtual_temperature")
    dep_keys = [p.key for p in deps]
    assert "temperature" in dep_keys or "humidity" in dep_keys

    # Test dépendants
    dependents = engine.dependents("humidity")
    dep_keys_down = [p.key for p in dependents]
    assert len(dep_keys_down) >= 1

    # Test explanation
    exp = engine.explain("temperature")
    assert exp["key"] == "temperature"
    assert "parameter" in exp


def test_query_engine_natural_language_questions():
    """Test le ScientificQueryEngine sur la liste des questions naturelles de la mission ACF-023."""
    q_engine = ScientificQueryEngine()

    # 1. "What is CAPE?"
    res_cape = q_engine.ask("What is CAPE?")
    assert "physical_explanation" in res_cape
    assert res_cape["parameter_key"] == "CAPE"
    assert len(res_cape["equations"]) >= 1

    # 2. "How is potential temperature calculated?"
    res_theta = q_engine.ask("How is potential temperature calculated?")
    assert "potential_temperature" in res_theta.get("parameter_key", "potential_temperature")
    assert r"\theta" in res_theta.get("equation", "")

    # 3. "Which NWP models use ICE4?"
    res_ice4 = q_engine.ask("Which NWP models use ICE4?")
    assert "nwp_models" in res_ice4
    assert any("AROME" in m for m in res_ice4["nwp_models"])

    # 4. "Which parameters depend on humidity?"
    res_hum = q_engine.ask("Which parameters depend on humidity?")
    assert "dependent_parameters" in res_hum
    assert len(res_hum["dependent_parameters"]) >= 1

    # 5. "Which satellite products observe cloud top temperature?"
    res_sat = q_engine.ask("Which satellite products observe cloud top temperature?")
    assert "satellite_instruments_and_products" in res_sat
    assert any("SEVIRI" in p or "GOES" in p for p in res_sat["satellite_instruments_and_products"])


def test_convective_flash_flood_causal_chain():
    """Test la chaîne causale complète du chauffage au sol jusqu'à la crue éclair."""
    graph = KnowledgeGraphEngine()
    chain = graph.explain_chain("surface heating", "flash flood")
    assert chain["connected"] is True
    assert chain["path"][0] == "surface heating"
    assert chain["path"][-1] == "flash flood"
    assert "cumulonimbus" in chain["path"] or "heavy rain" in chain["path"]
