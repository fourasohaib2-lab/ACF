import math

import pytest

from acf.science.sweat_index import SWEATIndex


def test_sweat():

    value = SWEATIndex.calculate(
        td850=18,
        tt=52,
        wind850=25,
        wind500=50,
        dir850=170,
        dir500=240,
    )

    assert value > 0


def test_sweat_known_value_all_shear_conditions_met():
    # Manually verified against the documented formula:
    # 12*18 + 20*(52-49) + 2*25 + 50 + 125*(sin(radians(70))+0.2)
    value = SWEATIndex.calculate(td850=18, tt=52, wind850=25, wind500=50, dir850=170, dir500=240)
    expected = 12 * 18 + 20 * (52 - 49) + 2 * 25 + 50 + 125 * (math.sin(math.radians(70)) + 0.2)
    assert value == pytest.approx(expected)


def test_sweat_negative_dewpoint_zeroes_dewpoint_term():
    with_negative_td = SWEATIndex.calculate(td850=-5, tt=52, wind850=25, wind500=50, dir850=170, dir500=240)
    with_zero_td = SWEATIndex.calculate(td850=0, tt=52, wind850=25, wind500=50, dir850=170, dir500=240)
    assert with_negative_td == pytest.approx(with_zero_td)


def test_sweat_tt_below_49_zeroes_tt_term():
    with_low_tt = SWEATIndex.calculate(td850=18, tt=40, wind850=25, wind500=50, dir850=170, dir500=240)
    without_tt_term = 12 * 18 + 0 + 2 * 25 + 50 + 125 * (math.sin(math.radians(70)) + 0.2)
    assert with_low_tt == pytest.approx(without_tt_term)


def test_sweat_shear_term_zeroed_when_direction_out_of_range():
    # dir850 outside [130, 250] -> shear term must be zero.
    value = SWEATIndex.calculate(td850=18, tt=52, wind850=25, wind500=50, dir850=90, dir500=240)
    expected_without_shear = 12 * 18 + 20 * (52 - 49) + 2 * 25 + 50
    assert value == pytest.approx(expected_without_shear)


def test_sweat_shear_term_zeroed_when_wind_speed_below_15kt():
    value = SWEATIndex.calculate(td850=18, tt=52, wind850=10, wind500=50, dir850=170, dir500=240)
    expected_without_shear = 12 * 18 + 20 * (52 - 49) + 2 * 10 + 50
    assert value == pytest.approx(expected_without_shear)


def test_sweat_shear_term_zeroed_when_direction_difference_not_positive():
    value = SWEATIndex.calculate(td850=18, tt=52, wind850=25, wind500=50, dir850=240, dir500=170)
    expected_without_shear = 12 * 18 + 20 * (52 - 49) + 2 * 25 + 50
    assert value == pytest.approx(expected_without_shear)


def test_category():

    assert SWEATIndex.category(100) == "Low"

    assert SWEATIndex.category(250) == "Moderate"

    assert SWEATIndex.category(350) == "High"

    assert SWEATIndex.category(500) == "Extreme"
