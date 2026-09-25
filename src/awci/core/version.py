"""
Atmospheric Complexity Framework (ACF)

AWCI Core - Version

Real version information - the ``version.py`` module named in
``docs/architecture/awci_reference_architecture.md`` section 1.

AWCI does not yet have its own independent version number or PyPI
release - it ships as part of the ``acf`` distribution (see
``pyproject.toml``'s single ``[project]`` entry), and
``acf.awci_app.run()``'s own real ``--version`` output already prints
``acf.__version__`` for the standalone AWCI application. This module
re-exports that same real, single source of truth rather than
inventing a second, independently-tracked AWCI version number that
would immediately drift out of sync with it.
"""

from __future__ import annotations

from acf.core.version import __author__, __license__, __version__

__all__ = ["__author__", "__license__", "__version__"]
