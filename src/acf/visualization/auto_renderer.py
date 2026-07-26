"""
Atmospheric Complexity Framework (ACF)

Automatic Weather Visualization Engine
"""

from acf.visualization.data_renderer import DataRenderer


class AutoRenderer:
    """
    Automatic scientific renderer.

    Choisit automatiquement :
      - la variable
      - la couche
      - la colormap
    """

    DEFAULT_VARIABLES = {
        "temperature": [
            "temperature",
            "t2m",
            "tmp",
            "temp",
        ],
        "pressure": [
            "pressure",
            "mslp",
            "slp",
            "pres",
        ],
        "wind": [
            "wind",
            "u10",
            "v10",
            "u",
            "v",
        ],
        "humidity": [
            "humidity",
            "rh",
            "relative_humidity",
        ],
        "precipitation": [
            "precipitation",
            "rain",
            "tp",
            "precip",
        ],
    }

    def __init__(self):

        self.renderer = DataRenderer()

    ##################################################

    def initialize(self):

        return self.renderer.initialize_map()

    ##################################################

    def detect_variable(
        self,
        dataset,
        family,
    ):

        if family not in self.DEFAULT_VARIABLES:
            return None

        names = dataset.variable_names

        for candidate in self.DEFAULT_VARIABLES[family]:

            for variable in names:

                if candidate.lower() in variable.lower():

                    return variable

        return None

    ##################################################

    def render_dataset(
        self,
        dataset,
        family,
        longitude,
        latitude,
        values,
    ):

        variable = self.detect_variable(
            dataset,
            family,
        )

        if variable is None:

            raise ValueError(
                f"No variable found for '{family}'."
            )

        self.renderer.create_layer(
            dataset,
            variable,
        )

        self.renderer.render(
            longitude,
            latitude,
            values,
            variable,
        )

        return variable

    ##################################################

    def available_families(self):

        return sorted(
            self.DEFAULT_VARIABLES.keys()
        )

    ##################################################

    def status(self):

        return {

            "families":
                self.available_families(),

            "renderer":
                self.renderer.status(),

        }
