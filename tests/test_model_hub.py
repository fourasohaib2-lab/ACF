from acf.models.hub import ModelHub


def test_model_hub():

    hub = ModelHub()

    assert hub.has_model("ERA5")

    assert hub.count() >= 1
