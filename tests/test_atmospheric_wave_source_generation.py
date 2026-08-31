from acf.model4d.physics.atmospheric_wave_source_generation import AtmosphericWaveSourceGeneration, WaveSourceState


def test_creation():

    model = AtmosphericWaveSourceGeneration()

    assert model.version == "8.94"


def test_convection_source():

    model = AtmosphericWaveSourceGeneration()

    state = WaveSourceState(convection_index=20, mountain_height=0, jet_speed=0, frontal_gradient=0, instability=5)

    assert model.convection_source(state) == 100


def test_orographic_source():

    model = AtmosphericWaveSourceGeneration()

    state = WaveSourceState(convection_index=0, mountain_height=2000, jet_speed=100, frontal_gradient=0, instability=1)

    assert model.orographic_source(state) == 200


def test_front_source():

    model = AtmosphericWaveSourceGeneration()

    state = WaveSourceState(convection_index=0, mountain_height=0, jet_speed=0, frontal_gradient=20, instability=10)

    assert model.frontal_source(state) == 200


def test_jet_source():

    model = AtmosphericWaveSourceGeneration()

    state = WaveSourceState(convection_index=0, mountain_height=0, jet_speed=200, frontal_gradient=0, instability=1)

    assert model.jet_source(state) == 400


def test_total_energy():

    model = AtmosphericWaveSourceGeneration()

    state = WaveSourceState(
        convection_index=50, mountain_height=1000, jet_speed=100, frontal_gradient=10, instability=2
    )

    assert model.total_source_energy(state) == 100


def test_classification():

    model = AtmosphericWaveSourceGeneration()

    state = WaveSourceState(convection_index=200, mountain_height=0, jet_speed=0, frontal_gradient=0, instability=5)

    assert model.classify_source(state) == "Strong wave source"


def test_simulation():

    model = AtmosphericWaveSourceGeneration()

    state = WaveSourceState(convection_index=10, mountain_height=500, jet_speed=50, frontal_gradient=5, instability=3)

    result = model.simulate(state)

    assert "energy" in result


def test_jet_type():

    model = AtmosphericWaveSourceGeneration()

    state = WaveSourceState(
        convection_index=0, mountain_height=0, jet_speed=100, frontal_gradient=0, instability=1, source_type="jet"
    )

    assert model.total_source_energy(state) == 100


def test_name():

    model = AtmosphericWaveSourceGeneration()

    assert model.name == "Atmospheric Wave Source Generation"
