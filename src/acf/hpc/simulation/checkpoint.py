"""Simulation state checkpointing and restart manager."""

import os
import pickle
from typing import Any


class CheckpointManager:
    """Manages simulation state serialization, checkpointing, and fault-tolerant restarts."""

    def __init__(self, checkpoint_dir: str = "checkpoints") -> None:
        self.checkpoint_dir = checkpoint_dir
        os.makedirs(self.checkpoint_dir, exist_ok=True)

    def save_checkpoint(self, state: dict[str, Any], step: int, filename: str | None = None) -> str:
        """Save full simulation state dictionary to disk checkpoint file.

        Args:
            state (Dict[str, Any]): Simulation state dictionary X(t).
            step (int): Simulation time step index.
            filename (Optional[str]): Target path.

        Returns:
            str: Path of saved checkpoint file.
        """
        if filename is None:
            filename = os.path.join(self.checkpoint_dir, f"acf_sim_checkpoint_step_{step:06d}.pkl")

        checkpoint_data = {
            "step": step,
            "state": state,
        }

        with open(filename, "wb") as f:
            pickle.dump(checkpoint_data, f, protocol=pickle.HIGHEST_PROTOCOL)

        return filename

    def load_checkpoint(self, filename: str) -> dict[str, Any]:
        """Load state checkpoint from file.

        Args:
            filename (str): Path to checkpoint file.

        Returns:
            Dict[str, Any]: Unserialized checkpoint data containing 'step' and 'state'.
        """
        with open(filename, "rb") as f:
            data = pickle.load(f)
        return data
