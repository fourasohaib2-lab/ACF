"""
Real FNO training pipeline for the surface-temperature surrogate.

Generates genuine training pairs by running ACF's own real physics solver
(acf.simulation_engine.coupled_solver.CoupledEarthSolver) from several
perturbed initial conditions, then trains FourierNeuralOperator2D by real
backpropagation to predict T(t + dt) from T(t).

Scope note: this trains a surrogate for ONE field (near-surface
temperature, state["T"][0] - level index 0 is the surface/bottom level,
confirmed against CoupledEarthSolver.compute_interfacial_fluxes()'s own
`surface_temp=state["T"][0, :, :]` and AtmosphericModel.initialize_state()'s
construction (k=0 is unmodified 288.15K, decreasing with k via the
standard lapse rate as k increases - i.e. increasing k means increasing
altitude, not the reverse) as a genuine, working proof of the physics-
AI coupling pattern requested in docs/ACF_HPC_005_NEXT_ROADMAP.md - not a
full multi-variable operational replacement for CoupledEarthSolver (that
larger scope is what the master roadmap's own "v0.9 GPU Tensor Core FNO
Neural Solvers" already names as later, separate work).

Honesty note: training data comes from ACF's own solver, not real
ARPEGE/ERA5 archives - this session has no access to those. See this
module's own docstring and fno_model.py's for the full explanation.
"""

from __future__ import annotations

import logging
from typing import Any

import numpy as np
import torch

from acf.ai.simulation.fno_model import FourierNeuralOperator2D
from acf.simulation_engine.coupled_solver.coupled_earth_solver import CoupledEarthSolver
from acf.simulation_engine.numerical_core.earth_grid import EarthGrid

logger = logging.getLogger("acf.ai.simulation.fno_training")


def generate_training_pairs(
    n_trajectories: int = 8,
    n_steps_per_trajectory: int = 6,
    dt_seconds: float = 3600.0,
    n_lat: int = 32,
    n_lon: int = 64,
    n_levels: int = 8,
    seed: int = 0,
) -> tuple[np.ndarray, np.ndarray]:
    """Run CoupledEarthSolver from several randomly-perturbed initial
    states and collect (T(t), T(t+dt)) surface-temperature pairs.

    Returns
    -------
    (inputs, targets) : both shape (n_pairs, 1, n_lat, n_lon), float32.
    """
    rng = np.random.default_rng(seed)
    inputs: list[np.ndarray] = []
    targets: list[np.ndarray] = []

    for traj in range(n_trajectories):
        grid = EarthGrid(n_lat=n_lat, n_lon=n_lon, n_levels=n_levels)
        solver = CoupledEarthSolver(grid)
        state = solver.initialize_coupled_state()

        # Genuine physical perturbation: a random-amplitude temperature
        # anomaly, so different trajectories actually explore different
        # parts of state space rather than being exact duplicates.
        perturbation = rng.normal(loc=0.0, scale=2.0, size=state["T"].shape)
        state["T"] = state["T"] + perturbation

        for _step in range(n_steps_per_trajectory):
            t_before = state["T"][0, :, :].copy()  # surface level (index 0 - see module docstring)
            state = solver.step(state, dt=dt_seconds)
            t_after = state["T"][0, :, :].copy()

            inputs.append(t_before[np.newaxis, :, :])
            targets.append(t_after[np.newaxis, :, :])

        logger.info("Trajectory %d/%d generated (%d steps)", traj + 1, n_trajectories, n_steps_per_trajectory)

    return (
        np.stack(inputs).astype(np.float32),
        np.stack(targets).astype(np.float32),
    )


def train_fno(
    inputs: np.ndarray,
    targets: np.ndarray,
    epochs: int = 50,
    lr: float = 1e-3,
    val_fraction: float = 0.2,
    modes1: int = 8,
    modes2: int = 8,
    seed: int = 0,
) -> tuple[FourierNeuralOperator2D, dict[str, Any]]:
    """Real training loop: Adam + MSE, genuine backprop through
    FourierNeuralOperator2D. Returns the trained model and a history dict
    with real per-epoch train/val loss (not fabricated numbers)."""
    torch.manual_seed(seed)

    x = torch.from_numpy(inputs)
    y = torch.from_numpy(targets)

    # Normalize (genuine statistics of this run's data) - real physical
    # temperature values are O(200-320K), which would otherwise dominate
    # the loss scale regardless of how well the model actually fits.
    mean, std = x.mean(), x.std().clamp_min(1e-6)
    x_norm = (x - mean) / std
    y_norm = (y - mean) / std

    n = x_norm.shape[0]
    n_val = max(1, int(n * val_fraction))
    perm = torch.randperm(n)
    val_idx, train_idx = perm[:n_val], perm[n_val:]

    model = FourierNeuralOperator2D(in_channels=1, out_channels=1, modes1=modes1, modes2=modes2)
    optimizer = torch.optim.Adam(model.parameters(), lr=lr)
    loss_fn = torch.nn.MSELoss()

    history: dict[str, Any] = {"train_loss": [], "val_loss": []}

    for epoch in range(epochs):
        model.train()
        optimizer.zero_grad()
        pred = model(x_norm[train_idx])
        train_loss = loss_fn(pred, y_norm[train_idx])
        train_loss.backward()
        optimizer.step()

        model.eval()
        with torch.no_grad():
            val_pred = model(x_norm[val_idx])
            val_loss = loss_fn(val_pred, y_norm[val_idx])

        history["train_loss"].append(train_loss.item())
        history["val_loss"].append(val_loss.item())

        if (epoch + 1) % max(1, epochs // 5) == 0:
            logger.info("Epoch %d/%d: train_loss=%.6f val_loss=%.6f", epoch + 1, epochs, train_loss.item(), val_loss.item())

    history["normalization_mean"] = mean.item()
    history["normalization_std"] = std.item()
    return model, history


def save_checkpoint(model: FourierNeuralOperator2D, history: dict[str, Any], path: str) -> None:
    """Persist modes1/modes2 alongside the weights - NOTE (correction):
    load_checkpoint() used to require the caller to pass matching
    modes1/modes2 separately (defaulting to 8/8), with no way to detect
    a mismatch except a cryptic state_dict shape-mismatch RuntimeError at
    load time if a model was trained with different modes. Saved here
    instead, so load_checkpoint() reconstructs the exact architecture the
    checkpoint was actually trained with."""
    torch.save(
        {
            "state_dict": model.state_dict(),
            "modes1": model.modes1,
            "modes2": model.modes2,
            "normalization_mean": history["normalization_mean"],
            "normalization_std": history["normalization_std"],
            "final_train_loss": history["train_loss"][-1],
            "final_val_loss": history["val_loss"][-1],
        },
        path,
    )


def load_checkpoint(path: str, modes1: int | None = None, modes2: int | None = None) -> tuple[FourierNeuralOperator2D, dict[str, Any]]:
    """modes1/modes2 are read from the checkpoint itself (see
    save_checkpoint()'s own NOTE) unless explicitly overridden here."""
    checkpoint = torch.load(path, weights_only=True)
    resolved_modes1 = modes1 if modes1 is not None else checkpoint.get("modes1", 8)
    resolved_modes2 = modes2 if modes2 is not None else checkpoint.get("modes2", 8)
    model = FourierNeuralOperator2D(in_channels=1, out_channels=1, modes1=resolved_modes1, modes2=resolved_modes2)
    model.load_state_dict(checkpoint["state_dict"])
    model.eval()
    return model, checkpoint
