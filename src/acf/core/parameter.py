from dataclasses import dataclass, field


@dataclass(slots=True)
class Parameter:

    id: str

    name: str

    units: str

    category: str

    renderer: str

    colormap: str

    description: str = ""

    alert_levels: dict = field(default_factory=dict)
