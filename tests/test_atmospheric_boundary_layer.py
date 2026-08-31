from acf.model4d.physics.atmospheric_boundary_layer import AtmosphericBoundaryLayerPhysics


def test_sensible_heat_flux():

    result = AtmosphericBoundaryLayerPhysics.calculate_sensible_heat_flux(1.225, 1005, 5, 300, 290)

    assert result > 0


def test_latent_heat_flux():

    result = AtmosphericBoundaryLayerPhysics.calculate_latent_heat_flux(0.0001)

    assert result > 0


def test_momentum_flux():

    result = AtmosphericBoundaryLayerPhysics.calculate_momentum_flux(1.225, 10)

    assert result > 0


def test_mixing_height():

    result = AtmosphericBoundaryLayerPhysics.calculate_mixing_height(300, 290, 5)

    assert result > 100


def test_monin_obukhov():

    result = AtmosphericBoundaryLayerPhysics.calculate_monin_obukhov_length(300, 0.5, 50)

    assert isinstance(result, float)


def test_stability():

    result = AtmosphericBoundaryLayerPhysics.calculate_stability(-100, 10)

    assert result == "unstable"


def test_boundary_status():

    result = AtmosphericBoundaryLayerPhysics.boundary_layer_status(305, 295, 4)

    assert result["regime"] == "convective"


def test_constants():

    assert AtmosphericBoundaryLayerPhysics.AIR_DENSITY > 0


def test_zero_flux():

    result = AtmosphericBoundaryLayerPhysics.calculate_latent_heat_flux(0)

    assert result == 0


def test_neutral_condition():

    result = AtmosphericBoundaryLayerPhysics.boundary_layer_status(300, 300, 3)

    assert result["regime"] == "neutral"
