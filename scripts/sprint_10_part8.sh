#!/usr/bin/env bash

set -e

PROJECT="$HOME/ACF"

echo "=========================================="
echo " ACF Sprint 10 - Partie 8"
echo " Scientific Parameter Validator"
echo "=========================================="

mkdir -p "$PROJECT/src/acf/validation"

touch "$PROJECT/src/acf/validation/__init__.py"

####################################################
# VALIDATION RULE
####################################################

cat > "$PROJECT/src/acf/validation/rule.py" << 'EOF'
from dataclasses import dataclass


@dataclass(slots=True)
class ValidationRule:

    parameter: str

    minimum: float | None = None

    maximum: float | None = None

    units: str = ""
EOF

####################################################
# VALIDATOR
####################################################

cat > "$PROJECT/src/acf/validation/validator.py" << 'EOF'
from acf.validation.rule import ValidationRule


class ParameterValidator:

    def __init__(self):

        self.rules = {}

    ####################################

    def register(self, rule: ValidationRule):

        self.rules[rule.parameter] = rule

    ####################################

    def validate(self, parameter, value):

        rule = self.rules.get(parameter)

        if rule is None:
            return True

        if value is None:
            return False

        if rule.minimum is not None and value < rule.minimum:
            return False

        if rule.maximum is not None and value > rule.maximum:
            return False

        return True
EOF

####################################################
# DEFAULT RULES
####################################################

cat > "$PROJECT/src/acf/validation/default_rules.py" << 'EOF'
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
EOF

####################################################
# TESTS
####################################################

cat > "$PROJECT/tests/test_validator.py" << 'EOF'
from acf.validation.default_rules import create_validator


def test_temperature():

    v = create_validator()

    assert v.validate("t2m", 295)
    assert not v.validate("t2m", 500)


def test_humidity():

    v = create_validator()

    assert v.validate("rh", 60)
    assert not v.validate("rh", 130)


def test_pressure():

    v = create_validator()

    assert v.validate("mslp", 101325)
    assert not v.validate("mslp", 60000)


def test_unknown():

    v = create_validator()

    assert v.validate("abcdef", 999)
EOF

echo
echo "Scientific Validator installed successfully."
