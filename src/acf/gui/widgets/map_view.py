"""
ACF Scientific Map View

Cartopy + Matplotlib engine
"""


from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
)


from matplotlib.backends.backend_qtagg import (
    FigureCanvasQTAgg
)


from matplotlib.figure import Figure


import cartopy.crs as ccrs
import cartopy.feature as cfeature



class MapCanvas(FigureCanvasQTAgg):


    def __init__(self):

        self.figure = Figure(
            figsize=(8,6)
        )


        self.ax = self.figure.add_subplot(
            111,
            projection=ccrs.PlateCarree()
        )


        super().__init__(
            self.figure
        )


        self.draw_map()



    ################################################


    def draw_map(self):

        self.ax.clear()



        self.ax.set_global()



        self.ax.add_feature(
            cfeature.LAND
        )


        self.ax.add_feature(
            cfeature.OCEAN
        )


        self.ax.add_feature(
            cfeature.COASTLINE
        )


        self.ax.add_feature(
            cfeature.BORDERS
        )


        self.ax.gridlines()



        self.ax.set_title(
            "ACF Atmospheric Map"
        )


        self.draw()



    ################################################


    def plot_field(
        self,
        longitude,
        latitude,
        values,
        title=""
    ):


        self.ax.clear()



        self.ax.coastlines()



        mesh = self.ax.pcolormesh(
            longitude,
            latitude,
            values,
            transform=ccrs.PlateCarree()
        )


        self.figure.colorbar(
            mesh,
            ax=self.ax
        )



        self.ax.set_title(
            title
        )


        self.draw()






class MapView(QWidget):


    def __init__(self):

        super().__init__()


        self.canvas = None


        self.build()



    ################################################


    def build(self):

        layout = QVBoxLayout(
            self
        )


        layout.setContentsMargins(
            0,0,0,0
        )


        self.canvas = MapCanvas()


        layout.addWidget(
            self.canvas
        )



    ################################################


    def clear(self):

        self.canvas.draw_map()



    ################################################


    def show_message(self,text):

        print(
            text
        )



    ################################################


    def display_dataset(
        self,
        dataset,
        variable
    ):

        """
        Affiche une variable météo.
        """

        data = dataset.get_variable(
            variable
        )


        if data is None:

            return



        try:

            lon = data.coords["longitude"]

            lat = data.coords["latitude"]



            self.canvas.plot_field(
                lon,
                lat,
                data,
                variable
            )


        except Exception as error:

            print(
                error
            )
