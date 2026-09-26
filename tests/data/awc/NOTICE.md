# Aviation Weather Center responses (test fixtures)

Real responses of the NOAA/NWS Aviation Weather Center Data API (https://aviationweather.gov/data/api/),
recorded on 2026-09-26 around 08:45 UTC by ACF for the AWCI Web SP3 tests. Works of the US Government:
public domain. Content is unchanged apart from field selection (`metar_corpus_*`) and time/station
filtering.

| File | Request |
|---|---|
| `metar_corpus_20260926T08.json` | `metar?bbox=15,-20,45,40&hours=2&format=json` (400 items, the API cap), fields icaoId, obsTime, rawOb, clouds, fltCat, visib, metarType, lat, lon, elev, name |
| `metar_daag_20260925.json` | `metar?bbox=35,2,37,4&hours=168&format=json`, kept 2026-09-24T21Z..2026-09-25T14Z (DAAG, Alger) |
| `taf_sample_20260926T08.json` | `taf?bbox=15,-20,45,40&format=json`, stations DAAG, GMMN, LEMD, DTTA, HECA |
| `isigmet_20260926T08.json` | `isigmet?format=json` (worldwide, 126 SIGMET incl. 10 VA) |
| `stations_north_africa.json` | `stationinfo?bbox=` tiled 10x10 deg over 15-45N / 20W-40E, METAR sites only (557) |
