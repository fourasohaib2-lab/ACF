#!/usr/bin/env python3
"""
Train the real FNO surface-temperature surrogate.

Implements docs/ACF_HPC_005_NEXT_ROADMAP.md's third CI/CD axis
("Couplage Avancé Physique-IA (Fourier Neural Operators / FNO)").

Honesty note: training data is generated from ACF's own real
CoupledEarthSolver (see acf.ai.simulation.fno_training's own docstring)
- this session has no access to real ARPEGE/ERA5 archives. The reference
checkpoint committed alongside this script
(models/fno_surface_temperature_reference.pt) was trained with this
script's own default (small) settings, on this repository's development
workstation - a genuine, working proof of the physics-AI coupling
pattern, not a production-scale operational model. Re-run with larger
--trajectories/--steps/--epochs (and, ideally, real GPU hardware - see
the master roadmap's own "v0.9 GPU Tensor Core FNO Neural Solvers" for
that larger scope) for anything beyond a demonstration.
"""

import argparse
import logging
import sys

from acf.ai.simulation.fno_training import generate_training_pairs, save_checkpoint, train_fno

logger = logging.getLogger("acf.train_fno_surrogate")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.strip().splitlines()[0])
    parser.add_argument("--trajectories", type=int, default=8)
    parser.add_argument("--steps", type=int, default=6, help="Steps per trajectory.")
    parser.add_argument("--dt", type=float, default=3600.0)
    parser.add_argument("--n-lat", type=int, default=32)
    parser.add_argument("--n-lon", type=int, default=64)
    parser.add_argument("--n-levels", type=int, default=8)
    parser.add_argument("--epochs", type=int, default=80)
    parser.add_argument("--modes1", type=int, default=8)
    parser.add_argument("--modes2", type=int, default=8)
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--output", default="models/fno_surface_temperature_reference.pt")
    args = parser.parse_args(argv)

    logging.basicConfig(level=logging.INFO, format="%(message)s")

    logger.info(
        "Generating training pairs: %d trajectories x %d steps (grid=%dx%dx%d)",
        args.trajectories, args.steps, args.n_lat, args.n_lon, args.n_levels,
    )
    inputs, targets = generate_training_pairs(
        n_trajectories=args.trajectories,
        n_steps_per_trajectory=args.steps,
        dt_seconds=args.dt,
        n_lat=args.n_lat,
        n_lon=args.n_lon,
        n_levels=args.n_levels,
        seed=args.seed,
    )
    logger.info("Training pairs: %s -> %s", inputs.shape, targets.shape)

    model, history = train_fno(
        inputs, targets, epochs=args.epochs, modes1=args.modes1, modes2=args.modes2, seed=args.seed
    )

    import os

    os.makedirs(os.path.dirname(args.output) or ".", exist_ok=True)
    save_checkpoint(model, history, args.output)

    print(f"Saved trained FNO surrogate to {args.output}")
    print(f"Final train loss: {history['train_loss'][-1]:.6f}")
    print(f"Final val loss:   {history['val_loss'][-1]:.6f}")
    print(
        f"Loss reduction: {history['train_loss'][0]:.4f} -> {history['train_loss'][-1]:.4f} "
        f"({100 * (1 - history['train_loss'][-1] / history['train_loss'][0]):.1f}% reduction)"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
