"""Module registry dynamically discovering, building tree hierarchy, and indexing universal global search for all ACF scientific subsystems (ACF-UI-013).

NOTE (correction, 2026-09-04 — the same "presented as connected when
it isn't" pattern already found and fixed across ESOC's own panels):
of this registry's 25 `_safe_import_register()` calls, 19 named a
`class_name` that genuinely does not exist at the given `module_path`
(verified by direct import + `getattr` for every single one - not a
sample). `_safe_import_register()`'s own old fallback for exactly this
case silently substituted the bare, empty PACKAGE `__init__` module
object for `self.modules[key]` instead of `None` - `is_connected()`
and `get_system_status_summary()` (both `is not None` checks) then
honestly reported these 19 modules as "connected", when in truth
nothing real had ever been instantiated for them. No real GUI code
currently reads `is_connected()`/`get_system_status_summary()`/
`global_search()`/`search_index` (verified by a repo-wide grep - this
registry's own search/status API has no wired caller yet), so this had
no visible symptom - but it was still a real, live lie waiting for the
day someone did wire a status panel to it.

Fixed two ways:
1. `_safe_import_register()` no longer falls back to the bare module -
   a missing class now honestly sets `self.modules[key] = None` (with
   a real WARNING, not a swallowed DEBUG line), the same "not connected"
   outcome an actual import failure already produced.
2. For the 15 of 19 where a real, correctly-named class demonstrably
   exists elsewhere in this codebase (verified: imports cleanly,
   instantiates with zero arguments, and is a genuine thematic match -
   e.g. `catalog`'s wanted `CatalogManager` turned out to be real, just
   at `acf.catalog.manager` instead of bare `acf.catalog`), the
   `(module_path, class_name)` below was corrected to point at it.
   The remaining 4 (`earth_physics`, `space_weather`, and the bare
   `acf.geology`/`acf.geoengineering` entries in target_domains) have
   no single real class anywhere that unambiguously represents "the"
   engine for that whole domain (each is a real, populated package of
   many independent formula/engine classes, not one orchestrator) -
   left honestly unregistered (`None`) rather than guessing.
"""

import importlib
import logging
from pathlib import Path
from typing import Any

from acf.ai.simulation.neural_operator import NeuralOperatorEngine
from acf.hpc.simulation.checkpoint import CheckpointManager
from acf.hpc.simulation.cuda_kernels import CUDAKernelManager
from acf.hpc.simulation.gpu_solver import GPUSolver
from acf.hpc.simulation.mpi_domain import MPIDomainDecomposition
from acf.simulation_engine.atmosphere_solver.atmospheric_model import AtmosphericModel
from acf.simulation_engine.atmosphere_solver.convection_engine import ConvectionEngine
from acf.simulation_engine.atmosphere_solver.microphysics_engine import MicrophysicsEngine
from acf.simulation_engine.climate_scenarios.cmip6 import CMIP6Engine, SSPScenario
from acf.simulation_engine.climate_scenarios.ssp_engine import SSPEngine
from acf.simulation_engine.coupled_solver.coupled_earth_solver import CoupledEarthSolver
from acf.simulation_engine.ensemble_prediction.ensemble_engine import EarthEnsembleEngine
from acf.simulation_engine.ensemble_prediction.probability_engine import ProbabilityEngine
from acf.simulation_engine.extreme_events.cyclone import CycloneSimulator
from acf.simulation_engine.extreme_events.flood import FloodSimulator
from acf.simulation_engine.extreme_events.storm import SevereStormSimulator
from acf.simulation_engine.extreme_events.wildfire import WildfireSimulator
from acf.simulation_engine.land_solver.carbon_flux import CarbonFluxModel
from acf.simulation_engine.land_solver.soil_model import SoilModel
from acf.simulation_engine.land_solver.vegetation_model import VegetationModel
from acf.simulation_engine.numerical_core.earth_grid import EarthGrid
from acf.simulation_engine.ocean_solver.ocean_model import OceanModel
from acf.simulation_engine.ocean_solver.wave_model import WaveModel

logger = logging.getLogger(__name__)


