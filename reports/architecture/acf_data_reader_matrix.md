# MATRICE DES LECTEURS ET FORMATS DE DONNÉES ACF (ACF-DATA-001)

**Role :** Chief Data Architect & Chief NWP Architect  
**Date :** 3 août 2026  
**Dépôt :** Atmospheric Complexity Framework (ACF)  

---

## Matrice Comparative des Lecteurs et Formats Supportés

| Format | Extensions | Lecteur ACF Canonique | Bibliothèque Backend | Support `Dataset` ACF |
| :--- | :--- | :--- | :--- | :---: |
| **FA** | `.fa`, `.fa.gz` | `EPyGrAMReader` | `epygram` (Météo-France) | **100%** |
| **LFA** | `.lfa` | `EPyGrAMReader` | `epygram` (Météo-France) | **100%** |
| **LFI** | `.lfi` | `EPyGrAMReader` | `epygram` (Météo-France) | **100%** |
| **GRIB1** | `.grib`, `.grb`, `.grib1` | `GRIBReader` / `EPyGrAMReader` | `xarray` + `cfgrib` / `eccodes` | **100%** |
| **GRIB2** | `.grib2`, `.grb2` | `GRIBReader` / `EPyGrAMReader` | `xarray` + `cfgrib` / `eccodes` | **100%** |
| **BUFR** | `.bufr`, `.buf` | `BufrReader` | `eccodes` | **100%** |
| **NetCDF3/4**| `.nc`, `.netcdf`, `.nc4` | `NetCDFReader` / `EPyGrAMReader`| `xarray` + `netCDF4` | **100%** |
| **HDF5** | `.h5`, `.hdf5`, `.he5` | `HDF5Adapter` / `NetCDFReader` | `h5py` / `netCDF4` | **100%** |
| **Zarr** | `.zarr` | `ZarrWriter` / `NetCDFReader` | `xarray` + `zarr` | **100%** |
| **GeoTIFF** | `.tif`, `.tiff`, `.cog` | `GeoTIFFReader` / `GeoTIFFAdapter` | `rasterio` / `gdal` / `PIL` | **100%** |
| **CSV** | `.csv`, `.tsv` | `CSVReader` / `CSVAdapter` | `pandas` / `numpy` | **100%** |
| **JSON** | `.json`, `.geojson` | `JSONReader` / `JSONAdapter` | `json` | **100%** |
| **XML** | `.xml`, `.kml` | `XMLAdapter` | `xml.etree.ElementTree` | **100%** |
| **Parquet** | `.parquet`, `.pq` | `DatasetMapper` | `pyarrow` / `fastparquet` | **100%** |
| **Arrow** | `.arrow`, `.ipc` | `DatasetMapper` | `pyarrow` | **100%** |
