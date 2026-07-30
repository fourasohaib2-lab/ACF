"""
Convection & Severe Convective Weather Encyclopedia Module
"""

from acf.science.encyclopedia.entry import EncyclopediaEntry
from acf.science.encyclopedia.registry import EncyclopediaRegistry

ENTRIES = [
    EncyclopediaEntry(
        key="stp_index_tornado",
        name="Significant Tornado Parameter (STP)",
        domain="Convection & Orages",
        subdomain="Paramètres orageux violents",
        equation="STP = (cape/1500)*(srh1km/150)*((2000-lcl)/1000)*(shear6km/20)",
        latex_equation=r"\text{STP} = \left(\frac{\text{CAPE}}{1500}\right) \left(\frac{\text{SRH}_{0-1}}{150}\right) \left(\frac{2000 - z_{\text{LCL}}}{1000}\right) \left(\frac{\Delta V_{0-6}}{20}\right)",
        variables={"CAPE": "J/kg", "SRH1km": "Hélicité 0-1 km (m²/s²)", "zLCL": "LCL altitude (m)", "Shear6km": "Cisaillement 0-6 km (m/s)"},
        units={"STP": "dimensionless"},
        description="Indice composite développé par la NOAA NSPC pour prévoir la probabilité de tornades significatives (EF2+).",
        application_conditions=["Environnements orageux supercellulaires"],
        limitations=["Valeurs > 1.0 indiquent un fort potentiel de tornade"],
        references=["Thompson et al. (2003) Wea. Forecasting", "NOAA SPC Indices"],
        compute_func=lambda cape, srh1km, lcl_m, shear6km: (cape / 1500.0) * (srh1km / 150.0) * (max(2000.0 - lcl_m, 0.0) / 1000.0) * (shear6km / 20.0),
    ),
]

for entry in ENTRIES:
    EncyclopediaRegistry.register(entry)
