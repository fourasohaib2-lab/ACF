"""
Applied Mathematics Encyclopedia Domain
"""

from acf.science.encyclopedia.entry import EncyclopediaEntry
from acf.science.encyclopedia.registry import EncyclopediaRegistry

ENTRIES = [
    EncyclopediaEntry(
        key="laplacian_operator",
        name="Opérateur Laplacien",
        domain="Mathématiques Appliquées",
        subdomain="Analyse vectorielle",
        equation="grad^2(phi) = d2phi/dx2 + d2phi/dy2 + d2phi/dz2",
        latex_equation=r"\nabla^2 \phi = \frac{\partial^2 \phi}{\partial x^2} + \frac{\partial^2 \phi}{\partial y^2} + \frac{\partial^2 \phi}{\partial z^2}",
        variables={"phi": "Champ scalaire atmosphérique (pression, géopotentiel)"},
        units={"Laplacian": "variable/m²"},
        description="Opérateur différentiel scalaire mesurant la différence entre la valeur locale d'un champ et sa moyenne environnante (diffusion).",
        application_conditions=["Champs scalaires continus et deux fois dérivables"],
        limitations=["Sensible aux bruits de grille à haute fréquence"],
        references=["Arfken & Weber (2005) Mathematical Methods for Physicists"],
        compute_func=lambda d2_dx2, d2_dy2, d2_dz2=0.0: d2_dx2 + d2_dy2 + d2_dz2,
    ),
    EncyclopediaEntry(
        key="fast_fourier_transform_nwp",
        name="Transformée de Fourier Rapide (FFT dans les Modèles Spectraux)",
        domain="Mathématiques Appliquées",
        subdomain="Méthodes spectrales",
        equation="F(k) = sum_(n=0)^(N-1) f(n) * exp(-2*pi*i*k*n / N)",
        latex_equation=r"F(k) = \sum_{n=0}^{N-1} f(n) e^{-i 2\pi k n / N}",
        variables={"f(n)": "Signal spatial sur le cercle de latitude", "F(k)": "Coefficients spectraux"},
        units={"F(k)": "complex"},
        description="Algorithme fondamental pour la résolution des équations primitives dans l'espace des harmoniques sphériques (ex: ECMWF IFS).",
        application_conditions=["Grilles périodiques longitudinales"],
        limitations=["Complexité O(N log N)"],
        references=["Cooley & Tukey (1965)", "ECMWF Spectral Model Documentation"],
    ),
]

for entry in ENTRIES:
    EncyclopediaRegistry.register(entry)
