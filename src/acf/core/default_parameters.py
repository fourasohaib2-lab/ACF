from acf.core.parameter import Parameter
from acf.core.parameter_registry import ParameterRegistry


def create_registry():

    registry = ParameterRegistry()

    registry.register(
        Parameter(
            id="t2m",
            name="2 m Temperature",
            units="°C",
            category="Surface",
            renderer="Raster",
            colormap="temperature",
            description="Air temperature at 2 metres"
        )
    )

    registry.register(
        Parameter(
            id="rh",
            name="Relative Humidity",
            units="%",
            category="Surface",
            renderer="Raster",
            colormap="humidity"
        )
    )

    registry.register(
        Parameter(
            id="mslp",
            name="Mean Sea Level Pressure",
            units="hPa",
            category="Surface",
            renderer="Contour",
            colormap="pressure"
        )
    )

    registry.register(
        Parameter(
            id="u10",
            name="10 m U Wind",
            units="m/s",
            category="Wind",
            renderer="Wind",
            colormap="wind"
        )
    )

    registry.register(
        Parameter(
            id="v10",
            name="10 m V Wind",
            units="m/s",
            category="Wind",
            renderer="Wind",
            colormap="wind"
        )
    )

    return registry
