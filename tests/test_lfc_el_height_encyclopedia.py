"""
Unit test for the "lfc_height_equation"/"el_height_equation" encyclopedia
entries' fabricated-formula fix (Étape 3 encyclopedia literature-verification
pass).

REWRITTEN: calculate_lfc_height(z_lcl, cape) and calculate_el_height(z_lfc,
cape) used to return ad-hoc linear formulas (z_lcl+1500, z_lfc+1000+cape*3.5,
etc.) with no physical basis, dressed with citations (WMO-No. 8, NOAA SPC,
AMS Glossary, ECMWF Convection Documentation) that define the CONCEPT of
LFC/EL but do not support these specific formulas. Verified via WebSearch:
no closed-form LFC/EL-from-(LCL or LFC, CAPE) approximation exists in the
meteorological literature - both are always determined by finding where a
parcel's virtual-temperature profile crosses the environmental profile,
which requires the actual sounding. Both entries' own documented equations
already correctly stated this true definition; only the compute_func
fabricated a shortcut. Now honestly raises NotImplementedError.
lcl_height_equation (a genuinely standard Espy/Bolton approximation) is
unaffected.
"""

import pytest

from acf.science.encyclopedia.cloud_microphysics.cloud_classification import (
    calculate_el_height,
    calculate_lcl_height,
    calculate_lfc_height,
)
from acf.science.encyclopedia.registry import EncyclopediaRegistry


def test_lfc_height_no_longer_returns_a_fabricated_formula():
    with pytest.raises(NotImplementedError):
        calculate_lfc_height(z_lcl=1200.0, cape=1500.0)


def test_el_height_no_longer_returns_a_fabricated_formula():
    with pytest.raises(NotImplementedError):
        calculate_el_height(z_lfc=2500.0, cape=1500.0)


def test_lfc_and_el_encyclopedia_entries_honestly_raise():
    with pytest.raises(NotImplementedError):
        EncyclopediaRegistry.calculate("lfc_height_equation", z_lcl=1200.0, cape=1500.0)
    with pytest.raises(NotImplementedError):
        EncyclopediaRegistry.calculate("el_height_equation", z_lfc=2500.0, cape=1500.0)


def test_lcl_height_unaffected_still_the_standard_approximation():
    """lcl_height_equation is a genuine, standard (Espy 1841 / Bolton 1980) approximation - untouched."""
    assert calculate_lcl_height(temp_c=25.0, dewpoint_c=15.0) == 1250.0
    result = EncyclopediaRegistry.calculate("lcl_height_equation", temp_c=25.0, dewpoint_c=15.0)
    assert result == 1250.0
