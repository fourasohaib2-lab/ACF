"""
Atmospheric Complexity Framework (ACF)

Weather Radar Principles, Products, Doppler & Dual Polarization Encyclopedia Module
"""

import math
from typing import List
from acf.science.encyclopedia.entry import EncyclopediaEntry
from acf.science.encyclopedia.registry import EncyclopediaRegistry

# ---------------------------------------------------------------------------
# Computational Functions for Weather Radar
# ---------------------------------------------------------------------------

def calculate_radar_reflectivity_z(r_mm_h: float, a: float = 200.0, b: float = 1.6) -> float:
    """Calcul de la réflectivité Z (mm^6/m^3) à partir du taux de pluie R (mm/h) via Z = a * R^b."""
    if r_mm_h <= 0.0:
        return 0.0
    return a * (r_mm_h ** b)


def calculate_rain_rate_from_z(z_dbz: float, a: float = 200.0, b: float = 1.6) -> float:
    """Calcul de l'intensité de précipitation R (mm/h) à partir de la réflectivité en dBZ via R = (Z / a)^(1/b)."""
    z_linear = 10.0 ** (z_dbz / 10.0)
    return (z_linear / a) ** (1.0 / b)


def calculate_doppler_radial_velocity(v_wind: float, wind_dir_deg: float, radar_azimuth_deg: float, elevation_deg: float = 0.0) -> float:
    """Calcul de la vitesse radiale Doppler mesurée par le radar (m/s)."""
    rad_wind = math.radians(wind_dir_deg)
    rad_az = math.radians(radar_azimuth_deg)
    rad_el = math.radians(elevation_deg)
    return v_wind * math.cos(rad_el) * math.cos(rad_wind - rad_az)


# ---------------------------------------------------------------------------
# Encyclopedia Entries
# ---------------------------------------------------------------------------

