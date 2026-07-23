from acf.core.environment import operating_system

def test_operating_system():
    assert isinstance(operating_system(), str)
