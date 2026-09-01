"""
Advanced Aviation Meteorology, Mountain Waves, Wake Turbulence & Runway Contamination Encyclopedia Module
"""

import math

from acf.science.encyclopedia.entry import EncyclopediaEntry
from acf.science.encyclopedia.registry import EncyclopediaRegistry

# ---------------------------------------------------------------------------
# Computational Functions for Aviation Meteorology
# ---------------------------------------------------------------------------


def calculate_mountain_wave_froude_number(wind_speed_perpendicular: float, brunt_vaisala_n: float, mountain_height_m: float) -> float:
    """
    Nombre de Froude pour les ondes de relief : Fr = U / (N*H).

    NOTE (correction): equation field is fully explicit but this entry
    had no compute_func.
    """
    denom = brunt_vaisala_n * mountain_height_m
    if denom == 0.0:
        raise ValueError("brunt_vaisala_n * mountain_height_m must not be zero.")
    return wind_speed_perpendicular / denom


def calculate_wake_vortex_initial_circulation(aircraft_mass_kg: float, g: float, air_density: float, wingspan_m: float, flight_velocity_m_s: float) -> float:
    """
    Circulation initiale des tourbillons de sillage : Gamma_0 = 4*M*g / (pi*rho*b*V), en m^2/s.

    NOTE (correction): equation field is fully explicit but this entry
    had no compute_func.
    """
    denom = math.pi * air_density * wingspan_m * flight_velocity_m_s
    if denom == 0.0:
        raise ValueError("pi * air_density * wingspan_m * flight_velocity_m_s must not be zero.")
    return (4.0 * aircraft_mass_kg * g) / denom


def calculate_density_altitude(pressure_alt_ft: float, oat_celsius: float, isa_temp_celsius: float = 15.0) -> float:
    """Calcul approximatif de l'altitude-densité (Density Altitude) en pieds."""
    return pressure_alt_ft + 120.0 * (oat_celsius - isa_temp_celsius)


def calculate_hydroplaning_speed_knots(tire_pressure_psi: float) -> float:
    """Calcul de la vitesse de déclenchement de l'aquaplanage dynamique Vp = 9 * sqrt(p_psi) en nœuds (Horonjeff)."""
    if tire_pressure_psi <= 0.0:
        return 0.0
    return 9.0 * math.sqrt(tire_pressure_psi)


# ---------------------------------------------------------------------------
# Encyclopedia Entries
# ---------------------------------------------------------------------------

ENTRIES: list[EncyclopediaEntry] = [
    EncyclopediaEntry(
        key="density_altitude_aviation",
        name="Altitude-Densité (Density Altitude)",
        domain="Météorologie Aéronautique",
        subdomain="Performances aéronefs",
        equation="DA = PA + 120 * (OAT - ISA_Temp)",
        latex_equation=r"\text{DA} = \text{PA} + 120 \times (T_{\text{reelle}} - T_{\text{ISA}})",
        variables={
            "PA": "Altitude-pression (ft)",
            "OAT": "Température extérieure réelle (°C)",
            "ISA_Temp": "Température ISA théorique à l'altitude PA",
        },
        units={"DA": "ft"},
        description="Altitude corrigée de la température à laquelle la densité de l'air est équivalente dans l'atmosphère standard ISA. Détermine la distance de décollage, le taux de montée et la puissance disponible du moteur.",
        application_conditions=["Calcul des performances d'envol sur terrains d'altitude par forte chaleur"],
        limitations=["Une altitude-densité élevée dégrade fortement les performances de décollage"],
        references=["ICAO Doc 8335", "FAA Pilot's Handbook of Aeronautical Knowledge"],
        compute_func=calculate_density_altitude,
    ),
    EncyclopediaEntry(
        key="mountain_waves_rotors",
        name="Ondes d'Obstacle et Rotors de Relief (Mountain Waves & Rotors)",
        domain="Météorologie Aéronautique",
        subdomain="Danger en vol & Relief",
        equation="Fr = U / (N * H)  (Nombre de Froude: Fr < 1 pour ondes stationnaires intenses)",
        latex_equation=r"Fr = \frac{U}{N H}, \quad N = \sqrt{\frac{g}{\theta}\frac{\partial \theta}{\partial z}}",
        variables={
            "U": "Vitesse du vent perpendiculaire au relief",
            "N": "Fréquence de Brunt-Väisälä",
            "H": "Hauteur de la chaîne de montagnes",
        },
        units={"Fr": "dimensionless"},
        description="Ondulations stationnaires de gravité générées sous le vent d'un relief perpendiculaire à un vent fort (> 20 kts) stable, accompagnées sous les crêtes de rotors à turbulence extrême et de rabattants violents.",
        application_conditions=["Reliefs montagneux (Alpes, Pyrénées, Rockies) par vent fort perpendiculaire"],
        limitations=["Zone de rotors extrêmement dangereuse avec perte de contrôle de l'appareil possible"],
        references=["ICAO Doc 9817 Wind Shear", "AMS Aviation Meteorology"],
        compute_func=calculate_mountain_wave_froude_number,
    ),
    EncyclopediaEntry(
        key="wake_turbulence_decay",
        name="Turbulence de Sillage et Dissipation des Tourbillons Marginales (Wake Turbulence)",
        domain="Météorologie Aéronautique",
        subdomain="Sécurité des vols",
        equation="Gamma_0 = (4 * M * g) / (pi * rho * b * V_fly)",
        latex_equation=r"\Gamma_0 = \frac{4 M g}{\pi \rho b V}",
        variables={
            "M": "Masse de l'aéronef (kg)",
            "b": "Envergure des ailes (m)",
            "V": "Vitesse de vol",
            "Gamma0": "Circulation initiale des tourbillons de saumon",
        },
        units={"Gamma": "m²/s"},
        description="Paire de tourbillons marginales contrarotatifs d'une grande violence générés par la portance des ailes des gros porteurs (Heavy / Super A380), descendant sous la trajectoire de vol.",
        application_conditions=["Procédures de séparation au décollage et à l'atterrissage aux aéroports"],
        limitations=["La dissipation est plus lente en atmosphère calme/stable à faible vent traversier"],
        references=["ICAO Doc 4444 PANS-ATM", "FAA Advisory Circular AC 90-23F"],
        compute_func=calculate_wake_vortex_initial_circulation,
    ),
    EncyclopediaEntry(
        key="runway_contamination_hydroplaning",
        name="Contamination de Piste et Aquaplanage Dynamique",
        domain="Météorologie Aéronautique",
        subdomain="Sécurité au sol & Pistes",
        equation="V_p = 9 * sqrt(p_psi)  (Nœuds)",
        latex_equation=r"V_p = 9 \sqrt{p_{\text{psi}}} \quad (\text{kts})",
        variables={"Vp": "Vitesse seuil d'aquaplanage (nœuds)", "p_psi": "Pression de gonflage des pneumatiques (psi)"},
        units={"Vp": "knots"},
        description="Phénomène physique où la pellicule d'eau, de neige fondante ou de verglas sur la piste empêche tout contact direct entre le pneumatique et l'enrobé, entraînant la perte totale du freinage et de la direction.",
        application_conditions=["Décollage et atterrissage sur piste mouillée, inondée ou contaminée par la neige"],
        limitations=["Formule d'Horonjeff valide pour l'aquaplanage dynamique pur"],
        references=["ICAO Global Reporting Format (GRF)", "Horonjeff (2010) Airport Engineering"],
        compute_func=calculate_hydroplaning_speed_knots,
    ),
]

for entry in ENTRIES:
    EncyclopediaRegistry.register(entry)
