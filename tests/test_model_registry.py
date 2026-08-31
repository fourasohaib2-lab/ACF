from acf.models.registry import ModelRegistry


class DummyModel:
    name = "ERA5"


def test_registry():

    registry = ModelRegistry()

    model = DummyModel()

    registry.register(model)

    assert registry.exists("ERA5")

    assert registry.get("ERA5") == model

    assert len(registry) == 1
