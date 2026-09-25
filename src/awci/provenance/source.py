"""
Atmospheric Complexity Framework (ACF)

AWCI Provenance & Audit - Source

Real, thin view over an already-built
``acf.core.contracts.provenance.Provenance``'s own data-origin fields -
"Which data?" in the reference architecture's own traceability chain
(``docs/architecture/awci_reference_architecture.md`` section 22:
"AWCI → Which model? → Which data? → Which time? → Which variables? →
Which formula? → Which factors? → Which code version?"). Never
computes or guesses a source this ``Provenance`` was not already built
with.
"""

from __future__ import annotations

from dataclasses import dataclass

from acf.core.contracts.provenance import Provenance


@dataclass(frozen=True)
class DataSource:
    """Real "which data" view - the exact real values already recorded
    on the ``Provenance`` this was built from."""

    input_files: tuple[str, ...]
    dataset_version: str
    run_identifier: str

    @property
    def is_known(self) -> bool:
        """True only if a real dataset_version/run_identifier was
        actually supplied (not left at the honest "unknown" default) -
        never treats "unknown" as a real answer."""
        return self.dataset_version != "unknown" and self.run_identifier != "unknown"


def describe_source(provenance: Provenance) -> DataSource:
    """Real, direct extraction of the data-origin fields already on
    ``provenance`` - no new value invented, nothing recomputed."""
    return DataSource(
        input_files=tuple(provenance.input_files),
        dataset_version=provenance.dataset_version,
        run_identifier=provenance.run_identifier,
    )
