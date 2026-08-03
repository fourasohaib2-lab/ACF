"""
Atmospheric Complexity Framework (ACF)

Advanced Turbulence, Boundary Layer Dynamics & Aviation CAT Encyclopedia Module
"""

from typing import List
from acf.science.encyclopedia.entry import EncyclopediaEntry
from acf.science.encyclopedia.registry import EncyclopediaRegistry

# ---------------------------------------------------------------------------
# Computational Functions for Turbulence & Boundary Layer
# ---------------------------------------------------------------------------

def calculate_kolmogorov_energy_spectrum(k: float, epsilon: float, c_k: float = 1.5) -> float:
    """Calcul du spectre d'énergie cinétique turbulente de Kolmogorov E(k) = C_k * epsilon^(2/3) * k^(-5/3)."""
    if k <= 0.0 or epsilon <= 0.0:
        return 0.0
    return c_k * (epsilon ** (2.0 / 3.0)) * (k ** (-5.0 / 3.0))


def calculate_gradient_richardson_number(g_over_theta: float, dtheta_dz: float, du_dz: float) -> float:
    """Calcul du Nombre de Richardson de Gradient (Ri)."""
    shear_sq = du_dz ** 2
    if shear_sq < 1e-10:
        shear_sq = 1e-10
    return (g_over_theta * dtheta_dz) / shear_sq


def calculate_ellrod_cat_index(shear: float, deformation: float) -> float:
    """Calcul de l'Indice de Turbulence en Air Clair (CAT) d'Ellrod & Knapp."""
    return shear * deformation


# ---------------------------------------------------------------------------
# Encyclopedia Entries
# ---------------------------------------------------------------------------

