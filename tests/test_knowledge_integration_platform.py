"""
Atmospheric Complexity Framework (ACF)

Global Meteorological Knowledge Integration Platform Test Suite (MISSION ACF-XXX)
"""

from acf.knowledge_platform.dependency_graph import ParameterDependencyGraph
from acf.knowledge_platform.equation_library import GlobalEquationLibrary
from acf.knowledge_platform.metadata_catalogue import MetadataCatalogue
from acf.knowledge_platform.parameter_database import GlobalParameterDatabase
from acf.knowledge_platform.parameter_schema import MeteorologicalParameterSchema
from acf.knowledge_platform.roadmap import ImplementationRoadmap


def test_parameter_schema_attributes_count():
    """Vérifie que le schéma de paramètre contient l'intégralité des 28 attributs requis."""
    schema = MeteorologicalParameterSchema(
        official_scientific_name="Air Temperature",
        alternative_names=["Dry Temp"],
        wmo_code="012001",
        cf_convention_name="air_temperature",
        grib2_identifier="0,0,0",
        netcdf_variable="ta",
        bufr_descriptor="0 12 001",
        si_units="K",
        dimensions="[K]",
        valid_ranges="180 K to 330 K",
        physical_meaning="Kinetic energy of air molecules",
        mathematical_definition="p = rho * R_d * T",
        full_governing_equations="dT/dt = ...",
        conservation_equations="d(rho*cp*T)/dt = ...",
        diagnostic_equations="T = Tv / (1+0.61q)",
        empirical_formulations=["Magnus"],
        numerical_approximations=["Spectral"],
        model_implementation=["IFS"],
        dependencies=["pressure", "density"],
        derived_variables=["potential_temperature"],
        scientific_references=["WMO-No. 8"],
        operational_usage="Core state variable",
        quality_control_procedures=["Plausibility check"],
        visualization_recommendations="Isotherms",
        typical_thresholds={"Freezing": "273.15 K"},
        forecast_applications=["Frost forecasting"],
        climate_applications=["Global warming indicator"],
        machine_learning_applications=["GraphCast temperature field"],
        key="temperature",
        domain="Atmospheric State",
    )
    d = schema.to_dict()
    assert len(d) >= 28
    assert d["official_scientific_name"] == "Air Temperature"
    assert d["si_units"] == "K"


def test_global_parameter_database():
    """Test de la base de données scientifique globale des paramètres."""
    keys = GlobalParameterDatabase.list_all_keys()
    assert len(keys) >= 5
    assert "temperature" in keys
    assert "cape" in keys
    assert "sea_surface_temperature" in keys

    temp_param = GlobalParameterDatabase.get("temperature")
    assert temp_param is not None
    assert temp_param.cf_convention_name == "air_temperature"
    assert temp_param.grib2_identifier == "0,0,0"

    dynamics_params = GlobalParameterDatabase.get_by_domain("Dynamics")
    assert len(dynamics_params) >= 1
    assert dynamics_params[0].official_scientific_name == "Relative Vorticity"


def test_global_equation_library():
    """Test de la bibliothèque d'équations physiques (Fluid dynamics, Radiation, TKE, DA)."""
    ns_eq = GlobalEquationLibrary.get_equation("navier_stokes")
    assert ns_eq is not None
    assert ns_eq.category == "Fluid Dynamics"
    assert "Navier" in ns_eq.scientific_references[0]

    rad_eqs = GlobalEquationLibrary.list_equations_by_category("Radiation")
    assert len(rad_eqs) >= 2

    var_eq = GlobalEquationLibrary.get_equation("four_d_var_cost_function")
    assert var_eq is not None
    assert "Courtier" in var_eq.scientific_references[0]


def test_parameter_dependency_graph():
    """Test du graphe de dépendances DAG et des dérivations de variables."""
    deps = ParameterDependencyGraph.get_dependencies("potential_temperature")
    assert "temperature" in deps
    assert "pressure" in deps

    derived = ParameterDependencyGraph.get_derived_variables("temperature")
    assert "potential_temperature" in derived or "virtual_temperature" in derived

    tree = ParameterDependencyGraph.build_full_causal_tree("potential_temperature")
    assert tree["target"] == "potential_temperature"
    assert "temperature" in tree["direct_dependencies"]

    # CORRECTED (2026-09-05 audit de continuation): build_full_causal_tree()
    # used to always stop after exactly 2 levels regardless of the real
    # DAG depth, despite the name/docstring claiming a "full" tree.
    # potential_temperature -> temperature -> pressure/density is a real
    # 3-level chain in this database - verify it is no longer truncated.
    temperature_node = next(node for node in tree["dependency_tree"] if node["target"] == "temperature")
    assert {"pressure", "density"} <= set(temperature_node["direct_dependencies"])
    assert {n["target"] for n in temperature_node["dependency_tree"]} == {"pressure", "density"}


def test_metadata_catalogue_and_roadmap():
    """Test du catalogue d'indexation OMM/CF/GRIB2/NetCDF et de la roadmap d'ingénierie."""
    grib_res = MetadataCatalogue.lookup_by_grib2("0,0,0")
    assert grib_res is not None
    assert grib_res["official_scientific_name"] == "Air Temperature"

    cf_res = MetadataCatalogue.lookup_by_cf_standard_name("sea_surface_temperature")
    assert cf_res is not None
    assert cf_res["key"] == "sea_surface_temperature"

    cat_export = MetadataCatalogue.export_full_catalogue()
    assert cat_export["total_parameters_catalogued"] >= 5

    # CORRECTED (2026-09-05 audit de continuation): overall_status and
    # each stage's "status" used to unconditionally claim "EXHAUSTIVE
    # SCIENTIFIC COVERAGE ACHIEVED" / "COMPLETED" / "OPERATIONAL /
    # CERTIFIED PLATINUM" / "OPERATIONAL" - the same fabricated self-
    # certification pattern already found and fixed in
    # acf.master.scientific_certification.ScientificCertificationEngine,
    # independently duplicated here and left uncorrected until now.
    roadmap = ImplementationRoadmap.get_roadmap_summary()
    assert roadmap["overall_status"] == "NOT_AUDITED_PREVIOUSLY_SELF_ASSERTED_WITHOUT_VERIFICATION"
    assert len(roadmap["target_centers"]) >= 5
    stage3 = next(s for s in roadmap["stages"] if "AEOS" in s["stage"])
    assert stage3["status"] == "NOT_OPERATIONAL"
