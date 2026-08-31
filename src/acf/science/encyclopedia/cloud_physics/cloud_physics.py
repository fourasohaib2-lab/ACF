"""
Atmospheric Complexity Framework (ACF)

Cloud Physics, Nucleation, Microphysics & Hydrometeors Encyclopedia Module
"""

import math

from acf.science.encyclopedia.entry import EncyclopediaEntry
from acf.science.encyclopedia.registry import EncyclopediaRegistry

# ---------------------------------------------------------------------------
# Computational Functions for Cloud Physics
# ---------------------------------------------------------------------------


def calculate_homogeneous_nucleation_rate(temp_c: float) -> float:
    """Calcul approximatif du taux de nucléation homogène de la glace en sous-refroidissement J(T).

    NOTE (correction): used a -35°C cutoff, inconsistent with this entry's
    own equation/description text (both state the standard, widely-cited
    -38°C homogeneous-freezing threshold for pure water droplets - the
    "limitations" field's -35°C was the odd one out). Aligned to -38°C.
    """
    if temp_c >= -38.0:
        return 0.0
    return math.exp(0.5 * (-temp_c - 38.0))


def calculate_two_moment_size_distribution(n0: float, lambda_param: float, diameter_m: float, mu: float = 0.0) -> float:
    """Calcul de la distribution en taille de gouttes N(D) = N0 * D^mu * exp(-lambda * D) (Gamma distribution)."""
    if diameter_m <= 0.0 or lambda_param <= 0.0:
        return 0.0
    return n0 * (diameter_m**mu) * math.exp(-lambda_param * diameter_m)


# ---------------------------------------------------------------------------
# Encyclopedia Entries
# ---------------------------------------------------------------------------

