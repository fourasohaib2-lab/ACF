"""
Ocean-Atmosphere Coupled Dynamics Encyclopedia Module
"""

from acf.science.encyclopedia.entry import EncyclopediaEntry
from acf.science.encyclopedia.registry import EncyclopediaRegistry

ENTRIES = [
    EncyclopediaEntry(
        key="sensible_heat_flux_bulk",
        name="Flux de Chaleur Sensible Océan-Atmosphère",
        domain="Océan-Atmosphère",
        subdomain="Échanges de surface",
        equation="H = rho * cp * Ch * U * (Ts - Ta)",
        latex_equation=r"H = \rho c_p C_h U_10 (T_s - T_a)",
        variables={"rho": "Masse volumique de l'air (1.2 kg/m³)", "cp": "1004 J/(kg·K)", "Ch": "1.1e-3", "U10": "Vent à 10m", "Ts": "SST (K)", "Ta": "Température de l'air (K)"},
        units={"H": "W/m²"},
        description="Transfert d'énergie thermique par conduction et convection directe entre la surface de l'eau et l'air superposé.",
        application_conditions=["Interface océan-atmosphère"],
        limitations=["Dépend de la stabilité thermique de la couche limite de surface (Monin-Obukhov)"],
        references=["COARE 3.0 Bulk Algorithm", "Fairall et al. (2003)"],
        compute_func=lambda rho, cp, U10, dt, Ch=1.1e-3: rho * cp * Ch * U10 * dt,
    ),
    EncyclopediaEntry(
        key="north_atlantic_oscillation_nao",
        name="Oscillation Nord-Atlantique (NAO)",
        domain="Océan-Atmosphère",
        subdomain="Variabilité climatique régionale",
        equation="NAO_index = Normalized_SLP(Açores) - Normalized_SLP(Islande)",
        latex_equation=r"\text{NAO} = \text{SLP}_{\text{Açores}}^* - \text{SLP}_{\text{Islande}}^*",
        variables={"SLP": "Pression au niveau de la mer (hPa)"},
        units={"NAO": "dimensionless"},
        description="Mode de variabilité atmosphérique majeur régissant les tempêtes et les régimes d'hiver sur l'Europe et l'Amérique du Nord.",
        application_conditions=["Atlantique Nord"],
        limitations=["Variabilité temporelle de l'action des centres d'action"],
        references=["Hurrell (1995) Science", "NOAA CPC Teleconnections"],
    ),
]

for entry in ENTRIES:
    EncyclopediaRegistry.register(entry)
