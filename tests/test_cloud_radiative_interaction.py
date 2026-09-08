from acf.model4d.physics.cloud_radiative_interaction import CloudRadiativeInteractionPhysics


def test_solar_reflection():
    assert CloudRadiativeInteractionPhysics.solar_reflection(1000, 0.5) == 500


def test_solar_absorption():
    assert CloudRadiativeInteractionPhysics.solar_absorption(1000, 0.5) == 500


def test_infrared_trapping():
    assert CloudRadiativeInteractionPhysics.infrared_trapping(400, 0.75) == 300


def test_cloud_radiative_forcing():
    assert CloudRadiativeInteractionPhysics.cloud_radiative_forcing(100, 50) == 150


def test_cloud_temperature_response():
    result = CloudRadiativeInteractionPhysics.cloud_temperature_response(300, 1)
    assert result == 270


def test_outgoing_longwave_balance():
    assert CloudRadiativeInteractionPhysics.outgoing_longwave_balance(400, 100) == 300


def test_zero_albedo():
    assert CloudRadiativeInteractionPhysics.solar_reflection(500, 0) == 0


def test_full_albedo():
    assert CloudRadiativeInteractionPhysics.solar_reflection(500, 1) == 500


def test_no_trapping():
    assert CloudRadiativeInteractionPhysics.infrared_trapping(300, 0) == 0


def test_full_trapping():
    assert CloudRadiativeInteractionPhysics.infrared_trapping(300, 1) == 300
