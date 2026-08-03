"""
Atmospheric Complexity Framework (ACF)

4D Atmospheric Volume Explorer Engine Test Suite (MISSION ACF-UI-007)
"""

from acf.visualization.volume_engine.atmospheric_volume import AtmosphericVolume
from acf.visualization.volume_engine.vertical_grid import VerticalCoordinateSystem
from acf.visualization.volume_engine.volume_shader import VolumeRaymarchingShader
from acf.visualization.volume_engine.volume_renderer import VolumeRenderer
from acf.visualization.volume_engine.isosurface_engine import IsosurfaceEngine
from acf.visualization.volume_engine.cross_section import CrossSectionAnalyzer
from acf.visualization.volume_engine.slice_controller import SliceController
from acf.visualization.volume_engine.particle_volume import ParticleVolumeRenderer
from acf.visualization.volume_engine.interpolation_engine import VolumeInterpolationEngine
from acf.visualization.volume_engine.turbulence_visualizer import TurbulenceVisualizer
from acf.visualization.volume_engine.atmosphere_scene import AtmosphereScene
from acf.ai.atmosphere_explorer.explorer_engine import AIAtmosphereExplorer


def test_atmospheric_volume_and_grid():
    """Test du volume 4D et du système de coordonnées verticales."""
    vol = AtmosphericVolume(variable_name="temperature_4d")
    meta = vol.get_volume_metadata()
    assert meta["variable_name"] == "temperature_4d"
    assert meta["status"] == "VOLUME_4D_LOADED"

    levels = VerticalCoordinateSystem.get_standard_pressure_levels()
    assert 500 in levels
    assert VerticalCoordinateSystem.get_layer_name_by_altitude(10.0) == "Troposphere"
    assert VerticalCoordinateSystem.get_layer_name_by_altitude(15.0) == "Stratosphere"


def test_volume_shader_and_renderer():
    """Test des shaders GLSL/Vulkan et du moteur de rendu volumétrique 60 FPS."""
    cfg = VolumeRaymarchingShader.get_shader_config()
    assert cfg["compilation_status"] == "COMPILED_OPTIMAL"

    renderer = VolumeRenderer()
    res = renderer.render_frame("atm.temperature.4d")
    assert res["render_fps"] == 60.0
    assert res["render_status"] == "FRAME_RENDERED_SUCCESS"


def test_isosurface_and_cross_section():
    """Test de l'extraction d'isosurface (PV=2 PVU) et de coupe verticale (Point A -> B)."""
    iso = IsosurfaceEngine.extract_isosurface("PV", 2.0, "PVU")
    assert iso["status"] == "ISOSURFACE_EXTRACTED"
    assert iso["isovalue"] == 2.0

    cs = CrossSectionAnalyzer.compute_cross_section((48.85, 2.35), (52.52, 13.40))
    assert cs["status"] == "CROSS_SECTION_COMPUTED"
    assert len(cs["vertical_structures_detected"]) >= 3


def test_particles_interpolation_and_turbulence():
    """Test du rendu de particules 3D, d'interpolation et de turbulence CAT EDR."""
    slice_ctrl = SliceController()
    assert slice_ctrl.set_vertical_level(700)["current_level_hpa"] == 700

    parts = ParticleVolumeRenderer.render_particle_streamlines(10000)
    assert parts["status"] == "PARTICLES_RENDERED"

    interp = VolumeInterpolationEngine.interpolate_point(10.0, 20.0, 500.0)
    assert interp["interpolated_value"] == 284.15

    turb = TurbulenceVisualizer.visualize_turbulence()
    assert turb["status"] == "VISUALIZED"

    scene = AtmosphereScene()
    assert scene.get_scene_summary()["status"] == "SCENE_ACTIVE"


def test_ai_atmosphere_explorer():
    """Test de l'assistant IA pour l'explication causale de la dynamique atmosphérique."""
    ai_res = AIAtmosphereExplorer.analyze_natural_query("Why is this storm intensifying?")
    assert ai_res["status"] == "ANALYSIS_COMPLETE"
    assert len(ai_res["physical_causes"]) >= 4
    assert ai_res["ai_confidence_score"] > 90.0
