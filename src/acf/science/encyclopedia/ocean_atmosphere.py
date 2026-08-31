"""
Atmospheric Complexity Framework (ACF)

Ocean-Atmosphere Coupled Dynamics, Surface Fluxes & Teleconnections Encyclopedia Module
"""

from acf.science.encyclopedia.entry import EncyclopediaEntry
from acf.science.encyclopedia.registry import EncyclopediaRegistry

# ---------------------------------------------------------------------------
# Computational Functions for Ocean-Atmosphere Exchanges
# ---------------------------------------------------------------------------


def calculate_sensible_heat_flux(
    rho: float, cp: float, u10: float, ts_k: float, ta_k: float, ch: float = 1.1e-3
) -> float:
    """Calcul du flux de chaleur sensible H = rho * cp * Ch * U10 * (Ts - Ta) en W/m²."""
    return rho * cp * ch * u10 * (ts_k - ta_k)


def calculate_latent_heat_flux(rho: float, lv: float, u10: float, qs: float, qa: float, ce: float = 1.1e-3) -> float:
    """Calcul du flux de chaleur latent LE = rho * Lv * Ce * U10 * (qs - qa) en W/m²."""
    return rho * lv * ce * u10 * (qs - qa)


def calculate_nao_index(
    slp_azores_hpa: float,
    slp_iceland_hpa: float,
    mean_azores: float = 1022.0,
    mean_iceland: float = 1000.0,
    std_azores: float = 5.0,
    std_iceland: float = 8.0,
) -> float:
    """Calcul de l'indice de l'Oscillation Nord-Atlantique (NAO)."""
    norm_azores = (slp_azores_hpa - mean_azores) / std_azores
    norm_iceland = (slp_iceland_hpa - mean_iceland) / std_iceland
    return norm_azores - norm_iceland


# ---------------------------------------------------------------------------
# Encyclopedia Entries
# ---------------------------------------------------------------------------