ENTRIES: list[EncyclopediaEntry] = [
    # --- NUCLEATION ---
    EncyclopediaEntry(
        key="homogeneous_nucleation_ice",
        name="Nucléation Homogène de la Glace",
        domain="Physique des Nuages",
        subdomain="Microphysique",
        equation="J_hom = A * exp(-Delta_G_crit / (k_B * T)) à T < -38 deg C",
        latex_equation=r"J_{\text{hom}}(T) = C \exp\left(-\frac{\Delta G^*}{k_B T}\right), \quad T \le -38^\circ\text{C}",
        variables={
            "J_hom": "Taux de congélation spontanée (cm⁻³·s⁻¹)",
            "Delta_G": "Énergie libre critique de germination",
        },
        units={"J": "cm⁻³·s⁻¹"},
        description="Congélation spontanée des gouttelettes d'eau pure surfondue sans présence de noyaux glaçogènes lorsque la température descend en dessous de -38°C (235.15 K).",
        application_conditions=["Troposphère supérieure et cirrus"],
        limitations=["Inexistante au-dessus de -38°C dans l'atmosphère réelle"],
        references=["Pruppacher & Klett (1997)", "Koop et al. (2000) Nature"],
        compute_func=calculate_homogeneous_nucleation_rate,
    ),
    EncyclopediaEntry(
        key="heterogeneous_nucleation_ice",
        name="Nucléation Hétérogène (Aérosols CCN & INP)",
        domain="Physique des Nuages",
        subdomain="Microphysique",
        equation="N_INP(T) = N_0 * exp(a * (T_subzero))",
        latex_equation=r"N_{\text{INP}}(T) = A \exp\left(\beta (T_0 - T)\right), \quad T < 0^\circ\text{C}",
        variables={"INP": "Ice Nucleating Particles (Noyaux glaçogènes)", "CCN": "Cloud Condensation Nuclei"},
        units={"N_INP": "L⁻¹"},
        description="Congélation ou condensation-congélation de l'eau provoquée par des particules d'aérosols solides spécifiques (poussières du Sahara, suies, bactéries) à des températures supérieures à -38°C.",
        application_conditions=["Formation de glace entre 0°C et -38°C"],
        limitations=["Faible concentration d'INP à haute température (-5°C à -15°C)"],
        references=["Meyers et al. (1992) J. Appl. Meteor.", "DeMott et al. (2010) PNAS"],
    ),
    # --- PHASE TRANSITIONS ---
    EncyclopediaEntry(
        key="cloud_condensation_process",
        name="Condensation Nuageuse",
        domain="Physique des Nuages",
        subdomain="Changements de phase",
        equation="dq_c/dt = max(0, q - q_sat) / dt",
        latex_equation=r"\frac{dq_c}{dt} = \frac{q - q_{\text{sat}}(T)}{\tau_{\text{cond}}} \cdot \mathcal{H}(q - q_{\text{sat}})",
        variables={"qc": "Eau nuageuse (kg/kg)", "q_sat": "Humidité spécifique à saturation"},
        units={"dq/dt": "kg/(kg·s)"},
        description="Passage de la vapeur d'eau à l'état liquide sur les noyaux de condensation (CCN) lorsque l'humidité relative dépasse 100%.",
        application_conditions=["Sursaturation par rapport à l'eau liquide (RH > 100%)"],
        limitations=["Nécessite la prise en compte du réchauffement par libération de chaleur latente"],
        references=["Pruppacher & Klett (1997)", "WMO Cloud Manual"],
    ),
    EncyclopediaEntry(
        key="cloud_evaporation_process",
        name="Évaporation Nuageuse et Précipitante",
        domain="Physique des Nuages",
        subdomain="Changements de phase",
        equation="dq_v/dt = C_evap * (q_sat - q) * Rain_Term",
        latex_equation=r"\frac{dq_v}{dt} = 2\pi D N_r f(Re, Sc) \frac{S - 1}{\frac{L_v^2}{K R_v T^2} + \frac{1}{\rho q_{\text{sat}} D_v}}",
        variables={"S": "Sous-saturation (e/es < 1)", "N_r": "Nombre de gouttes de pluie"},
        units={"dq/dt": "kg/(kg·s)"},
        description="Vaporisation des gouttelettes nuageuses ou des gouttes de pluie traversant une couche d'air sous-saturée (RH < 100%), provoquant un refroidissement diabolique par absorption de chaleur latente.",
        application_conditions=["Zones subsidentes ou sous la base nuageuse"],
        limitations=["Refroidissement pouvant déclencher une microrafale descendante (microburst)"],
        references=["Kessler (1969)", "Pruppacher & Klett (1997)"],
    ),
    EncyclopediaEntry(
        key="ice_deposition_sublimation",
        name="Déposition et Sublimation de la Glace",
        domain="Physique des Nuages",
        subdomain="Changements de phase",
        equation="dq_i/dt = 4 * C_crystal * (e - e_i) / Term_thermo",
        latex_equation=r"\frac{dq_i}{dt} = \frac{4\pi C (S_i - 1)}{\frac{L_s^2}{K R_v T^2} + \frac{1}{\rho q_{si} D_v}}",
        variables={
            "Si": "Sursaturation par rapport à la glace (e / e_i)",
            "C": "Capacité géométrique du cristal de glace",
        },
        units={"dq/dt": "kg/(kg·s)"},
        description="Transfert direct de vapeur d'eau vers la phase solide (déposition) ou de la glace vers la vapeur (sublimation) sans passer par la phase liquide.",
        application_conditions=["Nuages glacés et cirrus entre -10°C et -50°C"],
        limitations=["Forme géométrique des cristaux modifiant la constante C (plaques, aiguilles, dendrites)"],
        references=["Bergeron (1935)", "Pruppacher & Klett (1997)"],
    ),
    # --- HYDROMETEOR SPECIES ---
    EncyclopediaEntry(
        key="hydrometeor_cloud_water",
        name="Hydrométéore Eau Nuageuse (Cloud Water - qc)",
        domain="Physique des Nuages",
        subdomain="Espèces d'hydrométéores",
        equation="qc = mass_liquid / mass_air,  diamètre 5 to 30 microns",
        latex_equation=r"q_c = \frac{m_{\text{droplets}}}{m_{\text{air}}}, \quad \bar{D} \sim 10\text{ }\mu\text{m}, \quad v_t \approx 0\text{ m/s}",
        variables={"qc": "Contenu en eau liquide nuageuse (g/m³ ou kg/kg)"},
        units={"qc": "kg/kg"},
        description="Micro-gouttelettes d'eau liquide en suspension dans le nuage conservant une vitesse de chute négligeable par rapport aux mouvements d'air.",
        application_conditions=["Nuages chauds et zones surfondues des Cumulonimbus"],
        limitations=["Transformée en pluie par autoconversion et accrétion"],
        references=["WMO Microphysics", "ECMWF Physics Documentation"],
    ),
    EncyclopediaEntry(
        key="hydrometeor_cloud_ice",
        name="Hydrométéore Glace Nuageuse (Cloud Ice - qi)",
        domain="Physique des Nuages",
        subdomain="Espèces d'hydrométéores",
        equation="qi = mass_ice / mass_air,  diamètre 10 to 100 microns",
        latex_equation=r"q_i = \frac{m_{\text{crystals}}}{m_{\text{air}}}, \quad \bar{D} \sim 50\text{ }\mu\text{m}",
        variables={"qi": "Contenu en glace nuageuse (kg/kg)"},
        units={"qi": "kg/kg"},
        description="Petits cristaux de glace en suspension dans les cirrus et au sommet des nimbostratus et cumulonimbus.",
        application_conditions=["T < 0°C dans les nuages stratiformes et convectifs"],
        limitations=["Sédimentation lente"],
        references=["WMO Microphysics", "Thompson et al. (2008)"],
    ),
    EncyclopediaEntry(
        key="hydrometeor_rain",
        name="Hydrométéore Pluie (Rain Water - qr)",
        domain="Physique des Nuages",
        subdomain="Espèces d'hydrométéores",
        equation="qr = mass_rain / mass_air,  diamètre 0.5 to 6 mm",
        latex_equation=r"q_r = \frac{m_{\text{rain}}}{m_{\text{air}}}, \quad v_t(D) = 9.65 - 10.3 \exp(-600 D)",
        variables={"qr": "Contenu en eau précipitante (kg/kg)", "vt": "Vitesse terminale de chute (2 à 9 m/s)"},
        units={"qr": "kg/kg", "vt": "m/s"},
        description="Gouttes d'eau liquide de taille suffisante (D > 0.5 mm) pour tomber sous l'effet de la gravité à travers les courants atmosphériques.",
        application_conditions=["Précipitations au sol sous l'isotherme 0°C"],
        limitations=["Rupture des gouttes (breakup) au-delà de D > 6 mm"],
        references=["Gunn & Kinzer (1949)", "Kessler (1969)"],
    ),
    EncyclopediaEntry(
        key="hydrometeor_snow",
        name="Hydrométéore Neige (Snow - qs)",
        domain="Physique des Nuages",
        subdomain="Espèces d'hydrométéores",
        equation="qs = mass_snow / mass_air,  agrégats de cristaux",
        latex_equation=r"q_s = \frac{m_{\text{snow}}}{m_{\text{air}}}, \quad v_t \approx 1 \text{ m/s}, \quad \rho_s \approx 100 \text{ kg/m}^3",
        variables={"qs": "Contenu en neige (kg/kg)", "rho_s": "Masse volumique de la neige (kg/m³)"},
        units={"qs": "kg/kg"},
        description="Agrégats de cristaux de glace de forme complexe tombant lentement (vitesse de chute ~ 1 m/s).",
        application_conditions=["Précipitations solides hivernales"],
        limitations=["Grande variabilité de densité (50 à 300 kg/m³)"],
        references=["Lin et al. (1983)", "Thompson et al. (2008)"],
    ),
    EncyclopediaEntry(
        key="hydrometeor_graupel",
        name="Hydrométéore Graupel / Neige Roulée (qg)",
        domain="Physique des Nuages",
        subdomain="Espèces d'hydrométéores",
        equation="qg = mass_graupel / mass_air,  densité 400 to 800 kg/m3",
        latex_equation=r"q_g = \frac{m_{\text{graupel}}}{m_{\text{air}}}, \quad \rho_g \approx 400\text{--}800 \text{ kg/m}^3, \quad v_t \approx 2\text{--}4 \text{ m/s}",
        variables={"qg": "Contenu en graupel (kg/kg)"},
        units={"qg": "kg/kg"},
        description="Billes de glace poreuse formées par accrétion et givrage de gouttelettes d'eau surfondue sur des cristaux de glace. Élément clé de la foudre et des orages.",
        application_conditions=["Zone de phase mixte convective des Cumulonimbus"],
        limitations=["Nécessite la modélisation à 2 moments pour séparer graupel et grêle"],
        references=["Rutledge & Hobbs (1984)", "AROME ICE3 Scheme Manual"],
    ),
    # --- TWO MOMENT MICROPHYSICS ---
    EncyclopediaEntry(
        key="two_moment_microphysics_scheme",
        name="Paramétrisation Microphysique à 2 Moments",
        domain="Physique des Nuages",
        subdomain="Schémas NWP",
        equation="Prédiction simultanée du rapport de mélange q_x et de la concentration numérique N_x",
        latex_equation=r"\frac{\partial q_x}{\partial t} = \text{Physique}(q_x, N_x), \quad \frac{\partial N_x}{\partial t} = \text{Physique}(N_x, q_x)",
        variables={"qx": "Masse de l'espèce x (kg/kg)", "Nx": "Concentration numérique de l'espèce x (m⁻³)"},
        units={"Nx": "m⁻³"},
        description="Schéma microphysique moderne (ex: Morrison, WDM6, Seifert-Beheng, Meso-NH LIMA) calculant à la fois la masse et le nombre de particules par unité de volume pour une meilleure précision du spectre de gouttes.",
        application_conditions=["Modèles NWP à très haute résolution et prévision des orages/grêle"],
        limitations=["Doublement du nombre de variables pronostiques transportées (coût mémoire/calcul)"],
        references=["Morrison et al. (2005) Mon. Wea. Rev.", "Lim & Hong (2010) (WDM6)", "Seifert & Beheng (2006)"],
        compute_func=calculate_two_moment_size_distribution,
    ),
]

for entry in ENTRIES:
    EncyclopediaRegistry.register(entry)
