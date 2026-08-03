"""
Atmospheric Complexity Framework (ACF)

Neural Weather Prediction Models Registry & Metadata Module
(GraphCast, FourCastNet, Pangu-Weather, ClimaX, GenCast, NeuralGCM, FengWu, Aurora, AROME-AI, ECMWF-AIFS)
"""

from dataclasses import dataclass
from typing import Dict, List, Optional


@dataclass
class NeuralWeatherModelInfo:
    """Description scientifique complète d'un modèle d'IA météorologique."""
    key: str
    name: str
    institution: str
    architecture: str
    spatial_resolution_deg: float
    vertical_levels: int
    inputs: List[str]
    outputs: List[str]
    max_lead_time_days: int
    physics_assumptions: str
    training_datasets: List[str]
    limitations: List[str]
    references: List[str]
    operational_applications: List[str]


NEURAL_MODELS_REGISTRY: Dict[str, NeuralWeatherModelInfo] = {
    "graphcast": NeuralWeatherModelInfo(
        key="graphcast",
        name="GraphCast (Google DeepMind)",
        institution="Google DeepMind / ECMWF",
        architecture="Graph Neural Network (GNN) on icosahedral multi-mesh",
        spatial_resolution_deg=0.25,
        vertical_levels=37,
        inputs=["T", "U", "V", "Q", "Z", "MSLP", "2T", "10U", "10V", "TP"],
        outputs=["T", "U", "V", "Q", "Z", "MSLP", "2T", "10U", "10V", "TP"],
        max_lead_time_days=10,
        physics_assumptions="Prédit les tendances thermodynamiques et dynamiques globales sans résolution explicite des équations navier-stokes.",
        training_datasets=["ECMWF ERA5 Reanalysis (1979-2017)"],
        limitations=["Tendance au lissage des extrêmes pluviométriques locaux au-delà du jour 7"],
        references=["Lam et al. (2023) Science 382, 1416-1421"],
        operational_applications=["Prévision synoptique mondiale 10 jours, trajectoires de cyclones"],
    ),
    "fourcastnet": NeuralWeatherModelInfo(
        key="fourcastnet",
        name="FourCastNet v2 (NVIDIA Earth-2)",
        institution="NVIDIA / NERSC",
        architecture="Adaptive Fourier Neural Operator (AFNO) + Vision Transformer",
        spatial_resolution_deg=0.25,
        vertical_levels=13,
        inputs=["U10", "V10", "T2M", "SP", "MSL", "U500", "V500", "Z500", "T500", "TCWV"],
        outputs=["U10", "V10", "T2M", "SP", "MSL", "U500", "V500", "Z500", "T500", "TCWV"],
        max_lead_time_days=14,
        physics_assumptions="Opérateur spectral de Fourier modélisant les interactions de petite et grande échelle dans le domaine fréquentiel.",
        training_datasets=["ECMWF ERA5 Reanalysis"],
        limitations=["Dérive thermique moyenne sur les simulations à très long terme (> 30 jours)"],
        references=["Pathak et al. (2022) arXiv:2202.11214", "Kurth et al. (2023) PASC"],
        operational_applications=["NVIDIA Earth-2 Digital Twin, prévision rapide d'ensembles super-résolus"],
    ),
    "pangu_weather": NeuralWeatherModelInfo(
        key="pangu_weather",
        name="Pangu-Weather (Huawei Cloud)",
        institution="Huawei Inc.",
        architecture="3D Earth-Specific Swin Transformer with Hierarchical Spatial Aggregation",
        spatial_resolution_deg=0.25,
        vertical_levels=13,
        inputs=["Z", "Q", "T", "U", "V", "MSLP", "U10", "V10", "T2M"],
        outputs=["Z", "Q", "T", "U", "V", "MSLP", "U10", "V10", "T2M"],
        max_lead_time_days=7,
        physics_assumptions="Capture 3D explicite des structures d'altitude et de la géométrie sphérique de la Terre.",
        training_datasets=["ECMWF ERA5 Reanalysis (1979-2021)"],
        limitations=["Modèles d'entraînement séparés pour les échéances de 1h, 3h, 6h et 24h"],
        references=["Bi et al. (2023) Nature 619, 533-538"],
        operational_applications=["Prévision rapide de trajectoire de typhon et vagues de chaleur"],
    ),
    "gencast": NeuralWeatherModelInfo(
        key="gencast",
        name="GenCast (Google DeepMind Diffusion Model)",
        institution="Google DeepMind",
        architecture="Conditional Diffusion Model on Icosahedral Mesh",
        spatial_resolution_deg=0.25,
        vertical_levels=37,
        inputs=["Full Atmospheric State at t_0 and t_-6h"],
        outputs=["Ensemble Forecast Distributions at t+dt"],
        max_lead_time_days=15,
        physics_assumptions="Modélisation stochastique de l'incertitude sous-maille par processus de diffusion inverse.",
        training_datasets=["ERA5 Reanalysis"],
        limitations=["Coût de calcul d'échantillonnage par rapport aux modèles autorégressifs déterministes"],
        references=["Price et al. (2024) Nature / DeepMind Research"],
        operational_applications=["Génération stochastique d'ensembles météorologiques mondiaux"],
    ),
    "neuralgcm": NeuralWeatherModelInfo(
        key="neuralgcm",
        name="NeuralGCM (Google Research & ECMWF)",
        institution="Google Research / ECMWF",
        architecture="Differentiable Dynamical Core (Spectral Solver) + Neural Parameterizations",
        spatial_resolution_deg=0.7,
        vertical_levels=32,
        inputs=["Fluid Dynamics State Vector (Vor, Div, T, Q, LnSp)"],
        outputs=["Subgrid Physical Tendencies (dT/dt, dq/dt, du/dt, dv/dt)"],
        max_lead_time_days=30,
        physics_assumptions="Combine la conservation exacte des équations primitives (solveur dynamique) avec des réseaux de neurones pour les processus physiques sous-maille.",
        training_datasets=["ERA5 Reanalysis & Hybrid Physics Constraints"],
        limitations=["Résolution spectrale T63/T127 limitée aux simulations climat/moyen terme"],
        references=["Kochkov et al. (2024) Nature 632, 1060-1067"],
        operational_applications=["Prévisions mensuelles et saisonnières hybrides physique-IA"],
    ),
    "arome_ai": NeuralWeatherModelInfo(
        key="arome_ai",
        name="AROME-AI (Météo-France)",
        institution="Météo-France / CNRS",
        architecture="Convective-Scale Deep Residual Neural Network",
        spatial_resolution_deg=0.025,
        vertical_levels=90,
        inputs=["T", "q_v", "q_c", "q_r", "q_s", "q_g", "U", "V", "W", "P_sfc"],
        outputs=["T", "q_v", "q_c", "q_r", "q_s", "q_g", "U", "V", "W", "P_sfc"],
        max_lead_time_days=2,
        physics_assumptions="Emulateur haute résolution méso-échelle préservant l'instabilité convective.",
        training_datasets=["AROME Operational Reanalysis & Forecasts"],
        limitations=["Emprise géographique limitée à l'Europe occidentale"],
        references=["Météo-France AI Lab (2024) Research Note"],
        operational_applications=["Prévision immédiate d'orages violents et crues éclairs en France"],
    ),
    "ecmwf_aifs": NeuralWeatherModelInfo(
        key="ecmwf_aifs",
        name="ECMWF-AIFS (Artificial Intelligence Forecasting System)",
        institution="ECMWF",
        architecture="Graph Neural Network on Anisotropic Mesh with Spherical Harmonics Bias Correction",
        spatial_resolution_deg=0.25,
        vertical_levels=137,
        inputs=["ECMWF Operational Analysis (ODIM / GRIB2)"],
        outputs=["10-Day Deterministic & Ensemble Medium-Range Weather Fields"],
        max_lead_time_days=10,
        physics_assumptions="Entraîné directement sur l'analyse opérationnelle IFS haute résolution.",
        training_datasets=["ECMWF Operational Analysis (2019-2024)"],
        limitations=["Sous-estimation ponctuelle des vents extrêmes au cœur des dépressions explosives"],
        references=["Lang et al. (2024) ECMWF Newsletter No. 178"],
        operational_applications=["Bulletin officiel d'IA d'ECMWF diffusé en temps réel aux services nationaux"],
    ),
}


class NeuralWeatherModelEngine:
    """Moteur d'exécution et d'interrogation des modèles d'IA météorologiques."""

    @classmethod
    def get_model(cls, key: str) -> Optional[NeuralWeatherModelInfo]:
        return NEURAL_MODELS_REGISTRY.get(key.lower())

    @classmethod
    def list_models(cls) -> List[str]:
        return list(NEURAL_MODELS_REGISTRY.keys())
