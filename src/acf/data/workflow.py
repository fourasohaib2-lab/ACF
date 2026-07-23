"""
ACF Workflow Engine
"""


class Workflow:

    def __init__(self, name):

        self.name = name
        self.steps = []

    def add_step(self, name, function):

        self.steps.append(
            {
                "name": name,
                "function": function,
            }
        )

    def run(self, dataset):

        current = dataset

        for step in self.steps:

            current = step["function"](current)

        return current

    def list_steps(self):

        return [step["name"] for step in self.steps]

    def clear(self):

        self.steps.clear()

    def __len__(self):

        return len(self.steps)
