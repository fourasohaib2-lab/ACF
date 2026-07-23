"""
CF Convention Detector
"""

from typing import Dict


class CFDetector:

    LATITUDE_NAMES = {
        "lat",
        "latitude",
        "Latitude",
        "LAT"
    }

    LONGITUDE_NAMES = {
        "lon",
        "longitude",
        "Longitude",
        "LON"
    }

    TIME_NAMES = {
        "time",
        "Time",
        "forecast_time",
        "valid_time"
    }

    LEVEL_NAMES = {
        "level",
        "pressure",
        "isobaricInhPa",
        "height",
        "altitude"
    }

    def detect(self, dataset) -> Dict:

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

            if coord in self.LATITUDE_NAMES:
                result["latitude"] = coord

            elif standard == "latitude":
                result["latitude"] = coord

            elif axis == "Y":
                result["latitude"] = coord

            if coord in self.LONGITUDE_NAMES:
                result["longitude"] = coord

            elif standard == "longitude":
                result["longitude"] = coord

            elif axis == "X":
                result["longitude"] = coord

            if coord in self.TIME_NAMES:
                result["time"] = coord

            elif standard == "time":
                result["time"] = coord

            elif axis == "T":
                result["time"] = coord

            if coord in self.LEVEL_NAMES:
                result["level"] = coord

            elif axis == "Z":
                result["level"] = coord

        return result
