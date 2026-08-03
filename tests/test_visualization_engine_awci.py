"""
Atmospheric Complexity Framework (ACF)

Universal 2D/3D/4D Visualization Engine & AWCI Workstation Test Suite (MISSION ACF-027)
"""

from acf.visualization.scene.scene_manager import VisualizationScene
from acf.visualization.camera.camera_controller import CameraController
from acf.visualization.layers.scientific_layers import ParticleFlowLayer, IsosurfaceLayer, RadarVolumeLayer, SatelliteRGBLayer
from acf.visualization.timeline.timeline_controller import TimelineController
from acf.visualization.legends.color_tables import ColorTableRegistry
from acf.visualization.gpu.gpu_backend import GPUBackend
from acf.visualization.widgets.awci_dashboard import AWCIDashboardEngine


def test_visualization_scene():
    """Test du gestionnaire de scène 2D/3D/4D."""
    scene = VisualizationScene("Test Scene", mode="3D_Globe")
    assert scene.mode == "3D_Globe"

    layer = scene.add_layer("l1", "Temperature Grid", "raster")
    assert layer["id"] == "l1"
    assert len(scene.layers) == 1

    scene.set_layer_opacity("l1", 0.75)
    assert scene.get_layer("l1")["opacity"] == 0.75

    summary = scene.render_summary()
    assert summary["total_layers"] == 1
    assert summary["visible_layers"] == 1


def test_camera_controller():
    """Test du contrôleur de caméra 2D/3D."""
    camera = CameraController()
    camera.set_position(45.0, 5.0, 1000.0)
    assert camera.lat == 45.0
    assert camera.lon == 5.0

    camera.zoom(0.5)
    assert camera.altitude_km == 500.0

    camera.rotate_and_tilt(15.0, 30.0)
    assert camera.heading_deg == 15.0

    assert camera.goto_bookmark("Europe") is True
    assert camera.lat == 48.0


def test_scientific_layers():
    """Test des couches de rendu spécialisées (Vent, Isosurface, Radar, Satellite)."""
    flow = ParticleFlowLayer("l_flow", "Global Wind Streamlines", num_particles=10000)
    assert flow.render()["num_particles"] == 10000

    iso = IsosurfaceLayer("l_iso", "2 PVU Tropopause Surface", "potential_vorticity", iso_value=2.0)
    assert iso.render()["iso_value"] == 2.0

    radar = RadarVolumeLayer("l_rad", "NEXRAD Hail Core", "radar_data.h5", product="ZH")
    assert radar.render()["product"] == "ZH"

    sat = SatelliteRGBLayer("l_sat", "EUMETSAT Volcanic Ash RGB", recipe="Volcanic_Ash")
    assert sat.render()["recipe"] == "Volcanic_Ash"


def test_timeline_controller():
    """Test du contrôleur d'animation 4D."""
    timeline = TimelineController()
    assert timeline.current_index == 0

    timeline.play()
    assert timeline.playing is True

    next_t = timeline.next_frame()
    assert timeline.current_index == 1
    assert next_t == timeline.time_steps[1]

    timeline.set_vertical_level("500hPa")
    assert timeline.current_level == "500hPa"


def test_color_tables_registry():
    """Test des registres de palettes WMO et légendes."""
    pal = ColorTableRegistry.get_palette("radar_reflectivity")
    assert len(pal) >= 8

    leg = ColorTableRegistry.generate_legend("cape_severe", "J/kg")
    assert leg["unit"] == "J/kg"
    assert len(leg["stops"]) >= 5


def test_gpu_backend():
    """Test du backend d'accélération GPU et LOD."""
    gpu = GPUBackend(use_gpu=True)
    assert gpu.compile_shaders() is True

    lod = gpu.calculate_lod(altitude_km=50.0)
    assert lod == 0

    lod_high = gpu.calculate_lod(altitude_km=1500.0)
    assert lod_high == 2

    offscreen = gpu.render_offscreen(1920, 1080)
    assert offscreen["status"] == "success"


def test_awci_dashboard_engine():
    """Test du poste de travail AWCI et intégration langage naturel."""
    dashboard = AWCIDashboardEngine()
    summary = dashboard.layout_summary()

    assert "left_panel" in summary
    assert "center_canvas" in summary
    assert "right_inspector" in summary
    assert "bottom_timeline" in summary

    # Natural Language Query Interaction
    res = dashboard.process_natural_language_query("Show CAPE")
    assert res["dashboard_state"]["selected_parameter"] == "CAPE"
    assert len(dashboard.scene.layers) >= 1
