"""
Atmospheric Dynamics, Primitive Equations, Vorticity & Large-Scale Circulation Encyclopedia Module
"""

import math

from acf.science.cyclones import GradientWind
from acf.science.encyclopedia.entry import EncyclopediaEntry
from acf.science.encyclopedia.registry import EncyclopediaRegistry

# ---------------------------------------------------------------------------
# Computational Functions for Atmospheric Dynamics
# ---------------------------------------------------------------------------


def calculate_coriolis_parameter(latitude_deg: float, omega: float = 7.292115e-5) -> float:
    """Calcul du paramètre de Coriolis f = 2 * Omega * sin(lat) en s⁻¹."""
    return 2.0 * omega * math.sin(math.radians(latitude_deg))


def calculate_geostrophic_wind_speed(dp_dn_pa_m: float, rho: float, latitude_deg: float) -> float:
    """Calcul de la vitesse du vent géostrophique Vg = (1 / (rho * f)) * |dp/dn| en m/s."""
    f = calculate_coriolis_parameter(latitude_deg)
    if abs(f) < 1e-6 or rho <= 0.0:
        return 0.0
    return abs(dp_dn_pa_m) / (rho * abs(f))


def calculate_ertel_potential_vorticity(abs_vorticity: float, dtheta_dz: float, rho: float) -> float:
    """Calcul de la vorticité potentielle d'Ertel PV = (1 / rho) * (zeta + f) * (dtheta / dz) en PVU (1 PVU = 1e-6 K·m²/(kg·s))."""
    if rho <= 0.0:
        return 0.0
    pv_si = (1.0 / rho) * abs_vorticity * dtheta_dz
    return pv_si * 1e6  # conversion en PVU


def calculate_rossby_number(u_ms: float, length_scale_m: float, latitude_deg: float) -> float:
    """Calcul du nombre de Rossby Ro = U / (f * L)."""
    f = abs(calculate_coriolis_parameter(latitude_deg))
    if f < 1e-6 or length_scale_m <= 0.0:
        return 0.0
    return u_ms / (f * length_scale_m)


def calculate_hydrostatic_dp_dz(rho: float, g: float = 9.80665) -> float:
    """
    Équilibre hydrostatique : dp/dz = -rho*g, en Pa/m.

    NOTE (correction): equation field is fully explicit but this entry
    had no compute_func despite there being nothing left to design -
    it is literally this one line.
    """
    return -rho * g


def calculate_thermal_wind_shear_per_height(dt_dx: float, dt_dy: float, coriolis_f: float, mean_temperature_k: float) -> tuple[float, float]:
    """
    Cisaillement vertical du vent géostrophique par unité d'ALTITUDE
    (et non par ln(p) comme science/synoptic.py's ThermalWind.calculate()
    - deux formes DIFFERENTES, non interchangeables, de la même relation
    physique, selon la coordonnée verticale choisie) :

        d(Vg)/dz = (g / (f*T)) * k x grad_h(T)

    Dérivation du produit vectoriel (verifiee) : k x (dT/dx, dT/dy, 0)
    = (-dT/dy, dT/dx, 0), d'ou :
        d(ug)/dz = -(g/(f*T)) * dT/dy
        d(vg)/dz =  (g/(f*T)) * dT/dx

    Verification physique : dans l'hemisphere Nord (f>0), un gradient
    meridien de temperature decroissant vers le pole (dT/dy<0, avec y
    croissant vers le pole) donne d(ug)/dz>0, c.a.d. un cisaillement
    d'ouest croissant avec l'altitude - coherent avec l'existence des
    jets d'ouest pres de la tropopause (Holton & Hakim 2012).

    Parameters
    ----------
    dt_dx, dt_dy : float
        Gradient horizontal de température (K/m).
    coriolis_f : float
        Paramètre de Coriolis (s⁻¹), non nul.
    mean_temperature_k : float
        Température moyenne de la couche (K), > 0.

    Returns
    -------
    tuple of float
        (d(ug)/dz, d(vg)/dz) en s⁻¹.
    """
    if coriolis_f == 0.0:
        raise ValueError("coriolis_f must not be zero.")
    if mean_temperature_k <= 0.0:
        raise ValueError("mean_temperature_k must be positive.")
    factor = 9.80665 / (coriolis_f * mean_temperature_k)
    return (-factor * dt_dy, factor * dt_dx)


# ---------------------------------------------------------------------------
# Encyclopedia Entries
# ---------------------------------------------------------------------------

