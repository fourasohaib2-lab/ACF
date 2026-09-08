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
