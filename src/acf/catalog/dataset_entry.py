"""
ACF Dataset Catalog Entry

Represents a loaded scientific dataset.
"""

from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class DatasetEntry:
    """
    Information about a dataset.
    """

    dataset_id: str

    name: str

    filepath: str

    filetype: str

    variables: list = field(default_factory=list)

    metadata: dict = field(default_factory=dict)

    source: str = ""

    created: str = field(default_factory=lambda: datetime.now().isoformat())

    def summary(self):

        return {
            "id": self.dataset_id,
            "name": self.name,
            "filetype": self.filetype,
            "variables": self.variables,
            "source": self.source,
            "created": self.created,
        }