ENTRIES: list[EncyclopediaEntry] = [
    # --- PRIMITIVE EQUATIONS & SYSTEM FORMS ---
    EncyclopediaEntry(
        key="mass_conservation_continuity",
        name="Équation de Continuité (Conservation de la Masse)",
        domain="Dynamique Atmosphérique",
        subdomain="Équations primitives",
        equation="d(rho)/dt + div(rho * V) = 0",
        latex_equation=r"\frac{\partial \rho}{\partial t} + \nabla \cdot (\rho \mathbf{V}) = 0",
        variables={"rho": "Masse volumique de l'air (kg/m³)", "V": "Vecteur vitesse (u, v, w)"},
        units={"div": "kg/(m³·s)"},
        description="Loi de conservation de la masse garantissant qu'aucune matière n'est créée ni détruite au sein de l'écoulement atmosphérique.",
        application_conditions=["Fluides compressibles continuous"],
        limitations=["Forme modifiée pour les coordonnées masse ou sigma"],
        references=["Holton & Hakim (2012)", "WMO Atmospheric Dynamics"],
    ),
    EncyclopediaEntry(
        key="momentum_conservation_navier_stokes",
        name="Équation de Conservation de la Quantité de Mouvement (Navier-Stokes)",
        domain="Dynamique Atmosphérique",
        subdomain="Équations primitives",
        equation="DV/Dt = -1/rho * grad(p) - g*k - 2*Omega x V + F_viscous",
        latex_equation=r"\frac{D\mathbf{V}}{Dt} = -\frac{1}{\rho}\nabla p - g \mathbf{k} - 2\boldsymbol{\Omega}\times\mathbf{V} + \mathbf{F}_{\text{turb}}",
        variables={
            "V": "Vitesse du fluide",
            "p": "Pression",
            "Omega": "Vitesse angulaire de rotation terrestre",
            "F": "Force de frottement turbulent",
        },
        units={"Accélération": "m/s²"},
        description="Deuxième loi de Newton appliquée à une parcelle d'air dans le repère tournant terrestre, incorporant les forces de pression, de gravité, de Coriolis et de frottement.",
        application_conditions=["Modèles NWP non-hydrostatiques et hydrostatiques"],
        limitations=["Les termes sous-maille de frottement F_turb nécessitent une paramétrisation"],
        references=["Navier (1822)", "Stokes (1845)", "Durran (2010)"],
    ),
    EncyclopediaEntry(
        key="energy_conservation_thermodynamic",
        name="Équation de Conservation de l'Énergie",
        domain="Dynamique Atmosphérique",
        subdomain="Équations primitives",
        equation="cp * DT/Dt - 1/rho * Dp/Dt = Q_diabatic",
        latex_equation=r"c_p \frac{DT}{Dt} - \frac{1}{\rho}\frac{Dp}{Dt} = Q_{\text{rad}} + Q_{\text{lat}} + Q_{\text{diff}}",
        variables={"T": "Température (K)", "Q": "Sources de chauffage diabatique (W/kg)"},
        units={"Q": "W/kg"},
        description="Premier principe thermodynamique sous forme eulérienne/lagrangienne gouvernant les variations de température sous l'effet de la compression/détente et des chauffages diabatiques.",
        application_conditions=["Modèles NWP et simulations du climat"],
        limitations=["Incertitudes associées au calcul des schémas radiatifs et microphysiques"],
        references=["Holton & Hakim (2012)", "ECMWF Physics Docs"],
    ),
    EncyclopediaEntry(
        key="anelastic_approximation",
        name="Approximation Anélastique",
        domain="Dynamique Atmosphérique",
        subdomain="Approximations équations",
        equation="div(rho0(z) * V) = 0",
        latex_equation=r"\nabla \cdot (\rho_0(z) \mathbf{V}) = 0",
        variables={"rho0": "Profil de densité de référence neutre"},
        units={"div": "s⁻¹"},
        description="Approximation filtrant les ondes acoustiques à haute fréquence tout en conservant les variations de densité liées à l'altitude z.",
        application_conditions=["Modèles méso-échelle et modèles convectifs (Meso-NH, Cloud Resolving Models)"],
        limitations=["Non adaptée aux écoulements à très haut nombre de Mach"],
        references=["Ogura & Phillips (1962) J. Atmos. Sci.", "Durran (2010)"],
    ),
    EncyclopediaEntry(
        key="boussinesq_approximation",
        name="Approximation de Boussinesq",
        domain="Dynamique Atmosphérique",
        subdomain="Approximations équations",
        equation="rho = rho0 * (1 - alpha * (T - T0)),  div(V) = 0",
        latex_equation=r"\rho = \rho_0 \left(1 - \alpha (T - T_0)\right), \quad \nabla \cdot \mathbf{V} = 0",
        variables={"alpha": "Coefficient de dilatation thermique (1/T0)"},
        units={"rho": "kg/m³"},
        description="Approximation simplifiant la masse volumique à une constante rho0 partout sauf dans le terme de poussée d'Archimède.",
        application_conditions=["Convection thermique peu profonde et dynamique océanique"],
        limitations=["Invalide sur des couches atmosphériques de grande hauteur (> 2 km)"],
        references=["Boussinesq (1903)", "Stull (1988)"],
    ),
    # --- LARGE SCALE DYNAMICS & EQUILIBRIA ---
    EncyclopediaEntry(
        key="hydrostatic_equilibrium_law",
        name="Équilibre Hydrostatique",
        domain="Dynamique Atmosphérique",
        subdomain="Équilibres fondamentaux",
        equation="dp/dz = - rho * g",
        latex_equation=r"\frac{\partial p}{\partial z} = -\rho g",
        variables={"p": "Pression (Pa)", "z": "Altitude (m)", "g": "Gravité (9.81 m/s²)"},
        units={"dp/dz": "Pa/m"},
        description="Équilibre vertical parfait entre la force de pression dirigée vers le haut et la force de pesanteur dirigée vers le bas.",
        application_conditions=["Dynamique à grande échelle (échelles synoptiques L > 100 km)"],
        limitations=["Violé dans les zones de forts mouvements verticaux convectifs (w > 5 m/s)"],
        references=["WMO-No. 8", "Holton & Hakim (2012)"],
        compute_func=calculate_hydrostatic_dp_dz,
    ),
    EncyclopediaEntry(
        key="geostrophic_balance_wind",
        name="Équilibre Géostrophique & Vent Géostrophique",
        domain="Dynamique Atmosphérique",
        subdomain="Équilibres fondamentaux",
        equation="f * u_g = -1/rho * dp/dy,  f * v_g = 1/rho * dp/dx",
        latex_equation=r"f u_g = -\frac{1}{\rho}\frac{\partial p}{\partial y}, \quad f v_g = \frac{1}{\rho}\frac{\partial p}{\partial x} \implies \mathbf{V}_g = \frac{1}{\rho f} \mathbf{k} \times \nabla p",
        variables={"Vg": "Vent géostrophique (m/s)", "f": "Paramètre de Coriolis (s⁻¹)"},
        units={"Vg": "m/s"},
        description="Équilibre horizontal canonique entre la force du gradient de pression et la force de Coriolis aux latitudes moyennes et hautes.",
        application_conditions=["Atmosphère libre hors de la couche limite de frottement"],
        limitations=["Nul à l'équateur (f -> 0) et invalide dans les zones d'isobares très courbées"],
        references=["Buys Ballot (1857)", "Holton & Hakim (2012)"],
        compute_func=calculate_geostrophic_wind_speed,
    ),
    EncyclopediaEntry(
        key="thermal_wind_relation",
        name="Vent Thermique",
        domain="Dynamique Atmosphérique",
        subdomain="Cisaillement et fronts",
        equation="d(Vg)/dz = (g / (f * T)) * k x grad_h(T)",
        latex_equation=r"\frac{\partial \mathbf{V}_g}{\partial z} = \frac{g}{f T} \mathbf{k} \times \nabla_h T",
        variables={
            "d(Vg)/dz": "Cisaillement vertical du vent géostrophique",
            "grad_h(T)": "Gradient horizontal de température",
        },
        units={"dV/dz": "s⁻¹"},
        description="Relation liant le cisaillement vertical du vent géostrophique au gradient horizontal de température. Explique l'existence des jet-streams au-dessus des zones frontales.",
        application_conditions=["Atmosphère quasi-géostrophique et fronts synoptiques"],
        limitations=["Approximation géostrophique requise"],
        references=["Holton & Hakim (2012)", "WMO Technical Manual"],
        compute_func=calculate_thermal_wind_shear_per_height,
    ),
    EncyclopediaEntry(
        key="gradient_wind_balance",
        name="Équilibre du Vent de Gradient",
        domain="Dynamique Atmosphérique",
        subdomain="Équilibres fondamentaux",
        equation="v^2 / R + f * v = - 1/rho * dp/dn",
        latex_equation=r"\frac{V^2}{R} + f V = -\frac{1}{\rho}\frac{\partial p}{\partial n}",
        variables={"R": "Rayon de courbure de la trajectoire (m)", "V": "Vitesse du vent de gradient (m/s)"},
        units={"V": "m/s"},
        description="Équilibre à trois forces (gradient de pression, Coriolis et force centrifuge) rendant compte du vent réel autour des dépressions et anticyclones à forte courbure.",
        application_conditions=["Cyclones tropicaux, dépressions creuses et anticyclones"],
        limitations=["Pas de solution réelle pour des anticyclones trop intenses à petit rayon (limite de gradient)"],
        references=["Holton & Hakim (2012)", "AMS Glossary"],
        # NOTE (correction): reuses science/cyclones.py's GradientWind.calculate()
        # directly (same exact formula, same solved quadratic root) rather than
        # reimplementing it a second time - single source of truth.
        compute_func=GradientWind.calculate,
    ),
    EncyclopediaEntry(
        key="ertel_potential_vorticity_pv",
        name="Vorticité Potentielle d'Ertel (PV)",
        domain="Dynamique Atmosphérique",
        subdomain="Diagnostics de vorticité",
        equation="PV = (1 / rho) * (omega_a) * grad(theta)",
        latex_equation=r"PV = \frac{1}{\rho} \boldsymbol{\omega}_a \cdot \nabla \theta = \frac{1}{\rho} (\zeta + f) \frac{\partial \theta}{\partial z}",
        variables={
            "PV": "Vorticité potentielle (PVU)",
            "omega_a": "Vorticité absolue",
            "theta": "Température potentielle",
        },
        units={"PV": "PVU (10⁻⁶ K·m²/(kg·s))"},
        description="Quantité scalaire fondamentale conservée pour chaque parcelle d'air lors d'un écoulement adiabatique sans frottement. Traceur parfait des anomalies de tropopause.",
        application_conditions=["Diagnostic dynamique de méso et grande échelle (Anomalies de PV)"],
        limitations=["Non conservée en présence de dégagement de chaleur latente ou de frottement turbulent"],
        references=["Ertel (1942) Meteorol. Z.", "Hoskins et al. (1985) Q. J. R. Meteorol. Soc."],
        compute_func=calculate_ertel_potential_vorticity,
    ),
    EncyclopediaEntry(
        key="rossby_number_dynamic",
        name="Nombre de Rossby (Ro)",
        domain="Dynamique Atmosphérique",
        subdomain="Nombres sans dimension",
        equation="Ro = U / (f * L)",
        latex_equation=r"Ro = \frac{U}{f L}",
        variables={
            "U": "Vitesse caractéristique (m/s)",
            "L": "Échelle spatiale (m)",
            "f": "Paramètre de Coriolis (s⁻¹)",
        },
        units={"Ro": "dimensionless"},
        description="Nombre sans dimension mesurant le rapport entre les forces d'inertie et la force de Coriolis. Ro << 1 caractérise les écoulements quasi-géostrophiques à grande échelle.",
        application_conditions=["Analyse d'échelle de la dynamique des fluides"],
        limitations=["Ro >> 1 pour la convection et les tornades où Coriolis est négligeable"],
        references=["Rossby (1939)", "Holton & Hakim (2012)"],
        compute_func=calculate_rossby_number,
    ),
    EncyclopediaEntry(
        key="jet_stream_dynamics",
        name="Jet-Streams Atmosphériques (Courants-Jets)",
        domain="Dynamique Atmosphérique",
        subdomain="Circulation générale",
        equation="Vent zonal maximal au niveau de la tropopause: V > 30 m/s (60 à 100 m/s)",
        latex_equation=r"U_{\text{jet}} \approx \frac{g}{f \bar{T}} \Delta T_{\text{équateur-pôle}}",
        variables={"Altitude": "9 à 12 km (250-300 hPa)", "Vitesse": "30 à 100 m/s"},
        units={"Vitesse": "m/s"},
        description="Tubes de vent d'Ouest extrêmement rapides situés près de la tropopause au niveau des cellules de Hadley, Ferrel et Polaire, résultant du gradient thermique méridien.",
        application_conditions=["Navigation aérienne et prévision des tempêtes synoptiques"],
        limitations=["Sujet aux ondulations d'ondes de Rossby et aux méandres de blocage"],
        references=["WMO Jet Stream Manual", "Riehl (1962) Jet Streams"],
    ),
]

for entry in ENTRIES:
    EncyclopediaRegistry.register(entry)
