from acf.standards.hub import StandardsHub


def test_hub():

    hub = StandardsHub()

    hub.register("cf", object())

    assert hub.exists("cf")
    assert hub.count() == 1
