"""
Atmospheric Primitive Equations Module
(Navier-Stokes Navier-Stokes for Atmosphere: du/dt, dv/dt, dp/dz = -rho*g)
"""


class AtmosphericPrimitiveEquations:
    """Équations primitives de la dynamique atmosphérique (Navier-Stokes en coordonnées de pression)."""

    @classmethod
    def solve_momentum(
        cls, u: float, v: float, f: float, dp_dx: float, dp_dy: float = 0.0, rho: float = 1.225
    ) -> dict[str, float]:
        """
        Du/dt = f*v - (1/rho)*dp/dx ; Dv/dt = -f*u - (1/rho)*dp/dy.

        NOTE (correction): the module docstring has always advertised
        solving BOTH du/dt and dv/dt, but this method only ever computed
        and returned du_dt - dv_dt (the meridional momentum tendency,
        which needs u for its Coriolis term -f*u) was simply never
        implemented, which is why `u` went entirely unused despite being
        accepted as a parameter (flagged by `ruff --select ARG`). Added
        dp_dy (defaults to 0.0, preserving the previous behavior for
        every existing caller that doesn't pass it) so dv_dt can now
        genuinely be computed too. Simplified "f-plane, no advection/
        diffusion/curvature" form, same simplification level as the
        existing du_dt term - not a claim of the full primitive
        equations' advective terms.
        """
        du_dt = f * v - (1.0 / rho) * dp_dx
        dv_dt = -f * u - (1.0 / rho) * dp_dy
        return {"du_dt": du_dt, "dv_dt": dv_dt}
