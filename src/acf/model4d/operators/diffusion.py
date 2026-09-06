"""
ACF Model4D - Diffusion Operator

Calcul de diffusion atmosphérique :
D = K × ∇²φ

où :
K  : coefficient de diffusion
∇² : Laplacien
φ  : champ atmosphérique
"""


class Diffusion:
    """
    Operator de diffusion 4D.

    Utilisé pour simuler :
    - mélange turbulent
    - diffusion thermique
    - transport atmosphérique

    NOTE (Physics Guard, 2026-09-06 model4d duplication/fabrication
    audit continuation): the class-level formula above (D = K x nabla^2
    phi) is only actually applied in calculate(coefficient, laplacian).
    horizontal(x, y) and vertical(z) skip the diffusion coefficient K
    entirely and just return the raw Laplacian component(s) unweighted
    (x+y, z) - so despite their "Diffusion horizontale/verticale"
    docstrings, they compute a Laplacian, not a diffusion. Minor (no
    AI/ML overclaim, this package is disconnected from the rest of ACF
    - see acf.model4d's own module docstring), but disclosed rather
    than silently trusted.
    """

    @staticmethod
    def calculate(laplacian, coefficient):
        """
        Calcule la diffusion.

        diffusion = coefficient * laplacian
        """
        return round(coefficient * laplacian, 12)

    @staticmethod
    def compute(*values):
        """
        Somme générique pour tests et intégration.
        """
        return sum(values)

    @staticmethod
    def strength(value):
        """
        Classification de l'intensité.
        """
        if abs(value) < 1e-6:
            return "Weak"

        if abs(value) < 1e-5:
            return "Moderate"

        return "Strong"

    @staticmethod
    def horizontal(x, y):
        """
        Diffusion horizontale.
        """
        return x + y

    @staticmethod
    def vertical(z):
        """
        Diffusion verticale.
        """
        return z
