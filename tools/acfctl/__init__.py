"""
Atmospheric Complexity Framework (ACF)

acfctl - Operational Control Point (``tools/acfctl/``)

Real implementation of
``docs/architecture/acf_reference_architecture.md``'s own stated intent:
"``acfctl`` was meant to become the operational control point: ``acfctl
start | stop | status | report ...``" - previously identified as a
genuinely absent piece in
``docs/architecture/acf_awci_architecture_gap_analysis.md`` ("``tools/
acfctl/`` — an operational CLI control point — was not found... ``acfctl
start/stop/status/report`` does not exist").

Real, disclosed scope: manages the 3 real, already-registered
console-script apps (``pyproject.toml``'s own ``[project.scripts]``:
``acf-gui``/``acf-web``/``acf-awci``) as real OS subprocesses, tracked
via a real PID file under the same real ``~/.acf/`` local-state
directory already established by ``acf.workspace.recent``, using
``psutil`` (an already-real dependency) for cross-platform liveness
checks. ``report`` builds a real environment/health report from
independently-verifiable facts only - never a fabricated
self-certification (see ``report.py``'s own docstring for the
disclosed cautionary precedent this module avoids repeating).
Deliberately NOT built on Qt's own ``QLocalServer`` single-instance
mechanism (``acf.gui.single_instance``) - that needs a running Qt event
loop and only ever covered ``acf-gui``, not ``acf-web``/``acf-awci``.

Callable as ``python -m tools.acfctl <command>`` (see ``__main__.py``).
Deliberately NOT registered as a ``pyproject.toml``
``[project.scripts]`` console-script entry point alongside
``acf-gui``/``acf-web``/``acf-awci``: those 3 live under ``src/``, the
one directory ``[tool.setuptools.packages.find]`` actually scans, while
``tools/`` (like every other real script already there, e.g.
``omniroute_manager.py``) is repo-root-only, development-time tooling
not included in the installable distribution - adding a console-script
entry that resolves only in an editable/repo-root checkout, and breaks
a real ``pip install``/wheel build, would be a real, disclosed
packaging inconsistency this module avoids introducing.
"""

from __future__ import annotations
