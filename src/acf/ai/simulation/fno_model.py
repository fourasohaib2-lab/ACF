"""
Real Fourier Neural Operator (FNO) architecture.

Implements docs/ACF_HPC_005_NEXT_ROADMAP.md's third CI/CD axis:
"Couplage Avancé Physique-IA (Fourier Neural Operators / FNO) :
Accélérer la prévision méso-échelle via des surrogates IA formés sur les
archives ARPEGE/ERA5."

Honesty note (same discipline as the rest of this session): this session
does not have access to real ARPEGE/ERA5 archives, so the training
pipeline in fno_training.py generates its training pairs from ACF's own
real physics solver (acf.simulation_engine.coupled_solver.
CoupledEarthSolver) instead - genuine physically-consistent trajectories,
honestly not real reanalysis/operational-model data. What IS real here,
unlike acf.ai.simulation.neural_operator.NeuralOperatorEngine's existing
"FNO" path (found this session: a fixed, untrained, per-call exponential
spectral-decay filter with zero learnable parameters - not actually a
Fourier Neural Operator in the machine-learning sense, despite the
label), is the architecture itself: SpectralConv2d below has real
learnable complex-valued weight tensors multiplying the low Fourier
modes, trained by real backpropagation (see fno_training.py) - the
architecture from Li et al. 2020, "Fourier Neural Operator for
Parametric Partial Differential Equations".
"""

from __future__ import annotations

import torch
from torch import nn


class SpectralConv2d(nn.Module):
    """2D spectral convolution: keeps the first `modes1` x `modes2` Fourier
    modes and multiplies them by a learnable complex weight tensor, before
    inverse-transforming back to physical space.

    This is the actual defining FNO operation - a genuine learned linear
    operator in Fourier space, not a fixed filter.
    """

    def __init__(self, in_channels: int, out_channels: int, modes1: int, modes2: int) -> None:
        super().__init__()
        self.in_channels = in_channels
        self.out_channels = out_channels
        self.modes1 = modes1
        self.modes2 = modes2

        scale = 1.0 / (in_channels * out_channels)
        self.weights = nn.Parameter(
            scale * torch.randn(in_channels, out_channels, modes1, modes2, dtype=torch.cfloat)
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        batch_size = x.shape[0]
        height, width = x.shape[-2], x.shape[-1]

        x_fft = torch.fft.rfft2(x)

        out_fft = torch.zeros(
            batch_size, self.out_channels, height, width // 2 + 1, dtype=torch.cfloat, device=x.device
        )

        modes1 = min(self.modes1, height)
        modes2 = min(self.modes2, x_fft.shape[-1])

        # Learned complex linear map on the low-frequency modes only
        # (einsum: batch,in,mode1,mode2 x in,out,mode1,mode2 -> batch,out,mode1,mode2).
        out_fft[:, :, :modes1, :modes2] = torch.einsum(
            "bixy,ioxy->boxy",
            x_fft[:, :, :modes1, :modes2],
            self.weights[:, :, :modes1, :modes2],
        )

        return torch.fft.irfft2(out_fft, s=(height, width))


class FNOBlock(nn.Module):
    """One FNO block: spectral conv (global, low-frequency) + a pointwise
    1x1 conv (local, all frequencies) residual path, then a nonlinearity -
    the standard FNO block design."""

    def __init__(self, channels: int, modes1: int, modes2: int) -> None:
        super().__init__()
        self.spectral = SpectralConv2d(channels, channels, modes1, modes2)
        self.pointwise = nn.Conv2d(channels, channels, kernel_size=1)
        self.activation = nn.GELU()

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.activation(self.spectral(x) + self.pointwise(x))


class FourierNeuralOperator2D(nn.Module):
    """Full FNO: a lifting layer, a stack of FNOBlocks, and a projection
    layer back to physical field channels - predicts state(t + dt) from
    state(t) on a fixed lat/lon grid.
    """

    def __init__(
        self,
        in_channels: int = 1,
        out_channels: int = 1,
        hidden_channels: int = 16,
        n_blocks: int = 3,
        modes1: int = 8,
        modes2: int = 8,
    ) -> None:
        super().__init__()
        self.modes1 = modes1
        self.modes2 = modes2
        self.lift = nn.Conv2d(in_channels, hidden_channels, kernel_size=1)
        self.blocks = nn.ModuleList([FNOBlock(hidden_channels, modes1, modes2) for _ in range(n_blocks)])
        self.project = nn.Conv2d(hidden_channels, out_channels, kernel_size=1)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """x: (batch, in_channels, n_lat, n_lon) -> (batch, out_channels, n_lat, n_lon)."""
        h = self.lift(x)
        for block in self.blocks:
            h = block(h)
        return self.project(h)