class ModuleRegistry:
    """Central registry dynamically discovering, building system trees, and supporting universal search across all ACF modules."""

    def __init__(self) -> None:
        self.modules: dict[str, Any] = {}
        self.search_index: list[dict[str, str]] = []
        self._initialize_all_subsystems()
        self._auto_discover_packages()
        self._build_search_index()

    def _safe_import_register(self, key: str, module_path: str, class_name: str) -> None:
        """Safely import and instantiate a subsystem class - real success
        or real, honestly-reported failure, never a look-alike stand-in.

        NOTE (correction, 2026-09-04): this used to fall back to
        `self.modules[key] = mod` (the bare, empty PACKAGE module
        object) whenever `class_name` didn't exist on it - `is_connected()`
        then reported that module as genuinely connected (its own
        `is not None` check), which was never true: nothing real had
        been instantiated. See this file's own module docstring for the
        full disclosure. A missing class is now the exact same real
        "not connected" outcome as an import failure - self.modules[key]
        = None, with a real WARNING (was silently swallowed at DEBUG)."""
        try:
            mod = importlib.import_module(module_path)
        except Exception as e:
            logger.warning(f"Module {key} ({module_path}.{class_name}) unavailable - import failed: {e}")
            self.modules[key] = None
            return

        cls = getattr(mod, class_name, None)
        if cls is None:
            logger.warning(f"Module {key}: {module_path}.{class_name} does not exist - registering as not connected")
            self.modules[key] = None
            return

        try:
            self.modules[key] = cls()
        except Exception as e:
            logger.warning(f"Module {key} ({module_path}.{class_name}) unavailable - construction failed: {e}")
            self.modules[key] = None

    def _auto_discover_packages(self) -> None:
        """Dynamically scan acf subpackages and register any unregistered operational modules."""
        target_domains = [
            # NOTE (correction, 2026-09-04): the 4 corrected below each
            # named a class that did not exist at the given path (see
            # this file's own module docstring) - fixed to the real
            # class that does. geoengineering_lab/ai_emergency/
            # ai_digital_twin were already genuinely correct.
            (
                "planetary_limits",
                "acf.digital_twin.planetary_limits.planetary_boundaries",
                "PlanetaryBoundariesSimulator",
            ),
            ("geoengineering_lab", "acf.digital_twin.geoengineering_lab", "GeoengineeringLab"),
            ("ai_emergency", "acf.ai.emergency_assistant", "AIEmergencyAssistant"),
            ("ai_digital_twin", "acf.ai.digital_twin", "AIDigitalTwinAssistant"),
            ("aerosols_dust", "acf.science.clouds.aerosols", "CloudAerosolEngine"),
            ("volcanoes", "acf.geology.volcanic_physics", "VolcanicPhysicsEngine"),
            ("reports_generator", "acf.reports.briefings.briefing_generator", "BriefingGenerator"),
        ]
        for key, path, cls_name in target_domains:
            if key not in self.modules or self.modules[key] is None:
                self._safe_import_register(key, path, cls_name)

    def _initialize_all_subsystems(self) -> None:
        """Instantiate foundational scientific engineering domains."""
        grid = EarthGrid(n_lat=36, n_lon=72, n_levels=16)
        self.modules["earth_grid"] = grid
        self.modules["coupled_earth_solver"] = CoupledEarthSolver(grid)

        self.modules["atmospheric_model"] = AtmosphericModel(grid)
        self.modules["convection_engine"] = ConvectionEngine()
        self.modules["microphysics_engine"] = MicrophysicsEngine()

        self.modules["ocean_model"] = OceanModel(grid)
        self.modules["wave_model"] = WaveModel()

        self.modules["soil_model"] = SoilModel()
        self.modules["vegetation_model"] = VegetationModel()
        self.modules["carbon_flux_model"] = CarbonFluxModel()

        self.modules["ensemble_engine"] = EarthEnsembleEngine(self.modules["coupled_earth_solver"])
        self.modules["probability_engine"] = ProbabilityEngine()
        self.modules["cyclone_simulator"] = CycloneSimulator()
        self.modules["storm_simulator"] = SevereStormSimulator()
        self.modules["flood_simulator"] = FloodSimulator()
        self.modules["wildfire_simulator"] = WildfireSimulator()

        self.modules["cmip6_engine"] = CMIP6Engine(SSPScenario.SSP2_45)
        self.modules["ssp_engine"] = SSPEngine(SSPScenario.SSP2_45)

        # NOTE: loads the real trained FNO surrogate for near-surface
        # temperature if the reference checkpoint (trained this session
        # by scripts/train_fno_surrogate.py) is present - see
        # ESOCController.handle_run_ai_forecast()'s own NOTE for how this
        # is actually used. Honest fallback: if the file is missing,
        # NeuralOperatorEngine still constructs fine and
        # predict_surface_temperature() reports
        # NOT_PREDICTED_NO_TRAINED_SURROGATE_LOADED rather than crashing.
        _fno_checkpoint = Path(__file__).resolve().parents[4] / "models" / "fno_surface_temperature_reference.pt"
        self.modules["neural_operator"] = NeuralOperatorEngine(
            fno_checkpoint_path=str(_fno_checkpoint) if _fno_checkpoint.exists() else None
        )

        self.modules["gpu_solver"] = GPUSolver(use_gpu=False)
        self.modules["mpi_domain"] = MPIDomainDecomposition(global_nlat=36, global_nlon=72)
        self.modules["cuda_kernels"] = CUDAKernelManager()
        self.modules["checkpoint_manager"] = CheckpointManager()

        # NOTE (correction, 2026-09-04): see this file's own module
        # docstring. earth_physics/space_weather/geoengineering/geology
        # (this exact bare-package registration - "volcanoes" above is
        # a real, separate, now-fixed entry) are left as-is: each
        # named class never existed, and unlike the others below, no
        # single real class anywhere in this codebase unambiguously
        # represents "the" engine for that whole domain - each is a
        # real, populated package of many independent engines, not one
        # orchestrator. Now honestly resolves to None (not connected)
        # via _safe_import_register()'s own fixed fallback, instead of
        # the bare, inert package module silently reporting as
        # "connected" before this fix.
        self._safe_import_register("earth_physics", "acf.earth_physics", "AtmosphericDynamicsEngine")
        self._safe_import_register("data_assimilation", "acf.data_assimilation.analysis_state", "EarthAnalysisStateVector")
        self._safe_import_register("digital_twin", "acf.digital_twin.digital_twin_engine", "DigitalTwinEngine")
        self._safe_import_register("planetary_dashboard", "acf.digital_twin.planetary_dashboard", "PlanetaryDashboard")
        self._safe_import_register("ai_expert", "acf.ai_expert.earth_system_expert", "EarthSystemExpert")
        self._safe_import_register("geoengineering", "acf.geoengineering", "GeoengineeringPlatform")
        self._safe_import_register("space_weather", "acf.space_weather", "SpaceWeatherPlatform")
        self._safe_import_register("geology", "acf.geology", "GeologyPlatform")
        self._safe_import_register("monitoring", "acf.monitoring.monitoring_registry", "MonitoringRegistry")
        self._safe_import_register("verification", "acf.verification", "ForecastVerificationEngine")
        self._safe_import_register("catalog", "acf.catalog.manager", "CatalogManager")
        self._safe_import_register("plugins", "acf.core.plugin_manager", "PluginManager")
        self._safe_import_register("forecast", "acf.forecast.forecast_engine", "ForecastEngine")
        self._safe_import_register("hydrology", "acf.ai_expert.hydrology_reasoning", "HydrologyReasoningEngine")
        self._safe_import_register("air_quality", "acf.ai_expert.air_quality_reasoning", "AirQualityReasoningEngine")
        self._safe_import_register("production_dashboard", "acf.dashboard.manager", "DashboardManager")
        self._safe_import_register(
            "visualization", "acf.visualization.ai_forecast_center.forecast_dashboard", "AIForecastDashboard"
        )
        self._safe_import_register("hpc_connector", "acf.hpc_connector", "HPCConnectionManager")

    def _build_search_index(self) -> None:
        """Populate global search index with modules, classes, parameters, and commands."""
        self.search_index.clear()

        # 1. Registered modules
        for key, instance in self.modules.items():
            if instance is not None:
                cls_name = instance.__class__.__name__
                self.search_index.append(
                    {"type": "module", "name": key, "category": "Subsystem", "detail": f"Class: {cls_name}"}
                )

        # 2. Scientific Parameters
        params = [
            ("2m Temperature (T2M)", "Atmospheric Property", "Surface air temperature at 2 meters"),
            ("Mean Sea Level Pressure (MSLP)", "Synoptic Weather", "Atmospheric pressure reduced to mean sea level"),
            ("10m Wind Speed (U10/V10)", "Wind Vector", "Horizontal wind vector components at 10 meters"),
            (
                "CAPE / CIN Instability",
                "Severe Convective Storms",
                "Convective Available Potential Energy / Inhibition",
            ),
            ("Sea Surface Temperature (SST)", "Ocean Hydrodynamics", "Temperature of top ocean layer"),
            ("Fourier Neural Operator (FNO)", "AI Surrogate Model", "Neural operator for 1000x NWP acceleration"),
            ("4D-Var Data Assimilation", "Data Assimilation", "Four-Dimensional Variational Data Assimilation"),
            ("Planetary Health Score", "Planetary Dashboard", "Composite indicator of 9 Earth boundaries"),
        ]
        for name, cat, det in params:
            self.search_index.append({"type": "parameter", "name": name, "category": cat, "detail": det})

    def global_search(self, query: str) -> list[dict[str, str]]:
        """Perform universal search across modules, classes, parameters, and datasets."""
        if not query or len(query.strip()) == 0:
            return []

        q = query.lower().strip()
        results = []
        for item in self.search_index:
            if q in item["name"].lower() or q in item["category"].lower() or q in item["detail"].lower():
                results.append(item)
        return results

    def build_system_tree(self) -> dict[str, Any]:
        """Generate a hierarchical tree of packages, modules, classes, and public methods."""
        tree = {
            "Earth System": [
                "Atmosphere",
                "Ocean",
                "Hydrology",
                "Cryosphere",
                "Biosphere",
                "Land Surface",
                "Carbon Cycle",
                "Atmospheric Chemistry",
                "Air Quality",
                "Aerosols",
                "Dust",
                "Wildfires",
                "Volcanoes",
                "Geology",
            ],
            "Forecast": ["Short-Range NWP", "Medium-Range (15 days)", "Global Circulation"],
            "Assimilation": ["4D-Var Solver", "EnKF (50-member)", "Hybrid 4DEnVar", "Quality Control"],
            "Simulation": ["Coupled Earth Solver", "Finite Volume", "Spectral Solver", "AMR"],
            "Digital Twin": ["Present Earth", "Historical Replay", "2030", "2050", "2100", "2300"],
            "Climate": ["CMIP6 Trajectories", "SSP1-1.9 to SSP5-8.5", "Sea Level Rise"],
            "Planetary Limits": ["9 Planetary Boundaries Audit", "Freshwater & Biosphere"],
            "Geoengineering": ["Stratospheric Aerosol Injection", "Direct Air Capture (DACCS)"],
            "Artificial Intelligence": ["Fourier Neural Operators (FNO)", "GNN Surrogates", "PINN Models"],
            "Machine Learning": ["Model Calibration", "Feature Importance", "Uncertainty Quant"],
            "Earth Physics": ["Mass/Energy Conservation", "Navier-Stokes", "Thermodynamics"],
            "Monitoring": ["GOES/MTG Satellites", "NEXRAD Radar", "SYNOP/METAR AWS", "ARGO Floats"],
            "Verification": ["RMSE & MAE", "ACC Correlation", "CRPS & Brier Score", "ROC Curve"],
            "Products": ["Weather Bulletins", "Aviation SIGMETs", "Hydrological Warnings"],
            "Reports": ["Executive Risk Briefings", "Climate Impact Assessments"],
            "Catalog": ["WMO Standards", "CF-1.8 Conventions", "ECMWF Parameters"],
            "Output": ["NetCDF4 Files", "Cloud Zarr Stores", "GRIB2 Datasets", "GeoTIFF Maps"],
            "Settings": ["Workspace Modes", "Layer Preferences", "API Keys", "System Config"],
            "Plugins": ["Custom Physics Extensions", "AI Model Plug-ins"],
            "HPC": ["MPI Domain Topology", "CUDA GPU Kernels", "Checkpoints", "Memory Bandwidth"],
        }
        return tree

    def get_module(self, name: str) -> Any | None:
        """Retrieve instantiated subsystem by module key name."""
        return self.modules.get(name)

    def list_modules(self) -> list[str]:
        """List all registered module keys."""
        return sorted(self.modules.keys())

    def is_connected(self, name: str) -> bool:
        """Verify if target subsystem is instantiated and operational."""
        return name in self.modules and self.modules[name] is not None

    def get_system_status_summary(self) -> dict[str, Any]:
        """Return connectivity status dictionary for all registered engines."""
        return {
            "total_modules": len(self.modules),
            "connected_count": sum(1 for m in self.modules.values() if m is not None),
            "modules": {k: (v is not None) for k, v in self.modules.items()},
        }
