from acf.standards.manager import StandardsManager


def test_manager():

    manager = StandardsManager()

    assert manager.exists_cf("air_temperature")

    assert manager.get_cf("air_temperature")["unit"] == "K"

    assert manager.count_cf() > 0

    assert "air_temperature" in manager.list_cf()
