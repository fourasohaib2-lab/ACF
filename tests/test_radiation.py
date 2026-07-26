from acf.model4d.physics.radiation import Radiation


def test_stefan_positive():

    value = Radiation.stefan_boltzmann(
        temperature=300
    )

    assert value > 400


def test_emissivity():

    full = Radiation.stefan_boltzmann(
        300,
        1.0
    )

    half = Radiation.stefan_boltzmann(
        300,
        0.5
    )

    assert half == full / 2


def test_balance_positive():

    assert Radiation.net_balance(
        500,
        300
    ) == 200


def test_balance_negative():

    assert Radiation.net_balance(
        100,
        200
    ) == -100


def test_shortwave():

    assert Radiation.shortwave(
        1000,
        0.2
    ) == 800


def test_longwave():

    assert Radiation.longwave(300) > 400


def test_category_weak():

    assert Radiation.category(20) == "Weak"


def test_category_moderate():

    assert Radiation.category(100) == "Moderate"


def test_category_strong():

    assert Radiation.category(500) == "Strong"


def test_constant():

    assert Radiation.STEFAN_BOLTZMANN > 0
