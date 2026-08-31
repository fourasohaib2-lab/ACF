"""
Atmospheric Complexity Framework (ACF)

Severe Weather, Storm Kinematics, Hail & Severe Local Storms Encyclopedia Module
"""

from acf.science.encyclopedia.entry import EncyclopediaEntry
from acf.science.encyclopedia.registry import EncyclopediaRegistry

# ---------------------------------------------------------------------------
# Computational Functions for Severe Weather & Kinematics
# ---------------------------------------------------------------------------


def calculate_storm_relative_helicity(
    u_profile: list[float], v_profile: list[float], storm_u: float, storm_v: float, dz: float = 100.0
) -> float:
    """Calcul de l'Hélicité Relative à l'Orage (SRH) en m²/s²."""
    srh = 0.0
    n = min(len(u_profile), len(v_profile))
    for i in range(n - 1):
        du = u_profile[i + 1] - u_profile[i]
        dv = v_profile[i + 1] - v_profile[i]
        u_mean = 0.5 * (u_profile[i] + u_profile[i + 1]) - storm_u
        v_mean = 0.5 * (v_profile[i] + v_profile[i + 1]) - storm_v
        srh += (u_mean * dv) - (v_mean * du)
    return float(srh)


def estimate_hail_size_mesh(mesh_mm: float) -> str:
    """
    Classe un indice MESH (Maximum Expected Size of Hail, en mm) déjà connu
    en catégorie qualitative de sévérité de la grêle.

    NOTE (correction): this used to be wired as the "hail_size_estimation_mesh"
    entry's compute_func while that entry's own documented equation is
    "MESH = 2.54 * (SHI)^0.5" - deriving MESH FROM the Severe Hail Index
    (SHI). This function does something entirely different: it takes an
    ALREADY-KNOWN MESH value (mm) and returns a size-category description
    string - it never computes MESH from SHI at all, and doesn't even
    accept an `shi` parameter. Earlier this session (Étape 3 audit), the
    Witt et al. (1998) MESH-from-SHI formula's coefficients were
    investigated and found unverifiable against primary sources after
    multiple search attempts (same finding as the related MEHS/POH
    indices, left correctly unimplemented rather than guessed) - so this
    was NOT "fixed" by implementing an unverified SHI-based formula.
    Instead, the entry's documentation now honestly describes what this
    function actually does (classify a known MESH value), and no longer
    claims to compute MESH from SHI.
    """
    if mesh_mm < 20.0:
        return "Pas de risque majeur de grêle au sol (< 2 cm)"
    elif mesh_mm < 40.0:
        return "Grêlons de taille moyenne (2 à 4 cm - taille de balle de ping-pong)"
    elif mesh_mm < 70.0:
        return "Grosse grêle sévère (4 à 7 cm - taille de balle de tennis)"
    else:
        return "Très grosse grêle géante (> 7 cm - taille de balle de pamplemousse)"


# ---------------------------------------------------------------------------
# Encyclopedia Entries
# ---------------------------------------------------------------------------

