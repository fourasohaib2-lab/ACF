"""
Atmospheric Complexity Framework (ACF)

4D Atmospheric Volume Explorer Engine Test Suite (MISSION ACF-UI-007)
"""

import pytest

from acf.ai.atmosphere_explorer.explorer_engine import AIAtmosphereExplorer
from acf.visualization.volume_engine.atmosphere_scene import AtmosphereScene
from acf.visualization.volume_engine.atmospheric_volume import AtmosphericVolume
from acf.visualization.volume_engine.cross_section import CrossSectionAnalyzer
from acf.visualization.volume_engine.interpolation_engine import VolumeInterpolationEngine
from acf.visualization.volume_engine.isosurface_engine import IsosurfaceEngine
from acf.visualization.volume_engine.particle_volume import ParticleVolumeRenderer
from acf.visualization.volume_engine.slice_controller import SliceController
from acf.visualization.volume_engine.turbulence_visualizer import TurbulenceVisualizer
from acf.visualization.volume_engine.vertical_grid import VerticalCoordinateSystem
from acf.visualization.volume_engine.volume_renderer import VolumeRenderer
from acf.visualization.volume_engine.volume_shader import VolumeRaymarchingShader


def test_atmospheric_volume_and_grid():
    """Test du volume 4D et du système de coordonnées verticales."""
    vol = AtmosphericVolume(variable_name="temperature_4d")
    meta = vol.get_volume_metadata()
    assert meta["variable_name"] == "temperature_4d"
    # CORRECTED: status used to unconditionally claim "VOLUME_4D_LOADED"
    # despite this class holding no actual data array field at all.
    assert meta["status"] == "METADATA_ONLY_NO_DATA_ARRAY_LOADED"

    # CORRECTED: units used to default to "K" regardless of
    # variable_name - wrong for any variable other than temperature.
    other_vol = AtmosphericVolume(variable_name="specific_humidity")
    assert other_vol.units == ""

    levels = VerticalCoordinateSystem.get_standard_pressure_levels()
    assert 500 in levels
    assert VerticalCoordinateSystem.get_layer_name_by_altitude(10.0) == "Troposphere"
    assert VerticalCoordinateSystem.get_layer_name_by_altitude(15.0) == "Stratosphere"


def test_volume_shader_and_renderer():
    """Test des shaders GLSL/Vulkan et du moteur de rendu volumétrique 60 FPS."""
    # CORRECTED: the shader spec (language/steps/opacity/lighting) is
    # a genuine declared design target, but compilation_status used to
    # claim "COMPILED_OPTIMAL" - no shader compiler is ever invoked.
    cfg = VolumeRaymarchingShader.get_shader_config()
    assert cfg["compilation_status"] == "NOT_COMPILED_NO_SHADER_COMPILER_INVOKED"
    assert cfg["raymarching_steps"] == 256

    # CORRECTED: target_fps/rendering_mode are genuine declared design
    # targets, but render_status used to claim "FRAME_RENDERED_SUCCESS"
    # - no GPU raymarching backend is connected.
    renderer = VolumeRenderer()
    res = renderer.render_frame("atm.temperature.4d")
    assert res["target_fps"] == 60.0
    assert res["render_status"] == "NOT_RENDERED_NO_GPU_BACKEND_CONNECTED"


def test_isosurface_and_cross_section():
    """Test de l'extraction d'isosurface (PV=2 PVU) et de coupe verticale (Point A -> B)."""
    # CORRECTED: variable/isovalue/units are genuinely echoed, but
    # status used to claim "ISOSURFACE_EXTRACTED" with a fixed fake
    # triangle count - no real volume field/Marching Cubes connected.
    iso = IsosurfaceEngine.extract_isosurface("PV", 2.0, "PVU")
    assert iso["status"] == "NOT_EXTRACTED_NO_VOLUME_FIELD_PROVIDED"
    assert iso["isovalue"] == 2.0

    # CORRECTED: point_a/point_b are genuinely echoed and distance_km
    # is now a real great-circle (Haversine) computation, but this
    # used to also claim fixed fake vertical structures (a "Polar Jet
    # Core"...) regardless of the actual points - no real atmospheric
    # field is connected.
    cs = CrossSectionAnalyzer.compute_cross_section((48.85, 2.35), (52.52, 13.40))
    assert cs["status"] == "NOT_COMPUTED_NO_ATMOSPHERIC_FIELD_PROVIDED"
    assert cs["vertical_structures_detected"] == []
    assert cs["distance_km"] == pytest.approx(877.7, abs=0.5)


def test_particles_interpolation_and_turbulence():
    """Test du rendu de particules 3D, d'interpolation et de turbulence CAT EDR."""
    slice_ctrl = SliceController()
    assert slice_ctrl.set_vertical_level(700)["current_level_hpa"] == 700

    # CORRECTED: particle_count is genuinely echoed (renamed to
    # particle_count_requested), but status used to claim
    # "PARTICLES_RENDERED" - no GPU compute backend is connected.
    parts = ParticleVolumeRenderer.render_particle_streamlines(10000)
    assert parts["particle_count_requested"] == 10000
    assert parts["status"] == "NOT_RENDERED_NO_GPU_COMPUTE_BACKEND_CONNECTED"

    # CORRECTED: used to ignore x/y/z entirely and unconditionally
    # claim a fixed "284.15 K" via a fake "3D Trilinear GPU" method -
    # no real volume field is connected.
    interp = VolumeInterpolationEngine.interpolate_point(10.0, 20.0, 500.0)
    assert interp["interpolated_value"] is None
    assert interp["method"] == "NOT_INTERPOLATED_NO_VOLUME_FIELD_PROVIDED"

    # CORRECTED: used to claim a fabricated "0.45 EDR" and
    # "MODERATE_TO_SEVERE_TURBULENCE" - no real wind-shear field
    # connected.
    turb = TurbulenceVisualizer.visualize_turbulence()
    assert turb["status"] == "NOT_VISUALIZED_NO_WIND_FIELD_CONNECTED"
    assert turb["max_edr_value"] is None

    # CORRECTED: used to claim a fixed "12 active nodes" and
    # "SCENE_ACTIVE" regardless of whether any real scene graph was
    # ever built (no node-add method exists on this class).
    scene = AtmosphereScene()
    scene_summary = scene.get_scene_summary()
    assert scene_summary["status"] == "NOT_ACTIVE_NO_SCENE_GRAPH_BUILT"
    assert scene_summary["active_nodes"] == 0


def test_ai_atmosphere_explorer():
    """Test de l'assistant IA pour l'explication causale de la dynamique atmosphérique."""
    # CORRECTED: used to ignore query_text's content and always claim
    # a fabricated "Explosive Cyclogenesis" event with a fake location
    # and "96.8%" confidence for ANY query - no real NLU/causal-
    # attribution pipeline connected.
    ai_res = AIAtmosphereExplorer.analyze_natural_query("Why is this storm intensifying?")
    assert ai_res["status"] == "NOT_ANALYZED_NO_NLU_PIPELINE_CONNECTED"
    assert ai_res["physical_causes"] == []
    assert ai_res["ai_confidence_score"] is None
