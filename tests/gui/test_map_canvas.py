from PySide6.QtWidgets import QApplication

from acf.gui.map.map_canvas import MapCanvas


def main():

    app = QApplication([])

    canvas = MapCanvas()

    canvas.initialize()

    canvas.resize(1200, 700)

    canvas.show()

    app.exec()


if __name__ == "__main__":
    main()

