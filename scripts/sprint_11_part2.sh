#!/usr/bin/env bash

set -e

PROJECT="$HOME/ACF"

mkdir -p "$PROJECT/src/acf/io/readers"

cat > "$PROJECT/src/acf/io/readers/netcdf_reader.py" << 'EOF'
from pathlib import Path

import xarray as xr

from acf.catalog.default_mapping import create_default_mapper
from acf.io.base_reader import BaseReader


class NetCDFReader(BaseReader):

    extensions = [".nc", ".nc4", ".cdf"]

    def __init__(self):
        self.mapper = create_default_mapper()

    def can_read(self, filename: str) -> bool:
        suffix = Path(filename).suffix.lower()
        return suffix in self.extensions

    def read(self, filename: str):

        ds = xr.open_dataset(filename)

        info = {

            "path": filename,

            "dimensions": dict(ds.sizes),

            "variables": [],

            "global_attributes": dict(ds.attrs),

            "coordinates": list(ds.coords),

        }

        for name, variable in ds.variables.items():

            info["variables"].append({

                "original_name": name,

                "acf_name": self.mapper.resolve(name),

                "dimensions": list(variable.dims),

                "shape": list(variable.shape),

                "dtype": str(variable.dtype),

                "units": variable.attrs.get("units"),

                "standard_name": variable.attrs.get("standard_name"),

                "long_name": variable.attrs.get("long_name"),

            })

        ds.close()

        return info
EOF
