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

        if value < 0:
            value = 0

        if value > 1:
            value = 1

        self.opacity = value
