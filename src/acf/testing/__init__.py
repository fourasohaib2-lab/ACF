"""
ACF testing infrastructure - not scientific/HPC/GUI code, real support
utilities for this repository's own test suite.

See `acf.testing.golden` for the Prompt Maître ACF v2.0's section
31-32 "Golden Datasets" gap.
"""

from acf.testing.golden import GoldenMismatchError, assert_matches_golden, load_golden, write_golden

__all__ = ["GoldenMismatchError", "assert_matches_golden", "load_golden", "write_golden"]
