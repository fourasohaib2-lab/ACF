"""
Data Engine
===========

Main data engine of ACF.

NOTE (found, NOT changed — RÈGLE D'OR / single source of truth): this
module is dead code. `src/acf/data/engine/` is ALSO a package (with
its own __init__.py aliasing DataEngine = DatasetEngine, a more
substantial class with load()/loaded/variable_count()/summary()/
clear() beyond this file's single create_dataset()). Python's import
resolution always finds that package before this sibling module.py of
the same name, so `from acf.data.engine import DataEngine` (or
`import acf.data.engine`) can never actually reach this file - it is
permanently unreachable, silently shadowed. Verified empirically:
`inspect.getfile(DataEngine)` after `from acf.data.engine import
DataEngine` resolves to data/engine/dataset_engine.py, never here. Not
deleted per project convention (never silently delete conflicting
implementations) - flagged so nobody mistakes this for live code when
editing it.
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
