"""
Real vertical-profile physical invariant checking.

Generalizes the exact invariant already verified against real
CoupledEarthSolver output in acf.awci.vertical_field's own tests
(test_pressure_decreases_with_altitude_real_physics) into reusable
validation code, instead of leaving it as a one-off test assertion.
"""

from acf.core.exceptions import VerticalError


def check_pressure_decreases_with_altitude(pressure_by_level: list[float]) -> None:
    """
    Verify a real physical invariant: pressure must strictly decrease
    as native level index increases (level 0 = surface, per
    acf.simulation_engine.coupled_solver.CoupledEarthSolver.
    compute_interfacial_fluxes()'s own convention, reused throughout
    ACF - acf.forecast.engine, acf.awci.vertical_field, etc.).

    Parameters
    ----------
    pressure_by_level : list[float]
        Real local pressure at each native level, surface (index 0)
        to top of atmosphere - e.g.
        acf.awci.vertical_field's own pressure_volume_hpa[:, i, j], or
        ModelConsensusEngine.compute_real_multi_model_disagreement()-
        style per-level pressure.

    Raises
    ------
    VerticalError
        If pressure does not strictly decrease at every level - a
        real physics violation (or a real bug: levels supplied in the
        wrong order, a surface/TOA mix-up), not a cosmetic issue.
    """
    if len(pressure_by_level) < 2:
        return  # nothing to compare

    for level in range(len(pressure_by_level) - 1):
        if not (pressure_by_level[level] > pressure_by_level[level + 1]):
            raise VerticalError(
                f"Pressure at level {level} ({pressure_by_level[level]}) is not greater than "
                f"at level {level + 1} ({pressure_by_level[level + 1]}) - pressure must strictly "
                f"decrease with altitude (level 0 = surface). Levels may be in the wrong order, "
                f"or this profile mixes surface and top-of-atmosphere conventions."
            )
