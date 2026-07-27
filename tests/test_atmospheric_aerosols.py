from acf.model4d.physics.atmospheric_aerosols import AtmosphericAerosolsPhysics


def test_optical_depth():

    value = AtmosphericAerosolsPhysics.aerosol_optical_depth(
        0.5,
        2
    )

    assert value == 1


def test_settling_velocity():

    value = AtmosphericAerosolsPhysics.particle_settling_velocity(
        1e-6,
        2000,
        1.2
    )

    assert round(value, 8) == 0.000266


def test_number_density():

    value = AtmosphericAerosolsPhysics.aerosol_number_density(
        1000,
        10
    )

    assert value == 100


def test_mass_concentration():

    value = AtmosphericAerosolsPhysics.aerosol_mass_concentration(
        20,
        10
    )

    assert value == 2


def test_growth_factor():

    value = AtmosphericAerosolsPhysics.hygroscopic_growth_factor(
        1,
        1.5
    )

    assert value == 1.5


def test_angstrom():

    value = AtmosphericAerosolsPhysics.angstrom_exponent(
        0.5,
        0.3,
        440,
        870
    )

    assert round(value, 3) == 0.605


def test_radiative_forcing():

    value = AtmosphericAerosolsPhysics.radiative_forcing(
        0.5,
        20
    )

    assert value == -10


def test_lifetime():

    value = AtmosphericAerosolsPhysics.aerosol_lifetime(
        100,
        5
    )

    assert value == 20


def test_deposition_flux():

    value = AtmosphericAerosolsPhysics.deposition_flux(
        10,
        0.2
    )

    assert value == 2


def test_surface_area():

    value = AtmosphericAerosolsPhysics.aerosol_surface_area(
        100,
        0.01
    )

    assert round(value, 5) == 0.12566
