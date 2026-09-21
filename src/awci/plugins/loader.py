"""
Atmospheric Complexity Framework (ACF)

AWCI Plugins - Loader

Real dynamic plugin discovery from a real filesystem directory - the
``loader.py`` module named in
``docs/architecture/awci_reference_architecture.md`` section 20. A
plugin file is arbitrary, real, caller-supplied code - a broad
``except Exception`` here is a deliberate, real, disclosed design
choice (an untrusted/unvetted plugin failing to import or construct
must never crash the whole discovery, and its real failure reason must
never be silently swallowed), not sloppy error handling.
"""

from __future__ import annotations

import importlib.util
import inspect
from dataclasses import dataclass
from pathlib import Path

from awci.plugins.interface import AWCIPlugin


@dataclass(frozen=True)
class PluginLoadError:
    """One real, disclosed failure to load a candidate plugin file -
    never silently swallowed."""

    source_path: str
    reason: str


@dataclass(frozen=True)
class PluginDiscoveryResult:
    """Real result of one ``discover_plugins()`` call - every real
    plugin instance that loaded successfully, plus every real,
    disclosed failure, kept separate so a caller can act on either."""

    plugins: tuple[AWCIPlugin, ...]
    errors: tuple[PluginLoadError, ...]


def discover_plugins(plugin_dir: Path | str) -> PluginDiscoveryResult:
    """
    Real dynamic plugin discovery - scans ``plugin_dir`` for
    non-underscore-prefixed ``*.py`` files, imports each via
    ``importlib``, and instantiates every real ``AWCIPlugin`` subclass
    genuinely DEFINED in that file (not merely imported into its
    namespace - same "only the true defining module" discipline
    already established in ``awci.ai.rag.documents``). A file that
    fails to import, or whose ``AWCIPlugin`` subclass fails to
    construct, is recorded as a real ``PluginLoadError`` with the real
    exception type/message - never silently skipped, and never crashes
    the discovery of every other real file in the directory.
    """
    plugin_dir = Path(plugin_dir)
    plugins: list[AWCIPlugin] = []
    errors: list[PluginLoadError] = []
    if not plugin_dir.is_dir():
        return PluginDiscoveryResult(
            plugins=(), errors=(PluginLoadError(source_path=str(plugin_dir), reason="not a real directory"),)
        )
    for path in sorted(plugin_dir.glob("*.py")):
        if path.name.startswith("_"):
            continue
        module_name = f"_awci_plugin_{path.stem}"
        try:
            spec = importlib.util.spec_from_file_location(module_name, path)
            if spec is None or spec.loader is None:
                raise ImportError(f"could not build an import spec for {path}")
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
        except Exception as exc:
            errors.append(PluginLoadError(source_path=str(path), reason=f"{type(exc).__name__}: {exc}"))
            continue
        for _name, obj in inspect.getmembers(module, inspect.isclass):
            if obj is AWCIPlugin or not issubclass(obj, AWCIPlugin):
                continue
            if obj.__module__ != module_name:
                continue
            try:
                plugins.append(obj())
            except Exception as exc:
                errors.append(PluginLoadError(source_path=str(path), reason=f"{type(exc).__name__}: {exc}"))
    return PluginDiscoveryResult(plugins=tuple(plugins), errors=tuple(errors))
