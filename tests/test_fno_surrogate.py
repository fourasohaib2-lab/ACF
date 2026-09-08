"""
Tests for the real, trained Fourier Neural Operator surrogate
(docs/ACF_HPC_005_NEXT_ROADMAP.md's third CI/CD axis: "Couplage Avancé
Physique-IA (Fourier Neural Operators / FNO)").

CORRECTED: acf.ai.simulation.neural_operator.NeuralOperatorEngine's
existing "FNO" path (predict_next_state, still exercised by
test_simulation_engine.py::test_neural_operator) was found to have zero
learnable parameters - a fixed exponential spectral-decay filter, not
actually a trained Fourier Neural Operator despite the label. These
tests exercise the real, newly-added, genuinely-trained replacement
(fno_model.FourierNeuralOperator2D + fno_training) and
NeuralOperatorEngine.predict_surface_temperature(), which correctly
scopes itself to only the one field it was actually trained on.
"""

import numpy as np
import torch

from acf.ai.simulation.fno_model import FourierNeuralOperator2D, SpectralConv2d
from acf.ai.simulation.fno_training import (
    generate_training_pairs,
    load_checkpoint,
    save_checkpoint,
    train_fno,
)
from acf.ai.simulation.neural_operator import NeuralOperatorEngine


def test_spectral_conv2d_has_learnable_parameters():
    """The defining characteristic of an FNO layer, missing from the old
    NeuralOperatorEngine 'FNO' path entirely."""
    layer = SpectralConv2d(in_channels=2, out_channels=3, modes1=4, modes2=4)
    params = list(layer.parameters())
    assert len(params) == 1
    assert params[0].requires_grad
    assert params[0].shape == (2, 3, 4, 4)


def test_fno_forward_pass_shape():
    model = FourierNeuralOperator2D(in_channels=1, out_channels=1, hidden_channels=8, n_blocks=2, modes1=4, modes2=4)
    x = torch.randn(2, 1, 16, 32)
    y = model(x)
    assert y.shape == (2, 1, 16, 32)


def test_generate_training_pairs_uses_the_real_solver():
    """Training data must come from the real CoupledEarthSolver, not
    invented arrays - shapes/finiteness confirm a real physics run happened."""
    inputs, targets = generate_training_pairs(
        n_trajectories=2, n_steps_per_trajectory=3, n_lat=16, n_lon=32, n_levels=4
    )
    assert inputs.shape == (6, 1, 16, 32)
    assert targets.shape == (6, 1, 16, 32)
    assert np.all(np.isfinite(inputs))
    assert np.all(np.isfinite(targets))
    # Real physical near-surface temperatures, not placeholder zeros/ones.
    assert 150.0 < inputs.mean() < 400.0


def test_training_genuinely_reduces_loss():
    """The core claim under test: this model actually learns via real
    backprop, it isn't a fixed/untrained transform relabeled as an FNO."""
    inputs, targets = generate_training_pairs(
        n_trajectories=3, n_steps_per_trajectory=4, n_lat=16, n_lon=32, n_levels=4, seed=1
    )
    _model, history = train_fno(inputs, targets, epochs=60, modes1=4, modes2=4, seed=1)

    assert history["train_loss"][-1] < history["train_loss"][0]
    assert history["val_loss"][-1] < history["val_loss"][0]
    # Not just "slightly better than random init" - a real, substantial fit.
    assert history["train_loss"][-1] < 0.7 * history["train_loss"][0]


def test_checkpoint_round_trip(tmp_path):
    inputs, targets = generate_training_pairs(n_trajectories=2, n_steps_per_trajectory=3, n_lat=16, n_lon=32, n_levels=4)
    model, history = train_fno(inputs, targets, epochs=10, modes1=4, modes2=4)

    path = str(tmp_path / "fno_checkpoint.pt")
    save_checkpoint(model, history, path)

    loaded_model, checkpoint = load_checkpoint(path, modes1=4, modes2=4)
    assert "final_train_loss" in checkpoint
    assert "normalization_mean" in checkpoint

    # Same weights -> same output for the same input (a real, restorable model).
    x = torch.randn(1, 1, 16, 32)
    with torch.no_grad():
        out_before = model(x)
        out_after = loaded_model(x)
    assert torch.allclose(out_before, out_after, atol=1e-6)


def test_neural_operator_engine_honest_without_a_loaded_surrogate():
    engine = NeuralOperatorEngine()
    result = engine.predict_surface_temperature(np.random.normal(288, 5, size=(16, 32)))
    assert result["predicted_field"] is None
    assert result["status"] == "NOT_PREDICTED_NO_TRAINED_SURROGATE_LOADED"


def test_neural_operator_engine_uses_a_loaded_trained_surrogate(tmp_path):
    inputs, targets = generate_training_pairs(n_trajectories=2, n_steps_per_trajectory=3, n_lat=16, n_lon=32, n_levels=4)
    model, history = train_fno(inputs, targets, epochs=10, modes1=4, modes2=4)
    path = str(tmp_path / "fno_checkpoint.pt")
    save_checkpoint(model, history, path)

    engine = NeuralOperatorEngine(fno_checkpoint_path=path)
    result = engine.predict_surface_temperature(np.random.normal(288, 5, size=(16, 32)).astype(np.float32))

    assert result["status"] == "PREDICTED_BY_TRAINED_SURROGATE"
    assert result["predicted_field"].shape == (16, 32)
    assert np.all(np.isfinite(result["predicted_field"]))
    assert result["surrogate_final_train_loss"] is not None


def test_acceleration_factor_no_longer_a_fabricated_constant():
    """CORRECTED: acceleration_factor used to be a hardcoded "1000.0",
    never benchmarked against anything real."""
    engine = NeuralOperatorEngine()
    assert engine.acceleration_factor is None
