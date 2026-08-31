"""
Tests for ACF-017 Class Collision Resolution & Compatibility Shims
"""

from acf.catalog.dataset_registry import DatasetRegistry as CanonicalDatasetRegistry
from acf.catalog.manager import CatalogManager as CanonicalCatalogManager
from acf.catalogs.catalog_manager import CatalogManager as CatalogsCatalogManager
from acf.core.parameter import Parameter as CoreParameter
from acf.core.parameter_registry import ParameterRegistry as CoreParameterRegistry
from acf.data.dataset_registry import DatasetRegistry as DataDatasetRegistry
from acf.data.dataset_validator import DatasetValidator as CanonicalDatasetValidator
from acf.data.engine.dataset_validator import DatasetValidator as EngineDatasetValidator
from acf.gui.main_window import MainWindow as LegacyMainWindow
from acf.gui.main_window.main_window import MainWindow as CanonicalMainWindow
from acf.maps.engine import MapEngine as LegacyMapEngine
from acf.maps.map_engine import MapEngine as CanonicalMapEngine
from acf.model4d.operators.divergence import Divergence as OperatorDivergence
from acf.model4d.physics.dynamics import Dynamics as PhysicsDynamics
from acf.parameters.parameter import Parameter as CanonicalParameter
from acf.parameters.registry import ParameterRegistry as CanonicalParameterRegistry
from acf.science.divergence import Divergence as ScienceDivergence
from acf.science.dynamics import Dynamics as ScienceDynamics


def test_parameter_collision_resolution():
    p1 = CanonicalParameter(code="t2m", name="2m Temperature", unit="K")
    p2 = CoreParameter(id="t2m", name="2m Temperature", units="K")
    assert p1.code == "t2m"
    assert p2.id == "t2m"
    assert p2.units == "K"


def test_parameter_registry_collision_resolution():
    reg1 = CanonicalParameterRegistry()
    reg2 = CoreParameterRegistry()
    assert reg1 is not None
    assert reg2 is not None


def test_catalog_manager_collision_resolution():
    cm1 = CanonicalCatalogManager()
    cm2 = CatalogsCatalogManager()
    assert hasattr(cm1, "scientific")
    assert hasattr(cm2, "scientific")


def test_dataset_registry_collision_resolution():
    reg1 = CanonicalDatasetRegistry()
    reg2 = DataDatasetRegistry()
    assert hasattr(reg1, "all")
    assert hasattr(reg2, "all")


def test_dataset_validator_dual_api_support():
    val1 = CanonicalDatasetValidator()
    val2 = EngineDatasetValidator()
    assert val1 is not None
    assert val2 is not None


def test_main_window_reexport():
    assert CanonicalMainWindow is LegacyMainWindow


def test_map_engine_reexport():
    engine = CanonicalMapEngine()
    legacy_engine = LegacyMapEngine()
    assert hasattr(engine, "add_layer")
    assert hasattr(legacy_engine, "add_layer")


def test_science_vs_operator_divergence():
    res_science = ScienceDivergence.calculate(du_dx=0.001, dv_dy=0.002)
    res_op = OperatorDivergence.calculate(du_dx=0.001, dv_dy=0.002, dw_dz=0.003)
    assert res_science == 0.003
    assert res_op == 0.006


def test_science_vs_physics_dynamics():
    avail = ScienceDynamics.available()
    assert "divergence" in avail
    acc = PhysicsDynamics.acceleration(force=100, mass=10)
    assert acc == 10.0
