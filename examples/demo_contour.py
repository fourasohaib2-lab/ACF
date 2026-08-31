import numpy as np
from PySide6.QtWidgets import QApplication

from acf.maps.canvas.map_canvas import MapCanvas
from acf.maps.renderers.contour_renderer import ContourRenderer

app = QApplication([])

canvas = MapCanvas()

renderer = ContourRenderer(canvas)

x = np.linspace(-3, 3, 120)
y = np.linspace(-3, 3, 120)

X, Y = np.meshgrid(x, y)

Z = np.sin(X) * np.cos(Y)

renderer.render(Z, cmap="temperature", levels=20, filled=True, title="Temperature Contours", colorbar_label="°C")

canvas.resize(1200, 800)

canvas.show()

app.exec()
