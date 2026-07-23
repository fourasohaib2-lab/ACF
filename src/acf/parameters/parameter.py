from dataclasses import dataclass


@dataclass
class Parameter:

    code: str
    name: str
    unit: str
    standard_name: str
    category: str
