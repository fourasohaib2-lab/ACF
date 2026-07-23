from acf.validation.default_rules import create_validator


def test_temperature():

    v = create_validator()

    assert v.validate("t2m", 295)
    assert not v.validate("t2m", 500)


def test_humidity():

    v = create_validator()

    assert v.validate("rh", 60)
    assert not v.validate("rh", 130)


def test_pressure():

    v = create_validator()

    assert v.validate("mslp", 101325)
    assert not v.validate("mslp", 60000)


def test_unknown():

    v = create_validator()

    assert v.validate("abcdef", 999)
