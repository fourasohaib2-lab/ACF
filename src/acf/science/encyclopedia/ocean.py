"""
Ocean-Atmosphere Interaction Encyclopedia Domain
"""

from acf.science.encyclopedia.entry import EncyclopediaEntry
from acf.science.encyclopedia.registry import EncyclopediaRegistry

ENTRIES = [
    EncyclopediaEntry(
        key="bulk_latent_heat_flux_ocean",
        name="Flux de Chaleur Latente Océan-Atmosphère",
        domain="Océan-Atmosphère",
        subdomain="Échanges de surface",
        equation="Q_e = rho_a * L_v * C_e * U_10 * (q_sat(SST) - q_10)",
        latex_equation=r"Q_e = \rho_a L_v C_e U_{10} \left(q_{\text{sat}}(\text{SST}) - q_{10}\right)",
        variables={"rho_a": "Masse volumique de l'air", "Lv": "Chaleur latente de vaporisation", "Ce": "Coefficient de transfert d'humidité (~1.2e-3)", "U10": "Vent à 10 m", "SST": "Température de surface de la mer"},
        units={"Q_e": "W/m²"},
        description="Transfert d'énergie thermique sous forme d'évaporation de l'océan vers l'atmosphère.",
        application_conditions=["Couche de surface océanique"],
        limitations=["Sensible aux fortes brises et déferlement des vagues"],
        references=["COARE 3.0 Bulk Algorithm", "Fairall et al. (2003) J. Climate"],
        compute_func=lambda rho_a, U10, dq, Ce=1.2e-3, Lv=2.5e6: rho_a * Lv * Ce * U10 * dq,
    ),
    EncyclopediaEntry(
        key="enso_cycle",
        name="Oscillation Australe El Niño (ENSO)",
        domain="Océan-Atmosphère",
        subdomain="Variabilité climatique interannuelle",
        equation="ONI = 3-month running mean of SST anomalies in Nino 3.4 region",
        latex_equation=r"\text{ONI} = \overline{\Delta \text{SST}}_{\text{Nino 3.4}}",
        variables={"SST": "Température de surface du Pacifique équatorial"},
        units={"ONI": "°C"},
        description="Mode majeur de variabilité couplée océan-atmosphère modifiant le régime mondial des précipitations et de la circulation de Walker.",
        application_conditions=["Pacifique équatorial central et oriental"],
        limitations=["Prévisibilité limitée au-delà de la barrière du printemps"],
        references=["NOAA Climate Prediction Center", "WMO ENSO Updates"],
    ),
]

for entry in ENTRIES:
    EncyclopediaRegistry.register(entry)
