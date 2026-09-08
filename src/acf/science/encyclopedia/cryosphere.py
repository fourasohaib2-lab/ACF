"""
Cryosphere Science Encyclopedia Domain
"""

import math

from acf.science.encyclopedia.entry import EncyclopediaEntry
from acf.science.encyclopedia.registry import EncyclopediaRegistry

# ---------------------------------------------------------------------------
# Computational Functions for Cryosphere
# ---------------------------------------------------------------------------


def calculate_snow_albedo_exponential_decay(
    alpha_fresh: float, alpha_aged: float, decay_rate: float, age_or_time: float
) -> float:
    """
    Décroissance exponentielle de l'albédo de la neige entre une valeur
    fraîche et une valeur âgée/mouillée asymptotique :
    alpha_snow = alpha_aged + (alpha_fresh - alpha_aged) * exp(-decay_rate * t).

    NOTE (correction): this entry's "equation" field is fully explicit
    but had no compute_func. Also discovered this is algebraically the
    SAME formula as cryosphere_extended.py's 'snow_albedo_aging_
    metamorphism' entry (expand alpha_fresh*exp(-kt) + alpha_wet*(1-
    exp(-kt)) = alpha_wet + (alpha_fresh-alpha_wet)*exp(-kt) - identical
    to that entry's alpha_min + (alpha_fresh-alpha_min)*exp(-k_aging*t)
    once alpha_wet and alpha_min are recognized as the same physical
    quantity, ~0.50, the asymptotic aged/melting snow albedo, just
    named differently by two literature traditions - general "snow
    albedo feedback" framing here vs. Crocus-style "aging metamorphism"
    framing there). Per ACF's single-source-of-truth convention, both
    entries now share this ONE implementation (imported, not
    reimplemented) rather than silently duplicating the same formula
    under two names.

    Parameters
    ----------
    alpha_fresh : float
        Albédo de la neige fraîche (~0.85), en [0, 1].
    alpha_aged : float
        Albédo asymptotique de la neige âgée/mouillée (~0.50), en [0, 1].
    decay_rate : float
        Taux de décroissance k (unité inverse de age_or_time), > 0.
    age_or_time : float
        Âge de la neige ou temps écoulé depuis la dernière chute (même
        unité que 1/decay_rate), >= 0.

    Returns
    -------
    float
        Albédo de la neige (dimensionless, en [0, 1] si alpha_fresh et
        alpha_aged le sont).
    """
    if not (0.0 <= alpha_fresh <= 1.0):
        raise ValueError("alpha_fresh must be in [0, 1].")
    if not (0.0 <= alpha_aged <= 1.0):
        raise ValueError("alpha_aged must be in [0, 1].")
    if age_or_time < 0.0:
        raise ValueError("age_or_time must be non-negative.")
    return alpha_aged + (alpha_fresh - alpha_aged) * math.exp(-decay_rate * age_or_time)


ENTRIES = [
    EncyclopediaEntry(
        key="snow_albedo_feedback",
        name="Rétroaction Albédo-Neige",
        domain="Cryosphère",
        subdomain="Bilan d'énergie de la cryosphère",
        equation="alpha_snow = alpha_fresh * exp(-k * age) + alpha_wet * (1 - exp(-k * age))",
        latex_equation=r"\alpha_{\text{snow}} = \alpha_{\text{fresh}} e^{-k t} + \alpha_{\text{wet}} (1 - e^{-k t})",
        variables={"alpha_fresh": "Albédo neige fraîche (~0.85)", "alpha_wet": "Albédo neige fondante (~0.50)"},
        units={"alpha": "dimensionless"},
        description="Diminution de l'albédo de la neige avec le vieillissement et la fonte, accentuant le réchauffement radiatif de la surface.",
        application_conditions=["Surfaces recouvertes de neige"],
        limitations=[
            "Dépend du dépôt de suie / carbone noir",
            "Même formule (à renommage de variables près) que "
            "cryosphere_extended.py's 'snow_albedo_aging_metamorphism' - "
            "voir la note de calculate_snow_albedo_exponential_decay() ci-dessus.",
        ],
        references=["WMO Cryosphere Reports", "Wiscombe & Warren (1980) J. Atmos. Sci."],
        compute_func=lambda alpha_fresh, alpha_wet, k, age: calculate_snow_albedo_exponential_decay(
            alpha_fresh, alpha_wet, k, age
        ),
    ),
]

for entry in ENTRIES:
    EncyclopediaRegistry.register(entry)
