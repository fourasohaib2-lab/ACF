"""
ECMWF Parameter Converter
"""

from acf.parameters.parameter import Parameter


class ECMWFConverter:

    def convert(self, code, data):

        return Parameter(
            code=code,
            name=data["name"],
            unit=data["unit"],
            standard_name=data["standard_name"],
            category=data["category"],
        )
