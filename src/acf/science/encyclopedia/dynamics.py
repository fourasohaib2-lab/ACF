"""
Atmospheric Dynamics Encyclopedia Domain
"""

import math
from acf.science.encyclopedia.entry import EncyclopediaEntry
from acf.science.encyclopedia.registry import EncyclopediaRegistry

ENTRIES = [
    EncyclopediaEntry(
        key="coriolis_parameter",
        name="Paramètre de Coriolis",
        domain="Dynamique Atmosphérique",
        equation="f = 2 * Omega * sin(latitude)",
        latex_equation=r"f = 2\Omega \sin\phi",
        variables={"Omega": "Vitesse d'angle terrestre (7.292115e-5 rad/s)", "latitude": "Latitude en radians"},
        units={"f": "s⁻¹"},
        description="Fréquence de rotation apparente due à la rotation de la Terre déviant les mouvements fluides.",
        application_conditions=["Repère tournant terrestre"],
        limitations=["Nul à l'équateur (latitude = 0)"],
        references=["WMO Atmospheric Dynamics Manual", "Holton & Hakim (2012)"],
        compute_func=lambda latitude_deg, omega=7.292115e-5: 2.0 * omega * math.sin(math.radians(latitude_deg)),
    ),
    EncyclopediaEntry(
        key="rossby_waves_speed",
        name="Vitesse de Phase des Ondes de Rossby",
        domain="Dynamique Atmosphérique",
        equation="c = U - beta / (k^2 + l^2)",
        latex_equation=r"c = U - \frac{\beta}{k^2 + l^2}",
        variables={"U": "Vent moyen zonal", "beta": "df/dy", "k, l": "Nombres d'ondes horizontaux"},
        units={"c": "m/s"},
        description="Ondes planétaires de grand échelle ondulant le long du jet-stream sous l'effet de la variation de f avec la latitude (effet beta).",
        application_conditions=["Ondes synoptiques quasi-géostrophiques"],
        limitations=["Modèle barotrope bicolonne simplifiée"],
        references=["Rossby (1939)", "Holton & Hakim (2012)"],
    ),
]

for entry in ENTRIES:
    EncyclopediaRegistry.register(entry)
