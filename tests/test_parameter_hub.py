from acf.parameters.hub import ParameterHub
from acf.parameters.parameter import Parameter


def test_parameter_hub():

    hub = ParameterHub()

    hub.register(
        Parameter(
            code="t2m",
            name="2 metre temperature",
            unit="K",
            standard_name="air_temperature",
            category="Temperature",
        )
    )

    hub.add_alias("T2", "t2m")

    assert hub.exists("t2m")
    assert hub.by_code("t2m").unit == "K"
    assert hub.by_name("2 metre temperature").code == "t2m"
    assert hub.by_alias("T2").code == "t2m"
    assert hub.count() == 1
