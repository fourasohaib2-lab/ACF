"""
Meteorological Radar Encyclopedia Domain
"""

from acf.science.encyclopedia.entry import EncyclopediaEntry
from acf.science.encyclopedia.registry import EncyclopediaRegistry

_SPEED_OF_LIGHT_M_S = 2.99792458e8


def calculate_doppler_radial_velocity(doppler_shift_hz: float, transmit_frequency_hz: float) -> float:
    """
    Vitesse radiale Doppler : Vr = (fd*c) / (2*f0), en m/s.

    NOTE (correction): equation field is fully explicit but this entry
    had no compute_func.
    """
    if transmit_frequency_hz == 0.0:
        raise ValueError("transmit_frequency_hz must not be zero.")
    return (doppler_shift_hz * _SPEED_OF_LIGHT_M_S) / (2.0 * transmit_frequency_hz)


ENTRIES = [
    EncyclopediaEntry(
        key="radar_marshall_palmer_zr",
        name="Équation Z-R de Marshall-Palmer",
        domain="Radar Météorologique",
        subdomain="Estimation des précipitations (QPE)",
        equation="Z = a * R^b (Standard: Z = 200 * R^1.6)",
        latex_equation=r"Z = 200 R^{1.6}",
        variables={"Z": "Réflectivité radar (mm⁶/m³)", "R": "Intensité de pluie (mm/h)"},
        units={"Z": "mm⁶/m³", "R": "mm/h"},
        description="Relation empirique reliant la réflectivité radar convertie en dBZ à l'intensité horaire de la pluie au sol.",
        application_conditions=["Pluie stratiforme à gouttelettes moyennes"],
        limitations=["Déviation en cas de grêle (sous-estimation/sur-estimation) ou de neige"],
        references=["Marshall & Palmer (1948) J. Meteor.", "WMO Radar Meteorology Guide"],
        compute_func=lambda reflectivity_dbz, a=200.0, b=1.6: ((10.0 ** (reflectivity_dbz / 10.0)) / a) ** (1.0 / b),
    ),
    EncyclopediaEntry(
        key="doppler_radial_velocity",
        name="Vitesse Radiale Doppler",
        domain="Radar Météorologique",
        subdomain="Radar Doppler",
        equation="V_r = (fd * c) / (2 * f0)",
        latex_equation=r"V_r = \frac{f_d c}{2 f_0}",
        variables={
            "fd": "Décalage de fréquence Doppler",
            "f0": "Fréquence d'émission radar",
            "c": "Vitesse de la lumière",
        },
        units={"Vr": "m/s", "fd": "Hz"},
        description="Vitesse du vent et des précipitations projetée le long de l'axe du faisceau radar (détection des mésocyclones et microrafales).",
        application_conditions=["Cibles mobiles (gouttes de pluie, glace, insectes)"],
        limitations=["Mesure uniquement la composante radiale de vitesse"],
        references=["Doviak & Zrnic (1993) Doppler Radar and Weather Observations"],
        compute_func=calculate_doppler_radial_velocity,
    ),
]

for entry in ENTRIES:
    EncyclopediaRegistry.register(entry)
