"""
Unit test suite for science.encyclopedia.chemistry_extended's Leighton
photostationary-state ozone fix (Étape 3 encyclopedia literature-verification
pass) - the most severe numeric bug found in this pass.

REWRITTEN: calculate_leighton_ozone_photoequilibrium() applied k_o3_no
(1.8e-14 cm^3 molecule^-1 s^-1 - correct per JPL/literature for the
NO+O3->NO2+O2 rate constant at 298K) DIRECTLY to NO2/NO concentrations
expressed in ppb. A bimolecular rate constant in cm^3 molecule^-1 s^-1
requires concentrations in molecules/cm^3, not ppb - without the
ppb<->molecule/cm^3 conversion, the formula returned an [O3] roughly 11
orders of magnitude larger than any physically possible atmospheric ozone
concentration. Fixed by converting through air number density.
"""

import math

from acf.science.encyclopedia.chemistry_extended import calculate_leighton_ozone_photoequilibrium


def test_leighton_ozone_is_physically_plausible_not_astronomically_large():
    """
    CORRECTED: previously returned ~4e11 "ppb" for these inputs (an
    astronomically wrong, physically impossible ozone concentration).
    Real ambient tropospheric ozone is on the order of 10-100+ ppb.
    """
    o3_ppb = calculate_leighton_ozone_photoequilibrium(j_no2=0.008, no2_ppb=5.0, no_ppb=5.0)
    assert 0.0 < o3_ppb < 1000.0


def test_leighton_ozone_matches_direct_pseudo_first_order_computation():
    j_no2, no2_ppb, no_ppb = 0.008, 10.0, 2.0
    k_o3_no = 1.8e-14
    air_m = 2.46e19

    k_pseudo = k_o3_no * air_m * 1e-9
    expected = (j_no2 * no2_ppb) / (k_pseudo * no_ppb)

    result = calculate_leighton_ozone_photoequilibrium(j_no2, no2_ppb, no_ppb, k_o3_no=k_o3_no)
    assert math.isclose(result, expected, rel_tol=1e-9)


def test_leighton_ozone_scales_with_no2_no_ratio():
    """Higher NO2/NO ratio (less NO to titrate O3) should give more O3."""
    low_ratio = calculate_leighton_ozone_photoequilibrium(j_no2=0.008, no2_ppb=5.0, no_ppb=10.0)
    high_ratio = calculate_leighton_ozone_photoequilibrium(j_no2=0.008, no2_ppb=10.0, no_ppb=5.0)
    assert high_ratio > low_ratio


def test_leighton_ozone_zero_for_invalid_inputs():
    assert calculate_leighton_ozone_photoequilibrium(j_no2=0.008, no2_ppb=5.0, no_ppb=0.0) == 0.0
    assert calculate_leighton_ozone_photoequilibrium(j_no2=0.008, no2_ppb=5.0, no_ppb=-1.0) == 0.0
