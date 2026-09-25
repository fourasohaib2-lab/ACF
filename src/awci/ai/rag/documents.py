"""
Atmospheric Complexity Framework (ACF)

AWCI RAG - Documents & Corpus Extraction

Builds the real document corpus this package's retriever searches over,
entirely by Python introspection (``inspect``/``pkgutil``) of the
already-real, already-cited ``awci.knowledge`` package - never a
hand-typed or synthesized text. See this package's own ``__init__.py``
docstring for the full scope discipline.
"""

from __future__ import annotations

import importlib
import inspect
import pkgutil
import subprocess
from dataclasses import dataclass
from pathlib import Path

import awci.knowledge

#: Real, repo-relative root this package's git-commit lookups are run
#: from - the real checkout containing awci.knowledge itself.
_REPO_ROOT = Path(awci.knowledge.__file__).resolve().parents[3]

#: Real per-file git-commit cache, populated lazily by
#: ``_git_commit_for()`` - avoids one ``git log`` subprocess per
#: document when many documents share the same source file.
_GIT_COMMIT_CACHE: dict[str, str | None] = {}


@dataclass(frozen=True)
class Provenance:
    """
    Real, exact provenance for one retrieved document - never
    fabricated or approximated.

    source_path : str
        Real, repo-relative file path (e.g.
        ``src/awci/knowledge/meteorology/orographic_turbulence.py``).
    module : str
        Real, dotted import path (e.g.
        ``awci.knowledge.meteorology.orographic_turbulence``).
    symbol : str
        Real class/enum name this document's text came from, or an
        empty string for a whole-module document (the module's own
        top-level docstring).
    git_commit : str | None
        Real git commit hash that last touched ``source_path``, or
        ``None`` (never a fabricated hash) if git is unavailable, the
        file is untracked, or this checkout is not a git repository.
    """

    source_path: str
    module: str
    symbol: str
    git_commit: str | None


@dataclass(frozen=True)
class Document:
    """
    One real, retrievable unit of AWCI knowledge - the real docstring
    text of one module or one of its real, defined classes/enums, with
    exact provenance. ``content`` is always real, already-committed
    text - this package never generates or paraphrases it.
    """

    content: str
    provenance: Provenance


def _git_commit_for(source_path: Path) -> str | None:
    """Real ``git log -1`` lookup for the last commit touching
    ``source_path``, cached per path. Returns ``None`` (never
    fabricated) on any failure - a fresh checkout without git history,
    a non-git install, or git simply not being on PATH are all real,
    honest reasons to have no commit hash, not errors to raise."""
    key = str(source_path)
    if key in _GIT_COMMIT_CACHE:
        return _GIT_COMMIT_CACHE[key]
    commit: str | None
    try:
        result = subprocess.run(
            ["git", "log", "-1", "--format=%H", "--", key],
            cwd=_REPO_ROOT,
            capture_output=True,
            text=True,
            timeout=5,
            check=False,
        )
        commit = result.stdout.strip() or None if result.returncode == 0 else None
    except (OSError, subprocess.SubprocessError):
        commit = None
    _GIT_COMMIT_CACHE[key] = commit
    return commit


def _iter_knowledge_module_names() -> list[str]:
    """Real, always-in-sync module list - walks the real
    ``awci.knowledge`` package tree rather than a hand-maintained list
    that could silently go stale as new knowledge modules are added."""
    return sorted(
        module_info.name
        for module_info in pkgutil.walk_packages(awci.knowledge.__path__, prefix="awci.knowledge.")
        if not module_info.ispkg
    )


def _document_for_module(module: object, module_name: str, source_path: Path) -> Document | None:
    """Real whole-module document from ``module.__doc__`` - the module
    docstring every real awci.knowledge module already carries its own
    source citation in. ``None`` (never a fabricated placeholder) if
    the module genuinely has no docstring."""
    doc = inspect.getdoc(module)
    if not doc:
        return None
    provenance = Provenance(
        source_path=str(source_path),
        module=module_name,
        symbol="",
        git_commit=_git_commit_for(source_path),
    )
    return Document(content=doc, provenance=provenance)


def _documents_for_symbols(module: object, module_name: str, source_path: Path) -> list[Document]:
    """Real per-symbol documents - every real class/enum genuinely
    DEFINED in this module (not merely imported into its namespace,
    e.g. CloudGenus reused by weather_front.py is only indexed once,
    under its own real defining module) with a real, non-empty
    docstring."""
    documents: list[Document] = []
    for name, obj in inspect.getmembers(module, inspect.isclass):
        if getattr(obj, "__module__", None) != module_name:
            continue
        doc = inspect.getdoc(obj)
        if not doc:
            continue
        provenance = Provenance(
            source_path=str(source_path),
            module=module_name,
            symbol=name,
            git_commit=_git_commit_for(source_path),
        )
        documents.append(Document(content=doc, provenance=provenance))
    return documents


def build_document_corpus() -> list[Document]:
    """
    Real document corpus - every real module docstring and real
    class/enum docstring found in ``awci.knowledge`` today, each with
    exact provenance (see ``Provenance``). Deterministic: the same real
    checkout always yields the same real corpus (module order sorted,
    symbol order as ``inspect.getmembers`` itself returns, which is
    alphabetical).
    """
    documents: list[Document] = []
    for module_name in _iter_knowledge_module_names():
        module = importlib.import_module(module_name)
        source_file = inspect.getsourcefile(module)
        if source_file is None:
            continue  # a real, honest skip - no source to attribute this to
        source_path = Path(source_file).resolve().relative_to(_REPO_ROOT)
        module_document = _document_for_module(module, module_name, source_path)
        if module_document is not None:
            documents.append(module_document)
        documents.extend(_documents_for_symbols(module, module_name, source_path))
    return documents
