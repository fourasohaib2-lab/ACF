"""
Atmospheric Thermodynamics Encyclopedia Domain
"""

from acf.science.encyclopedia.entry import EncyclopediaEntry
from acf.science.encyclopedia.registry import EncyclopediaRegistry


def calculate_first_law_specific_heat(cp: float, dT: float, alpha: float, dp: float) -> float:
    """
    dq = cp*dT - alpha*dp, en J/kg.

    NOTE (correction): equation field is fully explicit but this entry
    had no compute_func. This is the THIRD entry in ACF with this exact
    formula (science/laws/thermodynamics.py's 'first_law_thermodynamics',
    encyclopedia/physical_laws/thermodynamics_laws.py's
    'first_law_thermodynamics_atmos') - algebraically identical,
    re-expressed locally per this file's own convention rather than
    cross-imported for a one-line formula (same treatment as
    aerodynamics/isa_atmosphere.py's Reynolds/drag entries).
    """
    return cp * dT - alpha * dp


ENTRIES = [
    EncyclopediaEntry(
        key="virtual_temperature_encyclopedia",
        name="Température Virtuelle",
        domain="Thermodynamique Atmosphérique",
        subdomain="Thermodynamique de l'air humide",
        equation="Tv = T * (1 + 0.608 * q)",
        latex_equation=r"T_v = T(1 + 0.608q)",
        variables={"T": "Température absolue (K)", "q": "Humidité spécifique (kg/kg)"},
        units={"Tv": "K", "T": "K", "q": "kg/kg"},
        description="Température théorique qu'aurait l'air sec pour avoir la même masse volumique que l'air humide à même pression.",
        application_conditions=["Air humide sous pression atmosphérique"],
        limitations=["Fractions massiques d'eau modérées"],
        references=["WMO Atmospheric Thermodynamics Guide", "ECMWF IFS Model Docs"],
        compute_func=lambda temperature, specific_humidity: temperature * (1.0 + 0.608 * specific_humidity),
    ),
    EncyclopediaEntry(
        key="potential_temperature_encyclopedia",
        name="Température Potentielle",
        domain="Thermodynamique Atmosphérique",
        subdomain="Processus adiabatiques",
        equation="theta = T * (p0 / p)**(Rd / cp)",
        latex_equation=r"\theta = T \left(\frac{p_0}{p}\right)^{\frac{R_d}{c_p}}",
        variables={"T": "Température (K)", "p": "Pression (Pa)", "p0": "100000 Pa", "Rd/cp": "0.286"},
        units={"theta": "K"},
        description="Température d'une parcelle ramenée adiabatiquement et séchement à la pression standard de 1000 hPa.",
        application_conditions=["Processus adiabatique sec"],
        limitations=["Absence de condensation de vapeur d'eau"],
        references=["Holton & Hakim (2012)"],
        compute_func=lambda temperature, pressure, p0=100000.0, kappa=0.286: temperature * (p0 / pressure) ** kappa,
    ),
    EncyclopediaEntry(
        key="first_law_thermodynamics_encyclopedia",
        name="Premier Principe de la Thermodynamique Atmosphérique",
        domain="Thermodynamique Atmosphérique",
        equation="dq = cp*dT - alpha*dp",
        latex_equation=r"dq = c_p dT - \alpha dp",
        variables={"dq": "Chaleur spécifique (J/kg)", "cp": "1004 J/(kg·K)", "alpha": "Volume massique (m³/kg)"},
        units={"dq": "J/kg"},
        description="Conservation de l'énergie thermique et mécanique pour une parcelle d'air fluide.",
        application_conditions=["Système thermodynamique fermé"],
        limitations=["Processus quasi-statique"],
        references=["Bohren & Albrecht (1998) Atmospheric Thermodynamics"],
        compute_func=calculate_first_law_specific_heat,
    ),
]

for entry in ENTRIES:
    EncyclopediaRegistry.register(entry)
