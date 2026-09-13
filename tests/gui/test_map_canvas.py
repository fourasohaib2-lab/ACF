import os

import pytest
from PySide6.QtWidgets import QApplication

from acf.gui.map.map_canvas import MapCanvas

os.environ["QT_QPA_PLATFORM"] = "offscreen"


@pytest.fixture(scope="module")
def qapp():
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


def test_zoom_reset_buttons_have_a_real_accessible_name(qapp):
    """The zoom in (+), zoom out (−), and reset view (⤢) buttons show no
    visible text at all - same icon-only accessibility gap already
    closed for AWCIMapPanel's own equivalent zoom stack (2026-09-13
    master-prompt v4 gap audit), extended here to this base map widget
    (used by MainWindow and every ESOC view built on it)."""
    canvas = MapCanvas()

    assert canvas.zoom_in_button.accessibleName() == "Zoom in"
    assert canvas.zoom_out_button.accessibleName() == "Zoom out"
    assert canvas.reset_view_button.accessibleName() == "Reset view"
    assert canvas.reset_view_button.accessibleDescription() == canvas.reset_view_button.toolTip()
    canvas.close()


def test_map_canvas_initialization(qapp):
    canvas = MapCanvas()
    assert canvas is not None
    assert canvas.figure is not None
    canvas.resize(1200, 700)
    assert canvas.width() >= 0
    qapp.processEvents()
    canvas.close()
    qapp.processEvents()


def main():
    app = QApplication([])
    canvas = MapCanvas()
    canvas.resize(1200, 700)
    canvas.show()
    app.exec()


if __name__ == "__main__":
    main()
