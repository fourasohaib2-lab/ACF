"""
Aeronautical Meteorology & Aerodynamics Encyclopedia Domain
"""

from acf.science.encyclopedia.entry import EncyclopediaEntry
from acf.science.encyclopedia.registry import EncyclopediaRegistry

ENTRIES = [
    EncyclopediaEntry(
        key="density_altitude_aviation",
        name="Altitude-Densité (Density Altitude)",
        domain="Aéronautique",
        subdomain="Performances de vol",
        equation="DA = PA + 120 * (OAT - ISA_Temp)",
        latex_equation=r"\text{DA} = \text{PA} + 120 (T_{\text{OAT}} - T_{\text{ISA}})",
        variables={"PA": "Pressure Altitude (ft)", "OAT": "Outside Air Temp (°C)", "ISA_Temp": "Température ISA (°C)"},
        units={"DA": "ft"},
        description="Altitude corrigée de la température à laquelle l'air a une densité équivalente dans l'Atmosphère Standard OACI.",
        application_conditions=["Calcul des longueurs de décollage et vitesses de montée"],
        limitations=["Dégradation importante des performances par fortes chaleurs à haute altitude"],
        references=["ICAO Doc 7488/3", "FAA Pilot's Handbook of Aeronautical Knowledge"],
        compute_func=lambda pressure_alt_ft, oat_c, isa_temp_c: pressure_alt_ft + 120.0 * (oat_c - isa_temp_c),
    ),
    EncyclopediaEntry(
        key="clear_air_turbulence_index",
        name="Indice de Turbulence en Air Clair (CAT Dutton Index)",
        domain="Aéronautique",
        subdomain="Sécurité aérienne",
        equation="CAT = 1.25 * S_horiz + 0.25 * S_vert^2",
        latex_equation=r"\text{CAT} = 1.25 |\nabla V_{\text{horiz}}| + 0.25 \left(\frac{\partial V}{\partial z}\right)^2",
        variables={"S_horiz": "Cisaillement horizontal (s⁻¹)", "S_vert": "Cisaillement vertical du vent (s⁻¹)"},
        units={"CAT": "s⁻¹"},
        description="Indicateur de risque de secousses violentes hors nuages associées au cisaillement du jet-stream.",
        application_conditions=["Niveaux de vol élevés (FL240 - FL450)"],
        limitations=["Turbulence à petite échelle non résolue par les grilles météo grossières"],
        references=["Dutton (1980) Meteor. Mag.", "ICAO Aviation Meteorology Manual"],
    ),
]

for entry in ENTRIES:
    EncyclopediaRegistry.register(entry)
