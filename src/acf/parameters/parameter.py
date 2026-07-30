"""
Atmospheric Complexity Framework (ACF)

PARAMETERS - Parameter (Canonical Definition)
"""

from dataclasses import dataclass, field


@dataclass
class Parameter:
    code: str = ""
    name: str = ""
    unit: str = ""
    standard_name: str = ""
    category: str = ""
    id: str = ""
    units: str = ""
    renderer: str = ""
    colormap: str = ""
    description: str = ""
    alert_levels: dict = field(default_factory=dict)

    def __post_init__(self):
        if not self.id and self.code:
            self.id = self.code
        elif not self.code and self.id:
            self.code = self.id

        if not self.units and self.unit:
            self.units = self.unit
        elif not self.unit and self.units:
            self.unit = self.units
