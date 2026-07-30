"""
Meteorological Radar Encyclopedia Domain
"""

from acf.science.encyclopedia.entry import EncyclopediaEntry
from acf.science.encyclopedia.registry import EncyclopediaRegistry

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
        variables={"fd": "Décalage de fréquence Doppler", "f0": "Fréquence d'émission radar", "c": "Vitesse de la lumière"},
        units={"Vr": "m/s", "fd": "Hz"},
        description="Vitesse du vent et des précipitations projetée le long de l'axe du faisceau radar (détection des mésocyclones et microrafales).",
        application_conditions=["Cibles mobiles (gouttes de pluie, glace, insectes)"],
        limitations=["Mesure uniquement la composante radiale de vitesse"],
        references=["Doviak & Zrnic (1993) Doppler Radar and Weather Observations"],
    ),
]

for entry in ENTRIES:
    EncyclopediaRegistry.register(entry)
