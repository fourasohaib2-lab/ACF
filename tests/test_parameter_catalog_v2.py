from acf.parameters.catalog import ParameterCatalog
from acf.parameters.parameter import Parameter


def test_catalog():

    catalog = ParameterCatalog()

    catalog.register(
        Parameter(
            code="t2m",
            name="2 metre temperature",
            unit="K",
            standard_name="air_temperature",
            category="Temperature",
        )
    )

    assert catalog.exists("t2m")
    assert catalog.get("t2m").unit == "K"
    assert len(catalog) == 1
