"""
Unit test for the "hail_size_estimation_mesh" encyclopedia entry's
documentation fix (Étape 3 encyclopedia literature-verification pass).

REWRITTEN: the entry's documented equation used to be "MESH = 2.54 *
(SHI)^0.5" (deriving MESH from the Severe Hail Index SHI), but its wired
compute_func (estimate_hail_size_mesh) never computed MESH from SHI at all -
it classifies an ALREADY-KNOWN MESH value (mm) into a size-category string,
and doesn't even accept an `shi` parameter. The SHI-to-MESH formula's
coefficients were investigated this session and found unverifiable against
primary sources, so this was fixed by correcting the documentation to
honestly describe the classification step the compute_func actually
performs, rather than implementing an unverified formula.
"""

from acf.science.encyclopedia.registry import EncyclopediaRegistry


def test_hail_mesh_entry_no_longer_claims_to_derive_mesh_from_shi():
    entry = EncyclopediaRegistry.get("hail_size_estimation_mesh")
    assert entry is not None
    assert "SHI" not in entry.equation
    assert "shi" not in entry.variables
    assert "mesh_mm" in entry.variables


def test_hail_mesh_entry_takes_mesh_mm_not_shi():
    """The compute_func genuinely takes an already-known MESH value, not SHI."""
    result = EncyclopediaRegistry.calculate("hail_size_estimation_mesh", mesh_mm=55.0)
    assert isinstance(result, str)
    assert "tennis" in result.lower() or "sévère" in result.lower()

    result_small = EncyclopediaRegistry.calculate("hail_size_estimation_mesh", mesh_mm=5.0)
    assert "risque majeur" in result_small.lower() or "pas de" in result_small.lower()
