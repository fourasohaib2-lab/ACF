"""
Atmospheric Turbulence Encyclopedia Domain
"""

from acf.science.encyclopedia.entry import EncyclopediaEntry
from acf.science.encyclopedia.registry import EncyclopediaRegistry

ENTRIES = [
    EncyclopediaEntry(
        key="kolmogorov_five_thirds_law",
        name="Loi des -5/3 de Kolmogorov (Cascade Turbulente)",
        domain="Turbulence Atmosphérique",
        subdomain="Spectre de la turbulence",
        equation="E(k) = C_k * epsilon^(2/3) * k^(-5/3)",
        latex_equation=r"E(k) = C_k \varepsilon^{2/3} k^{-5/3}",
        variables={"E(k)": "Densité spectrale d'énergie cinétique", "k": "Nombre d'onde spatial", "epsilon": "Taux de dissipation de la TKE", "Ck": "Constante de Kolmogorov (~1.5)"},
        units={"E(k)": "m³/s²", "k": "m⁻¹", "epsilon": "m²/s³"},
        description="Transfert d'énergie cinétique des grands tourbillons vers les petites échelles dans la sous-zone inertielle.",
        application_conditions=["Turbulence isotrope et homogène à très haut nombre de Reynolds"],
        limitations=["Inertie brisée à l'échelle de dissipation visqueuse de Kolmogorov"],
        references=["Kolmogorov (1941) Dok. Akad. Nauk SSSR", "Frisch (1995) Turbulence"],
        compute_func=lambda wavenumber_k, dissipation_epsilon, Ck=1.5: Ck * (dissipation_epsilon ** (2.0 / 3.0)) * (wavenumber_k ** (-5.0 / 3.0)),
    ),
]

for entry in ENTRIES:
    EncyclopediaRegistry.register(entry)
