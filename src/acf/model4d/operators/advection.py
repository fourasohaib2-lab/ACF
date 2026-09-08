"""
ACF - Model4D
Advection Operator

Calcule le transport d'une quantité scalaire par un champ de vitesse.

Formule :
A = u*dφ/dx + v*dφ/dy + w*dφ/dz
"""


class Advection:
    """
    Operateur d'advection 4D.

    Support :
    - 1D
    - 2D
    - 3D
    """

    @staticmethod
    def compute(*, velocity, gradient):
        """
        Calcule l'advection.

        velocity :
            tuple/list (u,v,w)

        gradient :
            tuple/list (dφ/dx,dφ/dy,dφ/dz)
        """

        size = min(len(velocity), len(gradient))

        return sum(velocity[i] * gradient[i] for i in range(size))

    @staticmethod
    def horizontal(u, dphi_dx, v, dphi_dy):
        """
        Advection horizontale 2D.
        """

        return u * dphi_dx + v * dphi_dy

    @staticmethod
    def vertical(w, dphi_dz):
        """
        Advection verticale.
        """

        return w * dphi_dz

    @staticmethod
    def category(value):
        """
        Classification intensité.
        """

        value = abs(value)

        if value < 1e-6:
            return "Weak"

        if value < 1e-5:
            return "Moderate"

        return "Strong"
