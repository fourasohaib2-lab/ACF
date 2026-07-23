from acf.core.parameter import Parameter


class ParameterRegistry:

    def __init__(self):

        self.parameters = {}

    ##############################################

    def register(self, parameter):

        self.parameters[parameter.id] = parameter

    ##############################################

    def get(self, parameter_id):

        return self.parameters.get(parameter_id)

    ##############################################

    def exists(self, parameter_id):

        return parameter_id in self.parameters

    ##############################################

    def all(self):

        return list(self.parameters.values())

    ##############################################

    def categories(self):

        return sorted(
            {
                p.category
                for p in self.parameters.values()
            }
        )

    ##############################################

    def by_category(self, category):

        return [

            p

            for p in self.parameters.values()

            if p.category == category

        ]
