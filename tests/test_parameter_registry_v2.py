from acf.parameters.parameter import Parameter
from acf.parameters.registry import ParameterRegistry


def test_registry():

    registry = ParameterRegistry()

    parameter = Parameter(
        code="t2m",
        name="2 metre temperature",
        unit="K",
        standard_name="air_temperature",
        category="Temperature",
    )

    registry.register(parameter)

    assert registry.exists("t2m")
    assert registry.count() == 1
    assert registry.get("t2m").name == "2 metre temperature"
