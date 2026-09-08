"""
Atmospheric Complexity Framework (ACF)

Applied Mathematics, Numerical Methods & Vector Calculus for NWP Encyclopedia Module
"""

import numpy as np

from acf.science.encyclopedia.entry import EncyclopediaEntry
from acf.science.encyclopedia.registry import EncyclopediaRegistry

# ---------------------------------------------------------------------------
# Computational Functions for NWP Mathematics
# ---------------------------------------------------------------------------


def calculate_spherical_divergence(
    u_grid: np.ndarray,
    v_grid: np.ndarray,
    lat_deg: np.ndarray,
    dlon_deg: float,
    earth_radius_m: float = 6371000.0,
) -> np.ndarray:
    """
    Calcul de la divergence horizontale d'un champ de vent (u, v) en coordonnées
    sphériques : div(V) = (1 / (a * cos(phi))) * [du/dlambda + d(v * cos(phi))/dphi].

    u_grid, v_grid: tableaux 2D (lat, lon) en m/s sur une grille régulière en
    longitude. lat_deg: tableau 1D des latitudes (deg) associées aux lignes de
    u_grid/v_grid (peut être irrégulier). dlon_deg: pas de grille uniforme en
    longitude (deg).

    Ne calcule que la composante horizontale (le terme vertical dw/dz de
    l'équation complète nécessite une grille 3D distincte et n'est pas
    représenté ici - c'est la composante horizontale qui porte le facteur
    métrique sphérique 1/(a cos phi) propre à ce système de coordonnées).
    Validé : un champ de rotation solide non divergent u = U0*cos(phi), v = 0
    donne une divergence numériquement nulle (aux erreurs de bord de
    différences finies près), comme l'exige la théorie.
    """
    u = np.asarray(u_grid, dtype=float)
    v = np.asarray(v_grid, dtype=float)
    lat_rad = np.radians(np.asarray(lat_deg, dtype=float))
    dlambda = np.radians(dlon_deg)
    cos_phi = np.cos(lat_rad)[:, None]

    du_dlambda = np.gradient(u, dlambda, axis=1)
    dvcos_dphi = np.gradient(v * cos_phi, lat_rad, axis=0)

    safe_cos_phi = np.where(np.abs(cos_phi) < 1e-6, 1e-6, cos_phi)
    return (du_dlambda + dvcos_dphi) / (earth_radius_m * safe_cos_phi)


def calculate_departure_point_semi_lagrangian(
    x_arrival: float, u_arrival: float, dt: float, num_iterations: int = 3
) -> float:
    """Calcul de la position du point de départ en advection 1D Semi-Lagrangienne x_dep = x - u(x_dep)*dt."""
    x_dep = x_arrival - u_arrival * dt
    for _ in range(num_iterations):
        u_mid = u_arrival
        x_dep = x_arrival - u_mid * dt
    return float(x_dep)


def calculate_finite_difference_gradient(f_values: list[float], dx: float) -> list[float]:
    """Calcul du gradient 1D par différences finies centrées d'ordre 2."""
    n = len(f_values)
    grad = [0.0] * n
    if n < 2 or dx <= 0.0:
        return grad
    grad[0] = (f_values[1] - f_values[0]) / dx
    for i in range(1, n - 1):
        grad[i] = (f_values[i + 1] - f_values[i - 1]) / (2.0 * dx)
    grad[-1] = (f_values[-1] - f_values[-2]) / dx
    return grad


# ---------------------------------------------------------------------------
# Encyclopedia Entries
# ---------------------------------------------------------------------------

