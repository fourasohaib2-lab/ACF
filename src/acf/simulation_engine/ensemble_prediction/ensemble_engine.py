"""Earth Ensemble Prediction Engine."""

from typing import List, Dict, Any
import numpy as np
from acf.simulation_engine.coupled_solver.coupled_earth_solver import CoupledEarthSolver


class EarthEnsembleEngine:
    """Manages multi-member ensemble forecasting (Member 001 to Member N).

    Generates perturbed initial states using singular vector / bred vector proxies,
    runs parallel ensemble trajectory simulations, and computes ensemble statistical moments:
    - Ensemble Mean: bar(X) = 1/N * sum(X_i)
    - Ensemble Spread (Std Dev): sigma_X = sqrt(1/(N-1) * sum((X_i - bar(X))^2))
    - Ensemble Variance
    """

    def __init__(self, solver: CoupledEarthSolver, n_members: int = 20) -> None:
        if n_members < 2:
            raise ValueError("Ensemble size must be at least 2.")
        self.solver = solver
        self.n_members = n_members

    def generate_perturbed_initial_states(
        self, base_state: Dict[str, Any], perturbation_scale: float = 0.05
    ) -> List[Dict[str, Any]]:
        """Generate N perturbed initial state vectors for ensemble initialization.

        Args:
            base_state (Dict[str, Any]): Unperturbed control analysis state vector.
            perturbation_scale (float): Standard deviation ratio of Gaussian noise.

        Returns:
            List[Dict[str, Any]]: N member initial states.
        """
        ensemble_states = []

        # Control member (Member 001) remains unperturbed
        ensemble_states.append(base_state.copy())

        # Members 002 through N receive orthogonal noise perturbations
        for i in range(1, self.n_members):
            member_state = {}
            for key, val in base_state.items():
                if isinstance(val, np.ndarray) and np.issubdtype(val.dtype, np.number):
                    std_val = float(np.std(val)) if np.std(val) > 0 else 1.0
                    noise = np.random.normal(0.0, perturbation_scale * std_val, size=val.shape)
                    member_state[key] = val + noise
                else:
                    member_state[key] = val
            ensemble_states.append(member_state)

        return ensemble_states

    def run_ensemble_forecast(
        self,
        base_state: Dict[str, Any],
        steps: int = 10,
        dt: float = 3600.0,
    ) -> List[Dict[str, Any]]:
        """Run all ensemble members over forecast horizon.

        Returns:
            List[Dict[str, Any]]: List of final states for each member.
        """
        members = self.generate_perturbed_initial_states(base_state)
        final_member_states = []

        for m_idx, state in enumerate(members):
            curr_state = state
            for s in range(steps):
                curr_state = self.solver.step(curr_state, dt=dt)
            final_member_states.append(curr_state)

        return final_member_states

    def compute_ensemble_statistics(
        self, member_states: List[Dict[str, Any]], field_key: str = "T"
    ) -> Dict[str, np.ndarray]:
        """Compute ensemble mean, variance, and spread (std dev) for a state variable.

        Args:
            member_states (List[Dict[str, Any]]): List of ensemble member state dicts.
            field_key (str): Key of target variable (e.g. 'T', 'SST', 'U').

        Returns:
            Dict[str, np.ndarray]: Dictionary with keys 'mean', 'spread', 'variance'.
        """
        field_stack = np.stack([m[field_key] for m in member_states], axis=0)

        ens_mean = np.mean(field_stack, axis=0)
        ens_variance = np.var(field_stack, axis=0, ddof=1)
        ens_spread = np.std(field_stack, axis=0, ddof=1)

        return {
            "mean": ens_mean,
            "variance": ens_variance,
            "spread": ens_spread,
        }