ENTRIES: List[EncyclopediaEntry] = [
    EncyclopediaEntry(
        key="kolmogorov_5_3_spectrum",
        name="Loi de Kolmogorov du Spectre Turbulent (-5/3)",
        domain="Turbulence Avancée",
        subdomain="Théorie de la turbulence",
        equation="E(k) = C_k * epsilon^(2/3) * k^(-5/3)",
        latex_equation=r"E(k) = C_k \varepsilon^{2/3} k^{-5/3}",
        variables={"k": "Nombre d'onde spatial (m⁻¹)", "epsilon": "Taux de dissipation de l'énergie cinétique (m²/s³)", "Ck": "Constante de Kolmogorov (~ 1.5)"},
        units={"E(k)": "m³/s²"},
        description="Loi universelle de la cascade d'énergie turbulente de Kolmogorov (1941) décrivant le transfert d'énergie des grands tourbillons vers les petites échelles dans la sous-zone inertielle.",
        application_conditions=["Sous-domaine inertiel de turbulence isotrope et homogène"],
        limitations=["Non valide dans la sous-zone de dissipation visqueuse"],
        references=["Kolmogorov (1941) Dokl. Akad. Nauk SSSR", "Stull (1988) Boundary Layer Meteorology"],
        compute_func=calculate_kolmogorov_energy_spectrum,
    ),
    EncyclopediaEntry(
        key="tke_prognostic_equation",
        name="Équation de Bilan de l'Énergie Cinétique Turbulente (TKE)",
        domain="Turbulence Avancée",
        subdomain="Paramétrisation de la turbulence",
        equation="de/dt = P_shear + P_buoyancy + Transports - dissipation_epsilon",
        latex_equation=r"\frac{\partial e}{\partial t} = -\overline{u^\prime w^\prime}\frac{\partial U}{\partial z} + \frac{g}{\theta_0}\overline{w^\prime \theta^\prime} - \frac{\partial}{\partial z}\left(\overline{w^\prime e} + \frac{\overline{w^\prime p^\prime}}{\rho_0}\right) - \varepsilon",
        variables={"P_shear": "Production par cisaillement", "P_buoyancy": "Production/destruction par flottabilité", "epsilon": "Dissipation visqueuse"},
        units={"e": "m²/s²", "epsilon": "m²/s³"},
        description="Équation pronostique fondamentale de la TKE décrivant l'énergie des fluctuations turbulentes dans la couche limite atmosphérique (ex: schémas EDMF dans AROME et IFS).",
        application_conditions=["Modélisation de la couche limite de surface et d'inversion"],
        limitations=["Hypothèses de fermeture de l'ordre 1.5 ou 2"],
        references=["Stull (1988)", "Mellor & Yamada (1982) Rev. Geophys."],
    ),
    EncyclopediaEntry(
        key="richardson_number_gradient",
        name="Nombre de Richardson de Gradient (Ri)",
        domain="Turbulence Avancée",
        subdomain="Stabilité de l'écoulement",
        equation="Ri = (g / theta) * (dtheta/dz) / (dU/dz)^2",
        latex_equation=r"Ri = \frac{\frac{g}{\theta_0}\frac{\partial \theta}{\partial z}}{\left(\frac{\partial U}{\partial z}\right)^2}",
        variables={"g_over_theta": "Gravité réduite g / theta_0", "dtheta_dz": "Gradient de température potentielle", "du_dz": "Cisaillement vertical du vent"},
        units={"Ri": "dimensionless"},
        description="Rapport sans dimension mesurant la stabilité thermique par rapport à la production mécanique par cisaillement. Ri < 0.25 (critique) indique le déclenchement de la turbulence dynamique (instabilité de Kelvin-Helmholtz).",
        application_conditions=["Cisaillement de jet-stream et couche limite stratifiée"],
        limitations=["Intermittence turbulente au-dessus du seuil critique"],
        references=["Richardson (1920)", "Miles & Howard (1964)", "AMS Turbulence Manual"],
        compute_func=calculate_gradient_richardson_number,
    ),
    EncyclopediaEntry(
        key="large_eddy_simulation_les",
        name="Simulation des Grands Tourbillons (LES)",
        domain="Turbulence Avancée",
        subdomain="Méthodes de simulation de la turbulence",
        equation="Filtrage spatial des équations de Navier-Stokes: resolved scales + Sub-Grid Scale (SGS)",
        latex_equation=r"\bar{u}_i = \int G(\mathbf{x} - \mathbf{x}^\prime) u_i(\mathbf{x}^\prime) d\mathbf{x}^\prime, \quad \tau_{ij}^{\text{sgs}} = \overline{u_i u_j} - \bar{u}_i \bar{u}_j",
        variables={"G": "Filtre spatial", "tau_sgs": "Tensor des contraintes sous-maille (Smagorinsky / Deardorff)"},
        units={"Maille": "10m à 100m"},
        description="Approche numérique résolvant explicitement les grands tourbillons turbulents contenant l'essentiel de l'énergie et modélisant uniquement les petites échelles sous-maille.",
        application_conditions=["Recherche en physique de la couche limite et convection très haute résolution"],
        limitations=["Très coûteux en ressources informatiques"],
        references=["Deardorff (1970) J. Fluid Mech.", "Moeng (1984) J. Atmos. Sci."],
    ),
    EncyclopediaEntry(
        key="direct_numerical_simulation_dns",
        name="Simulation Numérique Directe (DNS)",
        domain="Turbulence Avancée",
        subdomain="Méthodes de simulation de la turbulence",
        equation="Résolution complète de toutes les échelles jusqu'à l'échelle de Kolmogorov eta",
        latex_equation=r"\eta = \left(\frac{\nu^3}{\varepsilon}\right)^{1/4}, \quad N_{\text{grid}} \sim Re^{9/4}",
        variables={"eta": "Échelle de Kolmogorov (mm)", "nu": "Viscosité cinématique (1.5e-5 m²/s)", "Re": "Nombre de Reynolds"},
        units={"eta": "mm"},
        description="Résolution exacte des équations de Navier-Stokes sans aucune modélisation de turbulence, résolvant du mètre jusqu'à la dissipation millimétrique.",
        application_conditions=["Études théoriques fondamentales à faible nombre de Reynolds"],
        limitations=["Inapplicable aux applications météo réelles (Re > 10^8)"],
        references=["Moin & Mahesh (1998) Annu. Rev. Fluid Mech."],
    ),
    EncyclopediaEntry(
        key="rans_reynolds_averaged_navier_stokes",
        name="Modélisation RANS (Reynolds-Averaged Navier-Stokes)",
        domain="Turbulence Avancée",
        subdomain="Méthodes de simulation de la turbulence",
        equation="Moyennage statistique d'ensemble: u_i = <u_i> + u_i'",
        latex_equation=r"\frac{\partial \bar{u}_i}{\partial t} + \bar{u}_j \frac{\partial \bar{u}_i}{\partial x_j} = -\frac{1}{\rho}\frac{\partial \bar{p}}{\partial x_i} + \nu \nabla^2 \bar{u}_i - \frac{\partial \overline{u_i^\prime u_j^\prime}}{\partial x_j}",
        variables={"u_prime": "Fluctuations turbulentes", "Reynolds_stress": "-rho * <u_i' u_j'>"},
        units={"u": "m/s"},
        description="Approche classique utilisée dans la majorité des modèles NWP opérationnels où l'ensemble de la turbulence sous-maille est paramétré.",
        application_conditions=["Prévision numérique du temps globale et régionale"],
        limitations=["Ne résout pas les structures tourbillonnaires individuelles"],
        references=["Wilcox (1998) Turbulence Modeling for CFD", "ECMWF Physics Docs"],
    ),
    EncyclopediaEntry(
        key="aviation_edr_turbulence",
        name="Taux de Dissipation de la Turbulence Aéronautique (EDR)",
        domain="Turbulence Avancée",
        subdomain="Turbulence aviation",
        equation="EDR = epsilon^(1/3)",
        latex_equation=r"\text{EDR} = \varepsilon^{1/3} \quad [\text{m}^{2/3}\text{s}^{-1}]",
        variables={"epsilon": "Taux de dissipation de la TKE (m²/s³)"},
        units={"EDR": "m^(2/3)/s"},
        description="Standard officiel OACI (ICAO) pour quantifier l'intensité de la turbulence ressentie par les aéronefs en vol (EDR > 0.4 = Turbulence Sévère).",
        application_conditions=["Rapports d'avions en vol (PIREP) et modèles de prévision aviation"],
        limitations=["Indépendant du type d'avion (contrairement à l'accélération g)"],
        references=["ICAO Annex 3 Manual", "Sharman et al. (2014) Bull. Amer. Meteor. Soc."],
        compute_func=lambda epsilon: epsilon ** (1.0 / 3.0),
    ),
    EncyclopediaEntry(
        key="clear_air_turbulence_cat",
        name="Turbulence en Air Clair (Clear Air Turbulence - CAT)",
        domain="Turbulence Avancée",
        subdomain="Turbulence aviation",
        equation="Ellrod_Index = Vertical_Wind_Shear * Total_Deformation",
        latex_equation=r"\text{CAT}_{\text{Ellrod}} = \left|\frac{\partial \mathbf{V}}{\partial z}\right| \times \sqrt{DEF_{\text{str}}^2 + DEF_{\text{shr}}^2}",
        variables={"Shear": "Cisaillement vertical (s⁻¹)", "Deformation": "Déformation du champ de vent (s⁻¹)"},
        units={"CAT": "s⁻²"},
        description="Turbulence violente survenant en air clair en haute troposphère/stratosphère au voisinage des jet-streams sans manifestation nuageuse.",
        application_conditions=["Altitudes de croisière aviation (FL240 à FL400)"],
        limitations=["Invisible aux radars météorologiques embarqués classiques"],
        references=["Ellrod & Knapp (1992) Wea. Forecasting", "ICAO / WMO Aviation Turbulence Manual"],
        compute_func=calculate_ellrod_cat_index,
    ),
]

for entry in ENTRIES:
    EncyclopediaRegistry.register(entry)
