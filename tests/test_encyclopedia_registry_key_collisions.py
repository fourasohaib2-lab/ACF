"""
Regression tests for the encyclopedia registry key-collision bug found during
the Étape 3 encyclopedia literature-verification pass.

REWRITTEN: EncyclopediaRegistry.register() used to silently overwrite
`cls._entries[key]` with no collision detection at all. Five real key
collisions existed across the encyclopedia (ideal_gas_law,
boussinesq_approximation, supercell_thunderstorm, density_altitude_aviation,
thompson_microphysics_scheme) - whichever module happened to import last (a
side effect of unrelated test collection order, not a deliberate contract)
silently won, while the other entry became completely inaccessible. This was
demonstrated to cause real, non-deterministic test failures: `pytest -k
ideal_gas` and `pytest tests/test_scientific_encyclopedia.py` alone both
FAILED before this fix, while a full unfiltered `pytest tests/` run happened
to pass by accidental import ordering - exactly the "correct only by luck"
pattern this session's audit exists to catch. All five collisions were
resolved by renaming the losing side to a distinct key, and register() now
raises immediately on any future accidental collision instead of silently
overwriting.
"""

import pytest

from acf.science.encyclopedia.entry import EncyclopediaEntry
from acf.science.encyclopedia.registry import EncyclopediaRegistry
from acf.science.registry import ScientificRegistry


def test_register_raises_on_key_collision_instead_of_silently_overwriting():
    EncyclopediaRegistry._ensure_initialized()
    existing = EncyclopediaRegistry._entries["ideal_gas_law"]
    dupe = EncyclopediaEntry(
        key="ideal_gas_law",
        name="deliberately colliding test entry",
        domain="Test",
        equation="x",
        latex_equation="x",
        variables={},
        units={},
        description="d",
        application_conditions=[],
        limitations=[],
        references=[],
    )
    with pytest.raises(ValueError, match="key collision"):
        EncyclopediaRegistry.register(dupe)

    # The original entry must be untouched - no partial/silent overwrite.
    assert EncyclopediaRegistry._entries["ideal_gas_law"] is existing


@pytest.mark.parametrize(
    "key1,key2",
    [
        ("ideal_gas_law", "ideal_gas_law_thermodynamics"),
        ("boussinesq_approximation", "boussinesq_approximation_momentum_form"),
        ("supercell_thunderstorm", "supercell_thunderstorm_overview"),
        ("density_altitude_aviation", "density_altitude_aviation_basic"),
        ("thompson_microphysics_scheme", "thompson_microphysics_scheme_basic"),
    ],
)
def test_previously_colliding_pair_both_independently_accessible(key1, key2):
    """Both sides of each of the 5 former collisions must resolve to a real, distinct entry."""
    entry1 = EncyclopediaRegistry.get(key1)
    entry2 = EncyclopediaRegistry.get(key2)
    assert entry1 is not None
    assert entry2 is not None
    assert entry1.key != entry2.key


def test_ideal_gas_law_is_deterministic_and_matches_atmosphere_py_signature():
    """
    CORRECTED: EncyclopediaRegistry.get("ideal_gas_law") used to
    non-deterministically resolve to either atmosphere.py's or
    physical_laws/thermodynamics_laws.py's entry depending on import order.
    Now always atmosphere.py's (density/temperature params).
    """
    entry = EncyclopediaRegistry.get("ideal_gas_law")
    assert entry.name == "Équation d'État du Gaz Parfait"
    result = EncyclopediaRegistry.calculate("ideal_gas_law", density=1.2, temperature=300.0)
    assert pytest.approx(result, rel=1e-3) == 103340.88


def test_thompson_microphysics_scheme_basic_working_compute_func_no_longer_shadowed():
    """
    CORRECTED (the most consequential of the 5 collisions): clouds.py's
    working compute_func (qc+qr+qi+qs+qg) used to be silently discarded
    whenever parameterizations/operational_schemes.py's descriptive-only
    entry of the same key won the import-order race.
    """
    result = EncyclopediaRegistry.calculate(
        "thompson_microphysics_scheme_basic", qc=0.001, qr=0.002, qi=0.0005, qs=0.0003, qg=0.0001
    )
    assert result == pytest.approx(0.001 + 0.002 + 0.0005 + 0.0003 + 0.0001)


def test_scientific_registry_ideal_gas_law_matches_deterministically():
    law = ScientificRegistry.get("ideal_gas_law")
    assert law is not None
    result = law.calculate(density=1.2, temperature=300.0)
    assert pytest.approx(result, rel=1e-3) == 103340.88
