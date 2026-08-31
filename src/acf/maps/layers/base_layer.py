"""
Base Layer
"""


class BaseLayer:
    def __init__(self, name):

        self.name = name
        self.visible = True
        self.opacity = 1.0

    def show(self):
        self.visible = True

    def hide(self):
        self.visible = False

    def set_opacity(self, value):

        value = float(value)

        value = max(value, 0)

        value = min(value, 1)

        self.opacity = value
