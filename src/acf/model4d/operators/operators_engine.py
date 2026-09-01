"""
ACF Model4D - Operators Engine

Centralisation des opérateurs physiques :
- Gradient
- Divergence
- Laplacian
- Curl
- Advection
- Diffusion
"""

from .advection import Advection
from .curl import Curl
from .diffusion import Diffusion
from .divergence import Divergence
from .gradient import Gradient
from .laplacian import Laplacian


class OperatorsEngine:
    """
    Moteur central des opérateurs Model4D.
    """

    def gradient(self, *args, **kwargs):
        """
        NOTE (correction): this used to call Gradient.calculate(),
        which does not exist on the Gradient class (it only defines
        forward/backward/centered/magnitude) - any call to
        engine.gradient(...) or engine.apply("gradient", ...) always
        raised AttributeError. Untested (no existing test ever
        exercised this operator). Fixed to delegate to
        Gradient.centered(), the standard second-order-accurate default.
        """
        return Gradient.centered(*args, **kwargs)

    def divergence(self, *args, **kwargs):
        return Divergence.compute(*args, **kwargs)

    def laplacian(self, *args, **kwargs):
        return Laplacian.calculate(*args, **kwargs)

    def curl(self, *args, **kwargs):
        """
        NOTE (correction): this used to call Curl.compute(), which just
        sums whatever raw arguments are passed (a generic add-em-up
        helper meant for simple test/integration use) - not
        Curl.calculate(), which is Curl's actual formula
        (dw/dy-dv/dz, du/dz-dw/dx, dv/dx-du/dy). Summing instead of
        subtracting the paired terms produces a physically meaningless
        number for curl (unlike divergence, where compute()'s plain sum
        happens to coincide with the real divergence formula).
        Untested (no existing test ever exercised this operator).
        """
        return Curl.calculate(*args, **kwargs)

    def advection(self, *args, **kwargs):
        return Advection.compute(*args, **kwargs)

    def diffusion(self, *args, **kwargs):
        return Diffusion.calculate(*args, **kwargs)

    def apply(self, operator, *args, **kwargs):
        """
        Application dynamique d'un opérateur.
        """

        operators = {
            "gradient": self.gradient,
            "divergence": self.divergence,
            "laplacian": self.laplacian,
            "curl": self.curl,
            "advection": self.advection,
            "diffusion": self.diffusion,
        }

        if operator not in operators:
            raise ValueError(f"Unknown operator: {operator}")

        return operators[operator](*args, **kwargs)
