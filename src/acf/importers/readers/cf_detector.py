"""
CF Convention Detector
"""


class CFDetector:
    LATITUDE_NAMES = {
        "lat",
        "latitude",
        "Latitude",
        "LAT",
    }

    LONGITUDE_NAMES = {
        "lon",
        "longitude",
        "Longitude",
        "LON",
    }

    TIME_NAMES = {
        "time",
        "Time",
        "forecast_time",
        "valid_time",
    }

    LEVEL_NAMES = {
        "level",
        "pressure",
        "isobaricInhPa",
        "height",
        "altitude",
    }

    def detect(self, dataset) -> dict:

        result = {
            "latitude": None,
            "longitude": None,
            "time": None,
            "level": None,
        }

        for coord in dataset.coords:
            attrs = dataset[coord].attrs

            axis = attrs.get("axis")

            standard = attrs.get("standard_name")

            if coord in self.LATITUDE_NAMES or standard == "latitude" or axis == "Y":
                result["latitude"] = coord

            if coord in self.LONGITUDE_NAMES or standard == "longitude" or axis == "X":
                result["longitude"] = coord

            if coord in self.TIME_NAMES or standard == "time" or axis == "T":
                result["time"] = coord

            if coord in self.LEVEL_NAMES or axis == "Z":
                result["level"] = coord

        return result
