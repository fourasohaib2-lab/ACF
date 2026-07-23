"""
Data Engine
===========

Main data engine of ACF.
"""

from acf.data.dataset import Dataset


class DataEngine:
    """Main data engine."""

    def create_dataset(
        self,
        name="",
        filepath=None,
        filetype="",
    ):
        return Dataset(
            name=name,
            filepath=filepath,
            filetype=filetype,
        )
