from acf.parameters.parameter import Parameter


class ParameterCatalog:

    def __init__(self):

        self.parameters = {}

    def register(self, parameter):

        self.parameters[parameter.code] = parameter

    def get(self, code):

        return self.parameters.get(code)

    def exists(self, code):

        return code in self.parameters

    def list_codes(self):

        return sorted(self.parameters.keys())

    def __len__(self):

        return len(self.parameters)
