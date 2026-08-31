from acf.model4d.physics.atmospheric_radiation import AtmosphericRadiationPhysics


def test_stefan_boltzmann_flux():

    value = AtmosphericRadiationPhysics.stefan_boltzmann_flux(300)

    assert round(value, 2) == 459.3


def test_net_radiative_flux():

    value = AtmosphericRadiationPhysics.net_radiative_flux(500, 300)

    assert value == 200


def test_effective_temperature():

    value = AtmosphericRadiationPhysics.effective_temperature(459.3)

    assert round(value, 0) == 300


def test_greenhouse_forcing():

    value = AtmosphericRadiationPhysics.greenhouse_forcing(400, 250)

    assert value == 150


def test_blackbody_emission():

    value = AtmosphericRadiationPhysics.blackbody_emission(300, 1)

    assert round(value, 2) == 459.3


def test_absorption():

    value = AtmosphericRadiationPhysics.atmospheric_absorption(100, 0.5)

    assert value == 50


def test_optical_depth():

    value = AtmosphericRadiationPhysics.optical_depth(0.2, 10)

    assert value == 2


def test_equilibrium():

    value = AtmosphericRadiationPhysics.radiative_equilibrium(300, 300)

    assert value == 0


def test_olr():

    value = AtmosphericRadiationPhysics.outgoing_longwave_radiation(300)

    assert round(value, 2) == 459.3


def test_constant():

    assert AtmosphericRadiationPhysics.STEFAN_BOLTZMANN > 0
