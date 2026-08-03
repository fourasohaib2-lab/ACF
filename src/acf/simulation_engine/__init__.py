"""ACF Planetary Simulation Engine.

Global Earth Numerical Simulation & Forecast Core (ACF-DT-003).
Calculates future Earth state evolution:
    X(t + dt) = M(X(t), Physics, Forcing, AI)
where X = [T, P, U, V, q, O3, CO2, SST, Ice, Soil, Biomass].
"""

from acf.simulation_engine.coupled_solver.coupled_earth_solver import CoupledEarthSolver
from acf.simulation_engine.numerical_core.earth_grid import EarthGrid, GridResolution

__all__ = [
    "CoupledEarthSolver",
    "EarthGrid",
    "GridResolution",
]