ENTRIES: list[EncyclopediaEntry] = [
    EncyclopediaEntry(
        key="storm_relative_helicity_srh",
        name="Hélicité Relative à l'Orage (SRH)",
        domain="Phénomènes Violents & Grêle",
        subdomain="Cinématique des orages",
        equation="SRH = - int (V - c) x (dV/dz) dz",
        latex_equation=r"\text{SRH} = -\int_{0}^{z} (\mathbf{V} - \mathbf{c}) \cdot \boldsymbol{\omega}_h \, dz = \int_{0}^{z} \left[(u - c_u)\frac{\partial v}{\partial z} - (v - c_v)\frac{\partial u}{\partial z}\right] dz",
        variables={
            "V": "Profil du vent environnemental (m/s)",
            "c": "Vecteur déplacement de l'orage (m/s)",
            "omega_h": "Vorticité horizontale (s⁻¹)",
        },
        units={"SRH": "m²/s²"},
        description="Mesure du potentiel de rotation du courant ascendant d'un orage alimenté par le cisaillement du vent en basse couche (0-1 km ou 0-3 km). SRH > 150 m²/s² indique un risque supercellulaire.",
        application_conditions=["Prévision des supercellules et des tornades"],
        limitations=["Sensible à la précision du vecteur de mouvement de l'orage (méthode Bunkers)"],
        references=["Davies-Jones et al. (1990)", "Bunkers et al. (2000) Wea. Forecasting", "NOAA SPC Manual"],
        compute_func=calculate_storm_relative_helicity,
    ),
    EncyclopediaEntry(
        key="hail_growth_model",
        name="Modèle de Croissance de la Grêle (Dry & Wet Growth)",
        domain="Phénomènes Violents & Grêle",
        subdomain="Physique de la grêle",
        equation="dM_h/dt = pi * R^2 * E_h * (V_h - v_c) * LWC",
        latex_equation=r"\frac{dM_h}{dt} = \pi R^2 E_{\text{cap}} |V_h - w| \text{LWC}, \quad T_{\text{surface}} = T_0 \implies \text{Régime humide}",
        variables={
            "R": "Rayon du grêlon (m)",
            "LWC": "Liquid Water Content surfondue (kg/m³)",
            "Vh": "Vitesse de chute (m/s)",
        },
        units={"dM_h/dt": "kg/s"},
        description="Physique de la croissance de la grêle en régime sec (Dry growth: congélation immédiate formant de la glace opaque) ou humide (Wet growth: chaleur latente faisant monter T surface à 0°C formant de la glace transparente).",
        application_conditions=["Zone de fort courant ascendant (w > 20 m/s) entre 0°C et -40°C"],
        limitations=["Requis un temps de résidence prolongé dans le courant ascendant"],
        references=["Pruppacher & Klett (1997)", "Nelson (1983) J. Atmos. Sci.", "AMS Hail Physics"],
    ),
    EncyclopediaEntry(
        # NOTE (correction): this entry's compute_func used to be
        # estimate_hail_size_mesh() while the documented equation was
        # "MESH = 2.54 * (SHI)^0.5" (deriving MESH from the Severe Hail
        # Index SHI) - but that function never computes MESH from SHI at
        # all; it classifies an ALREADY-KNOWN MESH value (mm) into a
        # size-category string, and doesn't even accept an `shi`
        # parameter. The SHI-to-MESH formula's coefficients were
        # investigated this session and found unverifiable against
        # primary sources (same finding as the related MEHS/POH indices,
        # correctly left unimplemented rather than guessed). The equation/
        # variables/units below now honestly document the classification
        # step this compute_func actually performs, instead of a formula
        # it never implemented.
        key="hail_size_estimation_mesh",
        name="Estimation de la Taille de la Grêle (MESH Index)",
        domain="Phénomènes Violents & Grêle",
        subdomain="Algorithmes radar & sévérité",
        equation="Catégorie de sévérité = f(MESH_mm), pour un MESH déjà calculé en amont (radar 3D)",
        latex_equation=r"\text{Categorie}(\text{MESH}) : \text{MESH} < 20\to\text{Faible}, <40\to\text{Moyen}, <70\to\text{Sévère}, \ge 70\to\text{Géant} \quad [\text{mm}]",
        variables={"mesh_mm": "Indice MESH déjà calculé (mm) - la dérivation MESH=2.54*(SHI)^0.5 n'est PAS implémentée ici (coefficients non vérifiables)"},
        units={"mesh_mm": "mm", "return": "catégorie qualitative (str)"},
        description="Classification qualitative d'un indice MESH (Maximum Expected Size of Hail) déjà calculé par un algorithme radar 3D externe (ex: NSSL MRMS, Météo-France MESH), en catégorie de sévérité de grêle au sol.",
        application_conditions=["Traitements de réflectivité radar 3D (NSSL MRMS, Météo-France MESH)"],
        limitations=[
            "Effets de fonte sous la base du nuage",
            "Ne calcule PAS le MESH lui-même à partir du SHI - la formule de Witt et al. (1998) n'a pas pu être vérifiée avec confiance contre une source primaire ; prend un MESH déjà calculé en entrée",
        ],
        references=["Witt et al. (1998) Wea. Forecasting", "NSSL MRMS Technical Documentation"],
        compute_func=estimate_hail_size_mesh,
    ),
    EncyclopediaEntry(
        key="supercell_thunderstorm",
        name="Supercellule Convective (Supercell)",
        domain="Phénomènes Violents & Grêle",
        subdomain="Structure orageuse",
        equation="Courant ascendant rotatif (Mésocyclone): zeta > 10^-2 s^-1",
        latex_equation=r"\zeta_z = \frac{\partial v}{\partial x} - \frac{\partial u}{\partial y} \ge 10^{-2} \text{ s}^{-1} \quad (\text{Mésocyclone profond})",
        variables={"zeta_z": "Vorticité verticale du mésocyclone (s⁻¹)"},
        units={"Vorticité": "s⁻¹"},
        description="Type le plus dangereux d'orage convectif caractérisé par un courant ascendant en rotation continue (mésocyclone). Générateur de tornades majeures, très grosse grêle et rafales destructrices.",
        application_conditions=["Cisaillement profond élevé (Deep Shear 0-6km > 20 m/s) et fort CAPE"],
        limitations=["Classification en Supercellule Classique, LP (Low Precipitation) et HP (High Precipitation)"],
        references=["Browning (1964)", "Doswell & Burgess (1993) AMS Monograph", "NOAA SPC"],
    ),
    EncyclopediaEntry(
        key="tornado_vortex_dynamics",
        name="Tornade & Dynamique de Vorticité (Tornado)",
        domain="Phénomènes Violents & Grêle",
        subdomain="Phénomènes tornadiques",
        equation="Conservation du moment cinétique: v_theta * r = Constante",
        latex_equation=r"v_\theta r = \text{Cte} \implies v_\theta \propto \frac{1}{r}, \quad p(r) - p_\infty = -\rho \int_r^\infty \frac{v_\theta^2}{r^\prime} dr^\prime",
        variables={
            "v_theta": "Vitesse tangentielles des vents (m/s)",
            "r": "Rayon du cœur du vortex (m)",
            "p": "Dépression centrale (hPa)",
        },
        units={"Vent": "m/s", "Pression": "hPa"},
        description="Vortex atmosphérique extrêmement intense s'étendant de la base d'un nuage convectif jusqu'au sol. Vents pouvant dépasser 100 m/s (360 km/h) classés sur l'échelle Enhanced Fujita (EF0 à EF5).",
        application_conditions=[
            "Mésocyclone de basse couche ou étirement de vorticité sur une frontière de méso-échelle"
        ],
        limitations=["Échelle spatiale fine (quelques dizaines à centaines de mètres)"],
        references=["Davies-Jones (2015) Atmos. Res.", "Enhanced Fujita Scale (NOAA / NWS)"],
    ),
    EncyclopediaEntry(
        key="bow_echo_structure",
        name="Écho en Arc (Bow Echo)",
        domain="Phénomènes Violents & Grêle",
        subdomain="Systèmes Convectifs de Méso-échelle",
        equation="Rear Inflow Jet (RIJ) s'enfonçant dans la ligne de grain",
        latex_equation=r"\mathbf{V}_{\text{RIJ}} \cdot \mathbf{n} > V_{\text{system}} + 15 \text{ m/s}",
        variables={"RIJ": "Courant de jet entrant par l'arrière (Rear Inflow Jet)"},
        units={"Vitesse": "m/s"},
        description="Signature radar en forme d'arc caractérisant une ligne d'orages poussée par un jet d'air sec et froid à l'arrière, provoquant des rafales de vent dévastatrices au sol.",
        application_conditions=["Forte instabilité et fort cisaillement en moyenne troposphère"],
        limitations=["Évolution possible vers un complexe convectif en virgule (comma head)"],
        references=["Fujita (1978)", "Weisman (1993) J. Atmos. Sci.", "AMS Bow Echo Guide"],
    ),
    EncyclopediaEntry(
        key="derecho_windstorm",
        name="Derecho (Système Convectif de Rafales Dévastatrices)",
        domain="Phénomènes Violents & Grêle",
        subdomain="Systèmes Convectifs de Méso-échelle (MCS)",
        equation="Couloir de rafales > 26 m/s (50 kt) sur une longueur > 400 km",
        latex_equation=r"\text{Longueur} \ge 400 \text{ km}, \quad V_{\text{rafale}} \ge 26 \text{ m/s} \quad (50 \text{ kt})",
        variables={"Longueur": "Longueur du couloir de dégâts (> 400 km)", "Vitesse": "Vitesse des rafales (> 26 m/s)"},
        units={"Longueur": "km", "Vitesse": "m/s"},
        description="Événement rare et généralisé de rafales convectives très denses et dévastatrices généré par une succession d'échos en arc à déplacement rapide.",
        application_conditions=["Environnements très instables à fort CAPE et fort flux de moyenne troposphère"],
        limitations=["Persistance sur plusieurs heures requise"],
        references=["Johns & Hirt (1987) Wea. Forecasting", "Corfidi et al. (2016) NOAA SPC"],
    ),
    EncyclopediaEntry(
        key="microburst_downburst",
        name="Microrafale et Rafale Descendante (Microburst & Downburst)",
        domain="Phénomènes Violents & Grêle",
        subdomain="Sécurité aéronautique & vents",
        equation="Microburst: Diamètre < 4 km, V_rafale > 25 m/s, durée < 15 min",
        latex_equation=r"\text{Diameter} < 4 \text{ km}, \quad \Delta V_{\text{horizontal}} > 25 \text{ m/s} \quad (50 \text{ kt})",
        variables={"Diamètre": "< 4 km", "Vitesse_rafale": "> 25 m/s"},
        units={"Diamètre": "km", "Vitesse": "m/s"},
        description="Courant descendant extrêmement concentré et violent touchant le sol et s'étalant latéralement. Représente un danger mortel pour les avions en phase d'atterrissage/décollage.",
        application_conditions=["Microbursts sec (air sec sous la base) ou humide (fortes précipitations)"],
        limitations=["Phénomène très bref (5-15 min) et localisé"],
        references=["Fujita (1985) The Downburst", "ICAO Windshear Manual", "WMO Aviation Guide"],
    ),
]

for entry in ENTRIES:
    EncyclopediaRegistry.register(entry)
