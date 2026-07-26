"""
Atmospheric Complexity Framework (ACF)

Mouse Controller
================

Central mouse event controller.
"""

from PySide6.QtCore import QObject, Signal, QPoint


class MouseController(QObject):
    """
    Handles mouse interaction on the map.
    """

    ##################################################

    mouseMoved = Signal(float, float)

    mousePressed = Signal(object)

    mouseReleased = Signal(object)

    mouseDoubleClicked = Signal(object)

    ##################################################

    def __init__(self, parent=None):

        super().__init__(parent)

        self.initialize()

    ##################################################

    def initialize(self):

        self.last_position = QPoint()

        self.left_pressed = False

        self.middle_pressed = False

        self.right_pressed = False

    ##################################################

    def press(self, event):

        self.last_position = event.position().toPoint()

        if event.button() == event.button().LeftButton:

            self.left_pressed = True

        elif event.button() == event.button().MiddleButton:

            self.middle_pressed = True

        elif event.button() == event.button().RightButton:

            self.right_pressed = True

        self.mousePressed.emit(event)

    ##################################################

    def release(self, event):

        self.left_pressed = False

        self.middle_pressed = False

        self.right_pressed = False

        self.mouseReleased.emit(event)

    ##################################################

    def move(self, event):

        self.last_position = event.position().toPoint()

        self.mouseMoved.emit(
            self.last_position.x(),
            self.last_position.y(),
        )

    ##################################################

    def double_click(self, event):

        self.mouseDoubleClicked.emit(event)

    ##################################################

    def position(self):

        return self.last_position

    ##################################################

    def status(self):

        return {

            "left_pressed": self.left_pressed,

            "middle_pressed": self.middle_pressed,

            "right_pressed": self.right_pressed,

            "position": (
                self.last_position.x(),
                self.last_position.y(),
            ),
        }
