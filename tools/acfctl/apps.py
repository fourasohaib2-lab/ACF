"""
Atmospheric Complexity Framework (ACF)

acfctl - Known Apps

Real, already-registered ACF console-script entry points acfctl can
start/stop/status - the exact real table already in ``pyproject.toml``'s
own ``[project.scripts]`` (kept in sync by
``tests/test_acfctl.py::test_known_apps_matches_pyproject_scripts_exactly``,
never hand-duplicated and left to silently drift).
"""

from __future__ import annotations

KNOWN_APPS: dict[str, str] = {
    "gui": "acf-gui",
    "web": "acf-web",
    "awci": "acf-awci",
}
