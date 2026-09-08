"""
Atmospheric Complexity Framework (ACF)

AWCI Professional Weather Workstation Dashboard Layout Engine
"""

from typing import Any

from acf.science.encyclopedia.knowledge_graph.graph_engine import KnowledgeGraphEngine
from acf.science.parameters.engine import ParameterEngine
from acf.science.query_engine import ScientificQueryEngine
from acf.visualization.camera.camera_controller import CameraController
from acf.visualization.gpu.gpu_backend import GPUBackend
from acf.visualization.legends.color_tables import ColorTableRegistry
from acf.visualization.scene.scene_manager import VisualizationScene
from acf.visualization.timeline.timeline_controller import TimelineController


class AWCIDashboardEngine:
    """
    Moteur de Poste de Travail Opérationnel Météorologique AWCI (Professional Weather Workstation).
    """

    def __init__(self):
        self.scene = VisualizationScene("AWCI Main Scene", mode="2D")
        self.camera = CameraController()
        self.timeline = TimelineController()
        self.gpu = GPUBackend(use_gpu=True)
        self.param_engine = ParameterEngine()
        self.query_engine = ScientificQueryEngine()
        self.graph = KnowledgeGraphEngine()

        self.selected_parameter: str | None = "temperature"
        self.active_model: str = "IFS_00Z"
        self.mouse_position = {"lat": 48.8566, "lon": 2.3522, "value": 295.15}

    def render_left_panel(self) -> dict[str, Any]:
        """Panneau Gauche: Gestionnaire de couches, Modèles, Navigateur d'observations, Signets."""
        return {
            "layers": [layer_item["name"] for layer_item in self.scene.layers],
            "active_model": self.active_model,
            "available_models": ["IFS", "AROME", "ARPEGE", "ICON", "GFS", "WRF"],
            "bookmarks": list(self.camera.bookmarks.keys()),
        }

    def render_center_canvas(self) -> dict[str, Any]:
        """Canvas Central: Rendu Carte 2D/3D/4D.

        NOTE (correction): "fps" used to be a hardcoded 60 regardless of
        anything - this dashboard is a state/layout facade (see class
        docstring: it returns plain dicts describing panel state, there
        is no real render loop or frame timer anywhere in this stack -
        GPUBackend.render_offscreen() itself only echoes back
        width/height/lod, it doesn't measure a framerate either) so
        there was never a real frame rate behind this number. Reported
        as None (genuinely unmeasured) rather than a plausible-looking
        but entirely fabricated "60".
        """
        return {
            "scene_mode": self.scene.mode,
            "camera_position": self.camera.get_state()["position"],
            "active_layers": len(self.scene.layers),
            "fps": None,
        }

    def render_right_inspector(self) -> dict[str, Any]:
        """Panneau Droit: Inspecteur physique, Légendes, Explication du Reasoning Engine & Knowledge Graph."""
        if not self.selected_parameter:
            return {"selected_parameter": None}

        param_obj = self.param_engine.get(self.selected_parameter)
        explanation = self.param_engine.explain(self.selected_parameter) if param_obj else {}
        legend = ColorTableRegistry.generate_legend("temperature_wmo", "K")

        return {
            "parameter": self.selected_parameter,
            "name": param_obj.name if param_obj else self.selected_parameter,
            "unit": param_obj.unit if param_obj else "K",
            "equation": param_obj.governing_equation if param_obj else "",
            "latex_equation": param_obj.latex_equation if param_obj else "",
            "legend": legend,
            "physical_explanation": explanation.get("physical_meaning", ""),
            "dependencies": explanation.get("direct_dependencies", []),
            "governing_laws": explanation.get("governing_laws", []),
        }

    def render_bottom_timeline(self) -> dict[str, Any]:
        """Panneau Bas: Contrôle d'animation 4D, Sélecteur de niveau vertical & Barre d'état.

        NOTE (correction): same fabricated "fps": 60 as
        render_center_canvas() - see its NOTE. Also: self.timeline
        (TimelineController) is constructed here but nothing anywhere
        in this codebase ever drives it forward on a real timer once
        .play() is called (verified via grep: play()/next_frame() have
        no caller besides direct test invocation) - play() genuinely
        just flips a `playing` flag with no actual animation loop
        behind it yet. Flagged here rather than "fixed" since wiring a
        real Qt/GL timer loop is a larger feature this dashboard-state
        facade doesn't have the infrastructure for; TimelineController
        itself already reports frame/level state honestly.
        """
        return {
            "timeline_state": self.timeline.state(),
            "mouse_position": self.mouse_position,
            "current_model": self.active_model,
            "projection": "EPSG:4326 (WGS84 Equirectangular)",
            "fps": None,
        }

    def process_natural_language_query(self, user_query: str) -> dict[str, Any]:
        """Traite les requêtes vocales ou textuelles en langage naturel (ex: 'Show CAPE', 'Display radar')."""
        q_res = self.query_engine.ask(user_query)

        q_lower = user_query.lower()
        if "cape" in q_lower:
            self.selected_parameter = "CAPE"
            self.scene.add_layer("layer_cape", "CAPE Convective Energy", "raster", data="CAPE_GRID")
        elif "radar" in q_lower:
            self.selected_parameter = "radar_zdr"
            self.scene.add_layer("layer_radar", "NEXRAD Radar Reflectivity", "radar_volume", data="RADAR_GRID")
        elif "wind" in q_lower or "jet stream" in q_lower:
            self.selected_parameter = "wind_u"
            self.scene.add_layer("layer_wind", "Wind Particle Flow", "particle_flow", data="WIND_GRID")
        elif "cloud" in q_lower:
            self.selected_parameter = "cloud_water"
            self.scene.add_layer("layer_cloud", "Cloud Water Path", "raster", data="CLOUD_GRID")

        return {
            "query": user_query,
            "query_result": q_res,
            "dashboard_state": {
                "selected_parameter": self.selected_parameter,
                "layers_active": [layer_item["name"] for layer_item in self.scene.layers],
            },
        }

    def layout_summary(self) -> dict[str, Any]:
        """Génère le résumé global de la disposition du poste de travail AWCI."""
        return {
            "left_panel": self.render_left_panel(),
            "center_canvas": self.render_center_canvas(),
            "right_inspector": self.render_right_inspector(),
            "bottom_timeline": self.render_bottom_timeline(),
        }
