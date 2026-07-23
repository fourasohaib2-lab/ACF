from acf.validation.rule import ValidationRule
from acf.validation.validator import ParameterValidator


def create_validator():

    validator = ParameterValidator()

    validator.register(
        ValidationRule(
            parameter="t2m",
            minimum=180,
            maximum=340,
            units="K"
        )
    )

    validator.register(
        ValidationRule(
            parameter="rh",
            minimum=0,
            maximum=100,
            units="%"
        )
    )

    validator.register(
        ValidationRule(
            parameter="mslp",
            minimum=85000,
            maximum=110000,
            units="Pa"
        )
    )

    validator.register(
        ValidationRule(
            parameter="wind_speed",
            minimum=0,
            maximum=150,
            units="m s-1"
        )
    )

    validator.register(
        ValidationRule(
            parameter="tp",
            minimum=0,
            maximum=5000,
            units="mm"
        )
    )

    return validator
