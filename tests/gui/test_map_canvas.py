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
