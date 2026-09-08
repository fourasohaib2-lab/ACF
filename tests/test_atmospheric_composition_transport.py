import pytest

from acf.model4d.physics.atmospheric_composition_transport import AtmosphericCompositionTransportPhysics


def test_advection():

    assert AtmosphericCompositionTransportPhysics.advective_transport(400, 10, 2) == 20


def test_diffusion():

    assert AtmosphericCompositionTransportPhysics.turbulent_diffusion(5, 4) == 20


def test_vertical_mixing():

    assert AtmosphericCompositionTransportPhysics.vertical_mixing(100, 0.5) == 50


def test_chemical_lifetime():

    assert AtmosphericCompositionTransportPhysics.chemical_lifetime_transport(200, 0.25) == 50


def test_greenhouse_loading():

    assert AtmosphericCompositionTransportPhysics.greenhouse_gas_loading(400, 2, 1) == 403


def test_aerosol_gas():

    assert AtmosphericCompositionTransportPhysics.aerosol_gas_interaction(10, 5) == 50


def test_status():

    result = AtmosphericCompositionTransportPhysics.transport_status()

    assert result["status"] == "active"


def test_negative_concentration():

    with pytest.raises(ValueError):
        AtmosphericCompositionTransportPhysics.advective_transport(-1, 10, 2)


def test_negative_diffusion():

    with pytest.raises(ValueError):
        AtmosphericCompositionTransportPhysics.turbulent_diffusion(-1, 2)


def test_negative_gas():

    with pytest.raises(ValueError):
        AtmosphericCompositionTransportPhysics.greenhouse_gas_loading(-1, 2, 3)
