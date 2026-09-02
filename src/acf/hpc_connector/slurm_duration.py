"""
Real SLURM duration string parsing - shared by
`SlurmScheduler.get_job_progress()`.

SLURM's own `squeue -o %M`/`%l` duration format (per its real manual):
`[days-]hours:minutes:seconds`, `hours:minutes:seconds`, or
`minutes:seconds` depending on how long the value is - not a single
fixed format, so a naive `int(x.split(":")[0])*60 + ...` would
misparse most real values. `%l` (time limit) can also genuinely be the
literal string `"UNLIMITED"` (no `--time` was set) - a real, valid
SLURM value with no numeric seconds equivalent, honestly returned as
`None` here rather than an invented number.
"""

from __future__ import annotations

#: Real SLURM literal values with no numeric duration - not an
#: exhaustive SLURM state list, only the ones squeue's %l/%M columns
#: are documented to actually emit for "no bound"/"not applicable".
_NON_NUMERIC_VALUES = frozenset({"UNLIMITED", "NOT_SET", "N/A", "INVALID"})


def parse_slurm_duration(value: str) -> int | None:
    """
    Parse one real SLURM duration string into whole seconds.

    Returns
    -------
    int or None
        Whole seconds, or `None` if `value` is empty, one of SLURM's
        real non-numeric literals (see `_NON_NUMERIC_VALUES`), or
        genuinely unparseable - never a guessed number.
    """
    value = value.strip()
    if not value or value.upper() in _NON_NUMERIC_VALUES:
        return None

    days = 0
    rest = value
    if "-" in value:
        day_part, rest = value.split("-", 1)
        if not day_part.isdigit():
            return None
        days = int(day_part)

    time_parts = rest.split(":")
    if not (1 <= len(time_parts) <= 3) or not all(p.isdigit() for p in time_parts):
        return None
    padded = [0] * (3 - len(time_parts)) + [int(p) for p in time_parts]
    hours, minutes, seconds = padded

    return days * 86400 + hours * 3600 + minutes * 60 + seconds
