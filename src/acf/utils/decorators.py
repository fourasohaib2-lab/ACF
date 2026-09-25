"""
Atmospheric Complexity Framework (ACF)

Utils - Decorators

Real, generic, stdlib-only decorators - the ``decorators.py`` module
named in
``docs/architecture/acf_awci_architecture_gap_analysis.md`` (row
``utils/{...}.py``). Only ``retry`` - a genuinely reusable real need
(several real connectors in this codebase, e.g. ``awci.data.
connectors.pirep_reports.PIREPConnector``, make one real HTTP attempt
and honestly report failure rather than retrying - a caller wanting
retry behavior currently has to write its own loop). Not wired into
any existing connector here (out of scope - each connector's own
honest-failure-reporting behavior is unchanged); a real, disclosed
future addition for a caller that wants it.
"""

from __future__ import annotations

import functools
import time
from collections.abc import Callable
from typing import TypeVar

T = TypeVar("T")


def retry(
    attempts: int = 3,
    delay_seconds: float = 0.0,
    exceptions: tuple[type[BaseException], ...] = (Exception,),
) -> Callable[[Callable[..., T]], Callable[..., T]]:
    """
    Real retry decorator - calls the wrapped function up to
    ``attempts`` real times, real-sleeping ``delay_seconds`` between
    attempts, re-raising the last real exception if every attempt
    fails. ``attempts`` must be at least 1.
    """
    if attempts < 1:
        raise ValueError(f"attempts must be at least 1, got {attempts}")

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> T:
            last_exception: BaseException | None = None
            for attempt in range(1, attempts + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as exc:
                    last_exception = exc
                    if attempt < attempts and delay_seconds > 0:
                        time.sleep(delay_seconds)
            assert last_exception is not None
            raise last_exception

        return wrapper

    return decorator
