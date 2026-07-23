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
