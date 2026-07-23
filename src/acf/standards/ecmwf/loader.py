"""
ECMWF JSON Loader
"""

import json
from pathlib import Path


class ECMWFLoader:

    def load(self, filename):

        filename = Path(filename)

        with filename.open("r", encoding="utf-8") as f:

            return json.load(f)
