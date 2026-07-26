"""
Atmospheric Complexity Framework (ACF)

Pan Controller
==============

Handles map dragging.
"""

from PySide6.QtCore import QObject, Signal, QPoint


class PanController(QObject):
    """
    Professional map pan controller.
    """

    ##################################################

    panStarted = Signal()

    panMoved = Signal(float, float)

    panFinished = Signal()

    ##################################################

    def __init__(self, parent=None):

        super().__init__(parent)

        self.initialize()

    ##################################################

    def initialize(self):

        self.dragging = False

        self.last_position = QPoint()

    ##################################################

    def start(self, point):

        self.dragging = True

        self.last_position = point

        self.panStarted.emit()

    ##################################################

    def move(self, point):

        if not self.dragging:
            return

        dx = point.x() - self.last_position.x()

        dy = point.y() - self.last_position.y()

        self.last_position = point

        self.panMoved.emit(dx, dy)

    ##################################################

    def stop(self):

        if not self.dragging:
            return

        self.dragging = False

        self.panFinished.emit()

    ##################################################

    def status(self):

        return {

            "dragging": self.dragging,

            "position": (
                self.last_position.x(),
                self.last_position.y(),
            ),

        }
