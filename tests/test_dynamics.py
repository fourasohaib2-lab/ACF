from acf.science.dynamics import Dynamics


def test_available():

    modules = Dynamics.available()

    assert "vorticity" in modules
    assert "divergence" in modules
    assert "frontogenesis" in modules
    assert "potential_vorticity" in modules
