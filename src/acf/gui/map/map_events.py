"""
Atmospheric Complexity Framework (ACF)

Map Events
==========

Mouse and keyboard interaction mixin.
"""

from PySide6.QtCore import Qt


class EventMixin:
    ##################################################
    # Mouse
    ##################################################

    def mousePressEvent(self, event):

        self._last_mouse_position = event.position()

        super().mousePressEvent(event)

    ##################################################

    def mouseMoveEvent(self, event):

        if not hasattr(self, "_last_mouse_position"):
            self._last_mouse_position = event.position()

            return

        if event.buttons() & Qt.LeftButton:
            dx = event.position().x() - self._last_mouse_position.x()

            dy = event.position().y() - self._last_mouse_position.y()

            self.pan(
                -dx * 0.2,
                dy * 0.2,
            )

        self._last_mouse_position = event.position()

        super().mouseMoveEvent(event)

    ##################################################

    def mouseReleaseEvent(self, event):

        self._last_mouse_position = event.position()

        super().mouseReleaseEvent(event)

    ##################################################
    # Wheel
    ##################################################

    def wheelEvent(self, event):

        delta = event.angleDelta().y()

        if delta > 0:
            self.zoom_in()

        else:
            self.zoom_out()

        super().wheelEvent(event)

    ##################################################
    # Double Click
    ##################################################

    def mouseDoubleClickEvent(self, event):

        self.reset_view()

        super().mouseDoubleClickEvent(event)

    ##################################################
    # Keyboard
    ##################################################

    def keyPressEvent(self, event):

        key = event.key()

        if key == Qt.Key_Left:
            self.pan_left()

        elif key == Qt.Key_Right:
            self.pan_right()

        elif key == Qt.Key_Up:
            self.pan_up()

        elif key == Qt.Key_Down:
            self.pan_down()

        elif key in (Qt.Key_Plus, Qt.Key_Equal):
            self.zoom_in()

        elif key == Qt.Key_Minus:
            self.zoom_out()

        elif key == Qt.Key_Home:
            self.reset_view()

        super().keyPressEvent(event)