ENTRIES: list[EncyclopediaEntry] = [
    EncyclopediaEntry(
        key="sensible_heat_flux_bulk",
        name="Flux de Chaleur Sensible Océan-Atmosphère",
        domain="Océan-Atmosphère",
        subdomain="Échanges de surface",
        equation="H = rho * cp * Ch * U10 * (Ts - Ta)",
        latex_equation=r"H = \rho c_p C_h U_{10} (T_s - T_a)",
        variables={
            "rho": "Masse volumique de l'air (kg/m³)",
            "cp": "1004 J/(kg·K)",
            "Ch": "Coefficient de transfert neutre (~1.1e-3)",
            "U10": "Vent à 10m (m/s)",
            "Ts": "SST (K)",
            "Ta": "Température air à 2m (K)",
        },
        units={"H": "W/m²"},
        description="Transfert d'énergie thermique par conduction et convection directe entre la surface de l'océan et l'air marin superposé.",
        application_conditions=["Couche limite de surface marine"],
        limitations=["Formulation neutre modifiée en fonction de la stabilité Monin-Obukhov (COARE 3.0)"],
        references=["COARE 3.0 Bulk Algorithm", "Fairall et al. (2003) J. Climate", "WMO Surface Flux Manual"],
        compute_func=calculate_sensible_heat_flux,
    ),
    EncyclopediaEntry(
        key="latent_heat_flux_bulk",
        name="Flux de Chaleur Latente Océan-Atmosphère",
        domain="Océan-Atmosphère",
        subdomain="Échanges de surface",
        equation="LE = rho * Lv * Ce * U10 * (qs - qa)",
        latex_equation=r"LE = \rho L_v C_e U_{10} (q_s - q_a)",
        variables={
            "Lv": "Chaleur latente de vaporisation (2.5e6 J/kg)",
            "Ce": "Coefficient d'évaporation (~1.1e-3)",
            "qs": "Humidité spécifique à saturation à la SST",
            "qa": "Humidité de l'air",
        },
        units={"LE": "W/m²"},
        description="Transfert d'énergie associée à l'évaporation de l'eau de mer, composante majeure du bilan thermique des océans tropicaux et moteur des cyclones.",
        application_conditions=["Interface mer-air"],
        limitations=["Corrections pour embruns sous vents violents (U > 20 m/s)"],
        references=["Fairall et al. (2003)", "ECMWF Coupled Ocean-Atmosphere Docs"],
        compute_func=calculate_latent_heat_flux,
    ),
    EncyclopediaEntry(
        key="el_nino_southern_oscillation_enso",
        name="Oscillation Australe El Niño (ENSO)",
        domain="Océan-Atmosphère",
        subdomain="Variabilité climatique couplée",
        equation="Couplage Océan-Atmosphère Pacifique Tropical: SST Niño 3.4 & SOI Index",
        latex_equation=r"\text{SOI} = 10 \times \left[ \frac{\text{SLP}_{\text{Tahiti}}^* - \text{SLP}_{\text{Darwin}}^*}{\sigma_{\Delta p}} \right]",
        variables={
            "SST_Nino3.4": "Anomalie de température Pacifique équatorial central (°C)",
            "SOI": "Southern Oscillation Index",
        },
        units={"SST_anomaly": "°C", "SOI": "dimensionless"},
        description="Mode majeur de variabilité interannuelle du climat terrestre résultant du couplage entre la circulation atmosphérique de Walker et les températures de surface du Pacifique.",
        application_conditions=["Pacifique équatorial"],
        limitations=["Périodicité irrégulière entre 2 et 7 ans"],
        references=["Bjerknes (1969) Mon. Wea. Rev.", "NOAA CPC Climate Diagnostics", "WMO ENSO Updates"],
    ),
    EncyclopediaEntry(
        key="el_nino_warm_phase",
        name="Phase Chaude El Niño",
        domain="Océan-Atmosphère",
        subdomain="Variabilité climatique couplée",
        equation="Anomalie SST Niño 3.4 > +0.5 °C pendant 5 mois consécutifs",
        latex_equation=r"\Delta T_{\text{Niño 3.4}} \ge +0.5^\circ\text{C}, \quad \text{Affaiblissement des Alizés}",
        variables={"Alizés": "Vents d'Est Pacifique équatorial (affaiblis ou inversés)"},
        units={"Anomalie": "°C"},
        description="Phase chaude de l'ENSO caractérisée par un réchauffement des eaux du Pacifique Est, l'effondrement des alizés et le déplacement de la convection profonde vers le centre du Pacifique.",
        application_conditions=["Analyse des téléconnexions mondiales"],
        limitations=["Impacts Asymétriques selon le type Modoki ou Central Pacific"],
        references=["NOAA CPC", "Trenberth (1997) Bull. Amer. Meteor. Soc."],
    ),
    EncyclopediaEntry(
        key="la_nina_cold_phase",
        name="Phase Froide La Niña",
        domain="Océan-Atmosphère",
        subdomain="Variabilité climatique couplée",
        equation="Anomalie SST Niño 3.4 < -0.5 °C pendant 5 mois consécutifs",
        latex_equation=r"\Delta T_{\text{Niño 3.4}} \le -0.5^\circ\text{C}, \quad \text{Renforcement des Alizés}",
        variables={"Alizés": "Vents d'Est renforcés", "Upwelling": "Remontée d'eau froide intense au Pérou"},
        units={"Anomalie": "°C"},
        description="Phase froide de l'ENSO caractérisée par un renforcement des alizés d'Est, un upwelling intense le long des côtes sud-américaines et un confinement de la piscine chaude à l'Indonésie.",
        application_conditions=["Prévision saisonnière globale"],
        limitations=["Accentuations des sécheresses sur le sud des États-Unis et pluies intenses en Australie"],
        references=["NOAA CPC", "WMO El Niño/La Niña Bulletins"],
    ),
    EncyclopediaEntry(
        key="north_atlantic_oscillation_nao",
        name="Oscillation Nord-Atlantique (NAO)",
        domain="Océan-Atmosphère",
        subdomain="Variabilité climatique régionale",
        equation="NAO_index = Normalized_SLP(Açores) - Normalized_SLP(Islande)",
        latex_equation=r"\text{NAO} = \text{SLP}_{\text{Açores}}^* - \text{SLP}_{\text{Islande}}^*",
        variables={"SLP_Azores": "Pression surface Açores (hPa)", "SLP_Iceland": "Pression surface Islande (hPa)"},
        units={"NAO": "dimensionless"},
        description="Mode de variabilité atmosphérique majeur du bassin Atlantique Nord contrôlant le rail des tempêtes et les régimes de temps hivernaux en Europe.",
        application_conditions=["Atlantique Nord & Europe"],
        limitations=["Variabilité intra-saisonnière à décennale"],
        references=["Hurrell (1995) Science", "NOAA CPC Teleconnections"],
        compute_func=calculate_nao_index,
    ),
    EncyclopediaEntry(
        key="atlantic_multidecadal_oscillation_amo",
        name="Oscillation Multidécennale de l'Atlantique (AMO)",
        domain="Océan-Atmosphère",
        subdomain="Variabilité climatique basse fréquence",
        equation="Anomalie détrendée de la SST moyenne Atlantique Nord (0-60°N)",
        latex_equation=r"\text{AMO} = \text{SST}_{\text{Atl. North}} - \text{Tendance}_{\text{globale}}",
        variables={"Period": "Cycle de 60 à 80 ans"},
        units={"AMO": "°C"},
        description="Fluctuation basse fréquence des températures de surface de la mer dans l'Atlantique Nord liée aux variations de la circulation méridienne de retournement (AMOC).",
        application_conditions=["Climatologie et prévision décennale"],
        limitations=["Séparation complexe entre variabilité naturelle et réchauffement anthropique"],
        references=["Enfield et al. (2001) Geophys. Res. Lett.", "IPCC AR6 WG1 Report"],
    ),
    EncyclopediaEntry(
        key="pacific_decadal_oscillation_pdo",
        name="Oscillation Décennale du Pacifique (PDO)",
        domain="Océan-Atmosphère",
        subdomain="Variabilité climatique basse fréquence",
        equation="Premier mode EOF des anomalies de SST Pacifique Nord (au nord de 20°N)",
        latex_equation=r"\text{PDO} = \text{EOF}_1(\text{SST}_{\text{Pacific North}})",
        variables={"Période": "20 à 30 ans"},
        units={"PDO": "dimensionless"},
        description="Pattern récurrent de variabilité Océan-Atmosphère dans le Pacifique Nord modulant les impacts de l'ENSO sur des échelles décennales.",
        application_conditions=["Pacifique Nord & Amérique du Nord"],
        limitations=["Mode résultant de plusieurs processus physiques distincts"],
        references=["Mantua et al. (1997) Bull. Amer. Meteor. Soc.", "NOAA NCEI PDO Index"],
    ),
]

for entry in ENTRIES:
    EncyclopediaRegistry.register(entry)
