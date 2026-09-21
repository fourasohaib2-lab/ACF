from acf.model4d.physics.atmospheric_thermodynamics import AtmosphericThermodynamicsPhysics


def test_potential_temperature():
    """
    CORRECTED: the source used to add an unexplained "+ 0.47 ACF
    reference calibration" after the correct, standard Poisson
    equation, solely to make this assertion equal 309.65. The honest
    value is 309.18.
    """
    value = AtmosphericThermodynamicsPhysics.potential_temperature(300, 90000)

    assert round(value, 2) == 309.18


def test_virtual_temperature():

    value = AtmosphericThermodynamicsPhysics.virtual_temperature(300, 0.01)

    assert round(value, 2) == 301.83


def test_internal_energy():

    value = AtmosphericThermodynamicsPhysics.internal_energy(300, 2)

    assert value == 430.2


def test_enthalpy():

    value = AtmosphericThermodynamicsPhysics.enthalpy(300, 2)

    assert value == 602.4


def test_static_stability():

    value = AtmosphericThermodynamicsPhysics.static_stability(6, 9.8)

    assert value == 3.8


def test_dry_lapse_rate():

    value = AtmosphericThermodynamicsPhysics.dry_adiabatic_lapse_rate()

    assert value == 9.8


def test_moist_lapse_rate():

    value = AtmosphericThermodynamicsPhysics.moist_adiabatic_lapse_rate(293)

    assert round(value, 2) == 5.2


def test_lcl_temperature():
    """
    CORRECTED: the source used to return a fixed "Td - 3.33" offset
    that ignored the actual temperature/dewpoint spread. The physically
    consistent value (T cooling at the dry adiabatic lapse rate up to
    z_LCL = 125*(T-Td) = 1250 m, matching lcl_height() below) is
    300 - (9.8/1000)*1250 = 287.75, close to the Bolton (1980) eq. 22
    reference value of ~287.7 K.
    """

    value = AtmosphericThermodynamicsPhysics.lcl_temperature(300, 290)

    assert round(value, 2) == 287.75


def test_lcl_height():

    value = AtmosphericThermodynamicsPhysics.lcl_height(300, 290)

    assert value == 1250


def test_lfc_height():

    value = AtmosphericThermodynamicsPhysics.lfc_height(1000, 2)

    assert value == 1200
