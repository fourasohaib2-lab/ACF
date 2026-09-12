"""
Regression tests for acf.standards.{grib2_tables,ecmwf_parameters,
noaa_parameters} - real content added 2026-09-12, replacing generic
auto-generated boilerplate that had zero actual tables (verified dead
via grep before this fix; see grib2_tables.py's own module docstring).
"""

from acf.standards.ecmwf_parameters import ECMWF_PARAMETERS, get_ecmwf_parameter
from acf.standards.grib2_tables import GRIB2_PARAMETERS, get_grib2_parameter
from acf.standards.noaa_parameters import NOAA_PARAMETERS, get_noaa_parameter


def test_grib2_air_temperature_is_the_real_wmo_table_4_2_0_0_identifier():
    param = get_grib2_parameter("air_temperature")
    assert param is not None
    assert (param.discipline, param.parameter_category, param.parameter_number) == (0, 0, 0)
    assert param.abbreviation == "t"
    assert param.unit == "K"


def test_grib2_wind_components_are_category_2_momentum():
    u = get_grib2_parameter("eastward_wind")
    v = get_grib2_parameter("northward_wind")
    assert u is not None and v is not None
    assert u.parameter_category == v.parameter_category == 2


def test_grib2_covers_every_cf_standard_name_this_codebase_already_has():
    from acf.standards.cf_standard_names import CF_STANDARD_NAMES

    for name in CF_STANDARD_NAMES:
        assert name in GRIB2_PARAMETERS, f"{name!r} has a CF standard name but no GRIB2 identifier"


def test_grib2_unknown_name_returns_none_not_a_guess():
    assert get_grib2_parameter("not_a_real_cf_name") is None


def test_ecmwf_air_temperature_is_the_real_param_128_130():
    param = get_ecmwf_parameter("air_temperature")
    assert param is not None
    assert param.param_id == 130
    assert param.short_name == "t"


def test_ecmwf_covers_every_cf_standard_name_this_codebase_already_has():
    from acf.standards.cf_standard_names import CF_STANDARD_NAMES

    for name in CF_STANDARD_NAMES:
        assert name in ECMWF_PARAMETERS, f"{name!r} has a CF standard name but no ECMWF paramId"


def test_noaa_air_temperature_is_the_real_ncep_table_2_parameter_11():
    param = get_noaa_parameter("air_temperature")
    assert param is not None
    assert param.parameter_number == 11
    assert param.abbreviation == "TMP"


def test_noaa_covers_every_cf_standard_name_this_codebase_already_has():
    from acf.standards.cf_standard_names import CF_STANDARD_NAMES

    for name in CF_STANDARD_NAMES:
        assert name in NOAA_PARAMETERS, f"{name!r} has a CF standard name but no NOAA/NCEP parameter number"
