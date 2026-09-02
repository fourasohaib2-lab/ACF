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

# The four below were re-verified (not assumed) while auditing
# docs/architecture/duplicate_components.md's "Canvas carte" / "Plugins"
# / "Data manager" rows - each same-name pair below is a real, distinct,
# both-genuinely-used implementation, not a name collision resolved by
# import order. See each module's own NOTE for the full comparison.
from acf.ai.plugins.plugin_manager import PluginManager as AIPluginManager
from acf.core.plugin_manager import PluginManager as CorePluginManager
from acf.data.manager import DataManager as MapsDataManager
from acf.gui.map.map_canvas import MapCanvas as GuiMapCanvas
from acf.importers.manager import DataManager as ImportersDataManager
from acf.maps.canvas.map_canvas import MapCanvas as MapsCanvasMapCanvas


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


def test_plugin_manager_is_a_real_homonym_not_a_duplicate():
    """
    acf.core.plugin_manager.PluginManager (generic filesystem plugin
    discovery, used by acf.core.bootstrap) and
    acf.ai.plugins.plugin_manager.PluginManager (an in-memory AIPlugin
    registry with register()/analyze(), used by the AI subsystem) share
    a name and nothing else - same class of finding as
    Divergence/Dynamics above. Forcing them into one class would mix two
    genuinely unrelated responsibilities, so this locks in "different on
    purpose" rather than letting a future pass "fix" it into a merge.
    """
    assert CorePluginManager is not AIPluginManager
    core_pm = CorePluginManager(plugin_dir="/nonexistent")
    assert hasattr(core_pm, "discover") and not hasattr(core_pm, "analyze")
    ai_pm = AIPluginManager()
    assert hasattr(ai_pm, "analyze") and not hasattr(ai_pm, "discover")


def test_data_manager_is_a_real_homonym_not_a_duplicate():
    """
    acf.data.manager.DataManager (a real, stateful workflow orchestrator
    - open()/close()/current_dataset/history() - built on top of the
    canonical ReaderFactory/DatasetRegistry/CatalogManager, used by
    acf.dashboard.window) and acf.importers.manager.DataManager (the
    lower-level reader-registry ACF-016 already canonicalized io.manager
    onto - see test_importers_consolidation.py) are both real and both
    used, for different purposes.
    """
    assert MapsDataManager is not ImportersDataManager
    dm = MapsDataManager()
    assert hasattr(dm, "open") and hasattr(dm, "current_dataset")


def test_map_canvas_is_a_real_verified_duplicate_not_yet_consolidated():
    """
    Unlike every other pair in this file, this one IS a genuine
    duplicate needing a real consolidation decision (see both classes'
    own NOTEs) - not a false positive. Locked in here as "still open"
    so this doesn't silently get treated as resolved: acf.gui.map.
    map_canvas.MapCanvas wraps a QVBoxLayout'd FigureCanvasQTAgg as a
    child widget (a compose-by-delegation QWidget - it renders via its
    own internal MapProjection/MapRenderer/LayerManager trio) while
    acf.maps.canvas.map_canvas.MapCanvas IS a FigureCanvasQTAgg itself
    (renders via its own internal CartopyRenderer/RasterRenderer/
    ContourRenderer/WindRenderer trio) - both are technically QWidget
    subclasses (FigureCanvasQTAgg itself derives from QWidget), but they
    are not interchangeable: one is a matplotlib canvas you can call
    .draw()/.figure on directly, the other is a composite widget that
    merely contains one. Different real consumers today - picking a
    winner and migrating one side is a scoped design decision this
    repository has not made yet.
    """
    from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg

    assert GuiMapCanvas is not MapsCanvasMapCanvas
    assert not issubclass(GuiMapCanvas, FigureCanvasQTAgg)
    assert issubclass(MapsCanvasMapCanvas, FigureCanvasQTAgg)
