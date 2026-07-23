from acf.parameters.index import ParameterIndex
from acf.parameters.parameter import Parameter


def test_parameter_index():

    index = ParameterIndex()

    parameter = Parameter(
        code="t2m",
        name="2 metre temperature",
        unit="K",
        standard_name="air_temperature",
        category="Temperature",
    )

    index.add(parameter)

    assert index.exists("t2m")
    assert index.by_code("t2m").unit == "K"
    assert index.by_name("2 metre temperature").code == "t2m"
    assert index.count() == 1
