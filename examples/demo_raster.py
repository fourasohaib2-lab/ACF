import numpy as np

from PySide6.QtWidgets import QApplication

from acf.maps.canvas.map_canvas import MapCanvas
from acf.maps.renderers.raster_renderer import RasterRenderer

app = QApplication([])

canvas = MapCanvas()

renderer = RasterRenderer(canvas)

data = np.random.rand(100, 150) * 40 - 10

renderer.render(
    data,
    cmap="temperature",
    title="Demo Temperature",
    colorbar_label="°C"
)

canvas.resize(1200, 800)
canvas.show()

app.exec()

