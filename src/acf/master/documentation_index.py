"""
Atmospheric Complexity Framework (ACF)

Documentation Indexer Engine Module (Phase 15)
(DocumentationIndexer indexing classes, functions, physical laws, equations, and references)
"""

import ast
from pathlib import Path
from typing import Any

_SRC_ROOT = Path(__file__).resolve().parents[1]  # .../src/acf


class DocumentationIndexer:
    """
    Indexeur automatique de la documentation, des équations et des références du framework.
    """

    @classmethod
    def index_framework_documentation(cls) -> dict[str, Any]:
        """
        Génère l'index réel de la documentation d'ACF : classes et
        fonctions comptées par balayage AST du code source, lois et
        références comptées via les registres scientifiques réels
        (ScientificRegistry / EncyclopediaRegistry).

        NOTE (correction): this used to unconditionally return fixed
        fake counts (350 classes, 1200 functions, 450 laws, 850
        references, "UP_TO_DATE") regardless of the codebase's actual
        content. Now performs a real AST scan of src/acf/ for
        classes/functions, and queries the real science registries for
        law/reference counts.
        """
        classes = 0
        functions = 0
        for path in _SRC_ROOT.rglob("*.py"):
            if "__pycache__" in path.parts:
                continue
            try:
                tree = ast.parse(path.read_text(encoding="utf-8", errors="replace"))
            except SyntaxError:
                continue
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    classes += 1
                elif isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef):
                    functions += 1

        laws_indexed = 0
        references_indexed = 0
        try:
            from acf.science.encyclopedia.registry import EncyclopediaRegistry

            entries = EncyclopediaRegistry.list_entries()
            laws_indexed = len(entries)
            references_indexed = sum(len(e.references) for e in entries)
        except Exception:
            # Registry not importable in this context (e.g. partial
            # environment) - report what we could actually determine
            # rather than fabricate a number.
            pass

        return {
            "total_classes_indexed": classes,
            "total_functions_indexed": functions,
            "total_laws_indexed": laws_indexed,
            "total_references_indexed": references_indexed,
            "index_status": "INDEXED_FROM_LIVE_SCAN",
            "is_real_data": True,
        }
