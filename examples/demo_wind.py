import numpy as np
from PySide6.QtWidgets import QApplication

from acf.maps.canvas.map_canvas import MapCanvas
from acf.maps.renderers.wind_renderer import WindRenderer

app = QApplication([])

canvas = MapCanvas()

renderer = WindRenderer(canvas)

x = np.linspace(-2, 2, 60)
y = np.linspace(-2, 2, 60)

X, Y = np.meshgrid(x, y)

u = -Y
v = X

renderer.render(u, v, stride=3, title="Synthetic Wind Field")

canvas.resize(1200, 800)
canvas.show()

app.exec()