ENTRIES: List[EncyclopediaEntry] = [
    EncyclopediaEntry(
        key="radar_reflectivity_z_r_relation",
        name="Équation Radar & Relation Z-R de Marshall-Palmer",
        domain="Radar Météorologique",
        subdomain="Équation fondamentale du radar",
        equation="Z = a * R^b  (Marshall-Palmer: Z = 200 * R^1.6)",
        latex_equation=r"Z = \int N(D) D^6 dD = a R^b \quad \implies \text{dBZ} = 10 \log_{10}(Z)",
        variables={"Z": "Réflectivité linéaire (mm⁶/m³)", "R": "Intensité de pluie (mm/h)", "a": "Facteur empirique (200 pour pluie stratiforme)", "b": "Exposant (1.6)"},
        units={"Z": "mm⁶/m³", "dBZ": "dBZ", "R": "mm/h"},
        description="Relation empirique reliant la réflectivité radar équivalente Z au taux de précipitation R au sol en fonction de la distribution des tailles de gouttes.",
        application_conditions=["Estimation des précipitations par radar monopolarisé (QPE)"],
        limitations=["Dépendance du type de précipitation (pluie stratiforme vs convective, neige, grêle)"],
        references=["Marshall & Palmer (1948) J. Meteor.", "WMO Radar Meteorology Guide", "DWD / Météo-France Radar Manuals"],
        compute_func=calculate_radar_reflectivity_z,
    ),
    EncyclopediaEntry(
        key="ppi_radar_product",
        name="Plan Position Indicator (PPI)",
        domain="Radar Météorologique",
        subdomain="Produits radar",
        equation="Balayage azimutal à angle d'élévation fixe alpha",
        latex_equation=r"\text{PPI}_\alpha(r, \theta) = Z(r \cos\alpha, \theta, r \sin\alpha)",
        variables={"r": "Distance au radar (km)", "theta": "Azimut (°)", "alpha": "Angle d'élévation (°)"},
        units={"Z": "dBZ"},
        description="Représentation polaire standard d'un balayage conique à élévation constante au-dessus de l'horizon.",
        application_conditions=["Surveillance météo en temps réel et détection des cellules orageuses"],
        limitations=["Le faisceau radar s'élève avec la distance en raison de la courbure terrestre"],
        references=["WMO-No. 8", "DWD / NOAA Radar Documentation"],
    ),
    EncyclopediaEntry(
        key="cappi_radar_product",
        name="Plan de Réflectivité à Altitude Constante (CAPPI)",
        domain="Radar Météorologique",
        subdomain="Produits radar",
        equation="CAPPI(x, y, z0) = Interpolation des balayages PPI multi-élévations à l'altitude z0",
        latex_equation=r"\text{CAPPI}(x,y,z_0) = \mathcal{I}\left(\{\text{PPI}_{\alpha_k}(r,\theta)\}\right)",
        variables={"z0": "Altitude de la coupe horizontale choisie (ex: 2000m)"},
        units={"Z": "dBZ"},
        description="Produit radar représentant une coupe horizontale continue à altitude constante, éliminant les variations d'altitude liées au faisceau conique.",
        application_conditions=["Cartographie synthétique de précipitation et réseaux multi-radars"],
        limitations=["Zone aveugle (cône de silence) directement au-dessus du radar"],
        references=["Langleben & Gaherty (1957)", "WMO Radar Guide", "Météo-France ARAMIS"],
    ),
    EncyclopediaEntry(
        key="vad_velocity_azimuth_display",
        name="Velocity Azimuth Display (VAD)",
        domain="Radar Météorologique",
        subdomain="Traitement Doppler",
        equation="V_r(theta) = U * cos(theta) + V * sin(theta) + W * sin(alpha)",
        latex_equation=r"V_r(\theta) = a_0 + a_1 \cos\theta + b_1 \sin\theta",
        variables={"a1, b1": "Coefficients de Fourier déterminant le vent moyen u et v à une altitude donnée"},
        units={"Vent": "m/s"},
        description="Technique d'analyse harmonique du champ de vitesse radiale Doppler mesuré sur un cercle à élévation fixe pour restituer le profil vertical du vent (VAD Wind Profile).",
        application_conditions=["Atmosphère homogène à l'échelle du cercle de balayage"],
        limitations=["Sensible aux mouvements d'écho non atmosphériques (oiseaux, insectes, chantiers)"],
        references=["Browning & Wexler (1968) J. Appl. Meteor.", "NOAA NEXRAD Technical Note"],
    ),
    EncyclopediaEntry(
        key="qpe_quantitative_precipitation_estimation",
        name="Estimation Quantitative des Précipitations (QPE)",
        domain="Radar Météorologique",
        subdomain="Hydrométéorologie",
        equation="R_accumulated = sum_t R(Z, ZDR, KDP) * dt",
        latex_equation=r"\text{QPE} = \int_{0}^{T} R(Z, Z_{\text{DR}}, K_{\text{DP}}) \, dt",
        variables={"R": "Taux instantané (mm/h)", "T": "Durée d'accumulation (1h, 24h)"},
        units={"QPE": "mm"},
        description="Combinaison d'estimations radar et de données pluviométriques au sol pour produire des cartes d'accumulation de précipitation haute résolution pour l'hydrologie.",
        application_conditions=["Prévention des crues éclairs et gestion des bassins versants"],
        limitations=["Incertitudes liées au masquage du relief et aux échos parasitaires (clutter)"],
        references=["WMO Hydrological Radar Manual", "NOAA MRMS QPE", "Météo-France PANTHERE"],
        compute_func=calculate_rain_rate_from_z,
    ),
    EncyclopediaEntry(
        key="doppler_velocity_dealiasing",
        name="Vitesse Radiale Doppler & Désambiguïsation (Dealiasing)",
        domain="Radar Météorologique",
        subdomain="Traitement Doppler",
        equation="V_max (Nyquist) = lambda * PRF / 4",
        latex_equation=r"V_{\text{Nyquist}} = \frac{\lambda \cdot \text{PRF}}{4}, \quad V_{\text{vrai}} = V_{\text{mesuré}} \pm 2 k V_{\text{Nyquist}}",
        variables={"PRF": "Fréquence de répétition des impulsions (Hz)", "lambda": "Longueur d'onde radar (m)"},
        units={"V_Nyquist": "m/s"},
        description="Mesure de la vitesse de déplacement des hydrométéores le long du faisceau radar via l'effet Doppler, nécessitant un traitement de désambiguïsation lorsque la vitesse dépasse la vitesse de Nyquist.",
        application_conditions=["Détection des rotation mésocycloniques et des fronts de rafales"],
        limitations=["Dilemme de Nyquist (compromis portée maximale vs vitesse maximale)"],
        references=["Doviak & Zrnic (1993) Doppler Radar and Weather Observations"],
        compute_func=calculate_doppler_radial_velocity,
    ),
    EncyclopediaEntry(
        key="dual_polarization_radar",
        name="Radar à Double Polarisation (ZDR, KDP, RhoHV)",
        domain="Radar Météorologique",
        subdomain="Polarmétrie radar",
        equation="ZDR = 10 log(Zh / Zv),  KDP = d(PhiDP)/dr,  RhoHV = Cross-correlation",
        latex_equation=r"Z_{\text{DR}} = 10 \log_{10}\left(\frac{Z_H}{Z_V}\right), \quad K_{\text{DP}} = \frac{1}{2}\frac{\partial \Phi_{\text{DP}}}{\partial r}, \quad \rho_{hv} = \frac{|\langle S_{hh} S_{vv}^*\rangle|}{\sqrt{\langle |S_{hh}|^2\rangle \langle |S_{vv}|^2\rangle}}",
        variables={"ZDR": "Réflectivité différentielle", "KDP": "Phase spécifique différentielle (°/km)", "RhoHV": "Coefficient de corrélation croisée"},
        units={"ZDR": "dB", "KDP": "°/km", "RhoHV": "dimensionless (0 à 1)"},
        description="Émission et réception simultanées d'impulsions à polarisation horizontale et verticale permettant d'identifier la forme, la nature et le type d'hydrométéores (pluie, neige, grêle, insecte).",
        application_conditions=["Classification automatique des hydrométéores (Hydrometeor Classification Algorithm - HCA)"],
        limitations=["Nécessite des calibrations matérielles extrêmement rigoureuses"],
        references=["Bringi & Chandrasekar (2001) Polarimetric Radar Meteorology", "NOAA / DWD / Météo-France Dual-Pol Manuals"],
    ),
]

for entry in ENTRIES:
    EncyclopediaRegistry.register(entry)