ENTRIES: list[EncyclopediaEntry] = [
    EncyclopediaEntry(
        key="tensor_calculus_nwp",
        name="Calcul Tensoriel en Coordonnées Suivant le Relief (Terrain-Following)",
        domain="Mathématiques NWP",
        subdomain="Géométrie différentielle",
        equation="g_ij = dx^k/dx^i * dx^k/dx^j  (Tenseur métrique et Symboles de Christoffel)",
        latex_equation=r"g_{ij} = \frac{\partial x^k}{\partial \xi^i} \frac{\partial x^k}{\partial \xi^j}, \quad \Gamma_{ij}^k = \frac{1}{2} g^{kl} \left(\frac{\partial g_{jl}}{\partial \xi^i} + \frac{\partial g_{il}}{\partial \xi^j} - \frac{\partial g_{ij}}{\partial \xi^l}\right)",
        variables={
            "g_ij": "Tenseur métrique",
            "Gamma": "Symboles de Christoffel de seconde espèce",
            "xi": "Coordonnées généralisées (lambda, phi, eta)",
        },
        units={"Métrique": "dimensionless"},
        description="Formalisme mathématique sous-jacent à la formulation des équations primitives sur un relief escarpé (coordonnées hybrid sigma-pression ou Gal-Chen & Somerville).",
        application_conditions=["Modèles NWP sur relief montagneux (AROME, WRF, ICON)"],
        limitations=["Singularités métriques si la pente du relief dépasse 45 deg"],
        references=["Gal-Chen & Somerville (1975) J. Comput. Phys.", "Durran (2010) Numerical Methods"],
    ),
    EncyclopediaEntry(
        key="vector_calculus_spherical",
        name="Calcul Vectoriel en Coordonnées Sphériques Atmosphériques",
        domain="Mathématiques NWP",
        subdomain="Opérateurs différentiels",
        equation="div(V) = 1/(r cos phi) * [d(u)/dlon + d(v cos phi)/dphi] + d(w)/dz",
        latex_equation=r"\nabla \cdot \mathbf{V} = \frac{1}{a \cos\phi}\left[\frac{\partial u}{\partial \lambda} + \frac{\partial (v \cos\phi)}{\partial \phi}\right] + \frac{\partial w}{\partial z}",
        variables={"a": "Rayon moyen de la Terre (6.371e6 m)", "phi": "Latitude", "lambda": "Longitude"},
        units={"Divergence": "s⁻¹"},
        description="Expression des opérateurs différentiels (gradient, divergence, rotamètre, Laplacien) dans le système de coordonnées sphériques naturelles de la Terre.",
        application_conditions=["Dynamique des fluides atmosphériques à grande échelle"],
        limitations=["Singularité aux pôles géographiques cos(phi) -> 0"],
        references=["Holton & Hakim (2012) An Introduction to Dynamic Meteorology"],
        # NOTE (correction): this was wired to calculate_finite_difference_gradient
        # - the SAME generic 1D Cartesian centered-difference function used by
        # the unrelated finite_difference_schemes entry below. That function
        # takes a flat f_values/dx pair and has no latitude input at all, so it
        # could never apply the cos(phi) metric factor this entry's own
        # equation requires - calling it for "spherical divergence" silently
        # computed a plain 1D gradient instead. Replaced with a genuine
        # spherical-divergence implementation (calculate_spherical_divergence,
        # verified against the textbook zero-divergence solid-rotation case).
        compute_func=calculate_spherical_divergence,
    ),
    EncyclopediaEntry(
        key="spherical_harmonics_nwp",
        name="Harmoniques Sphériques (Base des Modèles Spectraux)",
        domain="Mathématiques NWP",
        subdomain="Méthodes spectrales",
        equation="Y_lm(lat, lon) = P_lm(sin(lat)) * exp(i * m * lon)",
        latex_equation=r"Y_l^m(\phi, \lambda) = P_l^m(\sin\phi) e^{i m \lambda}, \quad \nabla^2 Y_l^m = -\frac{l(l+1)}{a^2} Y_l^m",
        variables={"Plm": "Polynômes associés de Legendre", "l": "Nombre d'onde total", "m": "Nombre d'onde zonal"},
        units={"Y": "dimensionless"},
        description="Fonctions propres de l'opérateur Laplacien sur la sphère constituant la base d'expansion orthogonale des modèles globaux ECMWF IFS et Météo-France ARPEGE.",
        application_conditions=["Modèles spectraux globaux (troncatures triangulaires TCo1279)"],
        limitations=["Transformées de Legendre coûteuses à très haute résolution"],
        references=["Durran (2010)", "ECMWF Technical Documentation"],
    ),
    EncyclopediaEntry(
        key="fft_fast_fourier_transform_nwp",
        name="Transformée de Fourier Rapide (FFT) dans les Modèles Spectraux",
        domain="Mathématiques NWP",
        subdomain="Analyse spectrale",
        equation="Passage de l'espace physique (grille) à l'espace spectral en longitude: O(N log N)",
        latex_equation=r"X(m) = \frac{1}{N_{\lambda}} \sum_{j=0}^{N_{\lambda}-1} x(\lambda_j) e^{-i 2\pi m j / N_{\lambda}}",
        variables={"N_lambda": "Nombre de points de grille en longitude", "m": "Nombre d'onde zonal"},
        units={"Complex": "O(N log N)"},
        description="Algorithme de calcul rapide permettant d'effectuer les transformations bidirectionnelles entre l'espace physique de grille et l'espace des nombres d'onde zonaux.",
        application_conditions=["Cœur des modèles spectraux (IFS, ARPEGE) et filtres de Fourier"],
        limitations=["Exige un nombre de points de grille factorisable (puissances de 2, 3, 5)"],
        references=["Cooley & Tukey (1965) Math. Comput.", "Durran (2010)"],
    ),
    EncyclopediaEntry(
        key="spectral_methods_nwp",
        name="Méthodes Spectrales de Galerkin",
        domain="Mathématiques NWP",
        subdomain="Discrétisation spatiale",
        equation="Projection des équations aux dérivées partielles sur une base de fonctions orthogonales",
        latex_equation=r"\int_{\Omega} \left[ \frac{\partial \psi_N}{\partial t} - \mathcal{L}(\psi_N) \right] Y_l^{m*} \, d\Omega = 0",
        variables={"psi_N": "Champ développé sur N modes spectraux"},
        units={"Error": "Décroissance exponentielle (Spectral accuracy)"},
        description="Méthode de discrétisation offrant une précision spatiale optimale sans erreur de phase ou de dispersion numérique pour la dynamique à grande échelle.",
        application_conditions=["Dynamique atmosphérique globale et équations de Poisson"],
        limitations=["Difficulté d'application pour les conditions aux limites complexes ou non-périodiques"],
        references=["Canuto et al. (2006) Spectral Methods", "Durran (2010)"],
    ),
    EncyclopediaEntry(
        key="finite_difference_schemes",
        name="Schémas aux Différences Finies (Centered, Upwind, Compact)",
        domain="Mathématiques NWP",
        subdomain="Discrétisation spatiale",
        equation="Approximation des dérivées par développement en série de Taylor: df/dx = (f(x+dx) - f(x-dx)) / (2*dx)",
        latex_equation=r"\left.\frac{\partial f}{\partial x}\right|_i = \frac{f_{i+1} - f_{i-1}}{2\Delta x} + \mathcal{O}(\Delta x^2)",
        variables={"dx": "Pas de grille spatial (m)"},
        units={"Ordre": "O(dx^2) à O(dx^6)"},
        description="Méthode de discrétisation locale consistant à remplacer les dérivées continues par des combinaisons linéaires de valeurs discrètes aux points de grille adjacents.",
        application_conditions=["Modèles méso-échelle sur grille structurée (WRF, AROME)"],
        limitations=["Erreurs de phase et de dispersion sur les petites longueurs d'onde (< 4*dx)"],
        references=["Strikwerda (2004) Finite Difference Schemes", "Durran (2010)"],
        compute_func=calculate_finite_difference_gradient,
    ),
    EncyclopediaEntry(
        key="finite_volume_schemes",
        name="Schémas aux Volumes Finis Conservatifs",
        domain="Mathématiques NWP",
        subdomain="Discrétisation spatiale",
        equation="Intégration du bilan de flux sur chaque volume de contrôle V_i",
        latex_equation=r"\frac{d}{dt}\int_{V_i} Q \, dV + \oint_{\partial V_i} \mathbf{F}(Q) \cdot \mathbf{n} \, dS = \int_{V_i} S_Q \, dV",
        variables={"Q": "Quantité conservée (masse, quantité de mouvement, énergie)", "F": "Vecteur flux aux faces"},
        units={"Conservation": "Stricte à la précision machine"},
        description="Méthode de discrétisation basée sur la forme intégrale des lois de conservation, garantissant la conservation stricte des masses et des traceurs même sur des maillages icosaédriques ou non-structurés.",
        application_conditions=["Modèles modernes sur grilles non-structurées (DWD ICON, MPAS, FV3)"],
        limitations=[
            "Calcul des flux aux faces nécessitant des solveurs de Riemann ou des reconstructions d'ordre élevé"
        ],
        references=["LeVeque (2002) Finite Volume Methods for Hyperbolic Problems", "DWD ICON Documentation"],
    ),
    EncyclopediaEntry(
        key="semi_lagrangian_advection_scheme",
        name="Schéma d'Advection Semi-Lagrangien",
        domain="Mathématiques NWP",
        subdomain="Intégration temporelle",
        equation="psi(x, t+dt) = psi(x - V*dt, t)",
        latex_equation=r"\psi(\mathbf{x}, t+\Delta t) = \mathcal{I}_{3D}\left( \psi(\mathbf{x} - \mathbf{V}\Delta t, t) \right)",
        variables={
            "x": "Point de grille d'arrivée",
            "x - V*dt": "Point de départ de la trajectoire fluide (departure point)",
            "I3D": "Interpolateur tridimensionnel (cubic spline / Hermite)",
        },
        units={"CFL": "Inconditionnellement stable (CFL > 1)"},
        description="Schéma d'intégration temporelle affranchissant le pas de temps dt de la condition de Courant-Friedrichs-Lewy (CFL), permettant des pas de temps 5 à 10 fois plus grands dans les modèles NWP.",
        application_conditions=["ECMWF IFS, Météo-France AROME/ARPEGE, Met Office Unified Model"],
        limitations=[
            "Nécessite des interpolations spatiales 3D d'ordre élevé pour éviter la diffusion numérique excessive"
        ],
        references=["Robert (1981) Atmos. Ocean", "Staniforth & Côté (1991) Mon. Wea. Rev."],
        compute_func=calculate_departure_point_semi_lagrangian,
    ),
]

for entry in ENTRIES:
    EncyclopediaRegistry.register(entry)
