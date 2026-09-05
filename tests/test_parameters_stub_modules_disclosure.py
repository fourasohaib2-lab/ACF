"""
Atmospheric Complexity Framework (ACF)

Locks in the 2026-09-05 audit-de-continuation finding on
acf.parameters: converter.py/validator.py/units.py/categories.py are
empty scaffolding stubs (no class, no function) despite the package's
own "unit conversion tables"/"parameter aliases" purpose statement -
see each module's own NOTE (correction) and acf.parameters/__init__.py.

This test exists so a future silent addition of real (or fabricated)
behavior to one of these 4 files is a deliberate, reviewed change
rather than an unnoticed drift from the documented state - same
pattern as test_map_canvas_is_a_real_verified_duplicate_not_yet_consolidated
in tests/test_collisions_consolidation.py.
"""

import ast
import importlib
from pathlib import Path

STUB_MODULES = [
    "acf.parameters.converter",
    "acf.parameters.validator",
    "acf.parameters.units",
    "acf.parameters.categories",
]


def _public_names(module) -> list[str]:
    return [name for name in dir(module) if not name.startswith("_")]


def test_parameters_stub_modules_export_nothing_public():
    """These 4 modules define no class, function, or constant - only a docstring."""
    for module_name in STUB_MODULES:
        module = importlib.import_module(module_name)
        assert _public_names(module) == [], f"{module_name} now exports something - update its NOTE/this test"


def test_parameters_stub_modules_contain_no_executable_statement():
    """Parsed source has exactly one top-level statement: the module docstring."""
    for module_name in STUB_MODULES:
        module = importlib.import_module(module_name)
        with open(module.__file__, encoding="utf-8") as f:
            tree = ast.parse(f.read())
        assert len(tree.body) == 1
        assert isinstance(tree.body[0], ast.Expr)
        assert isinstance(tree.body[0].value, ast.Constant)
        assert isinstance(tree.body[0].value.value, str)


def test_real_unit_conversion_lives_elsewhere_not_in_acf_parameters():
    """
    acf.data.unit_converter / acf.normalization.units are the real
    implementations - located via the acf package's own directory and
    read directly (not imported) so this doesn't require their parent
    packages' own optional heavy dependencies (e.g. metpy, pulled in by
    acf.normalization/__init__.py) to be installed just to confirm they
    contain real code.
    """
    acf_root = Path(importlib.import_module("acf").__file__).parent
    for relative_path in ["data/unit_converter.py", "normalization/units.py"]:
        source_path = acf_root / relative_path
        assert source_path.is_file()
        tree = ast.parse(source_path.read_text(encoding="utf-8"))
        top_level_defs = [n for n in tree.body if isinstance(n, (ast.FunctionDef, ast.ClassDef))]
        assert top_level_defs, f"{relative_path} should contain real function/class definitions"
