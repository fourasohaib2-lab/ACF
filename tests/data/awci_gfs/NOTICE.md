Real NOAA/NCEP GFS 0.25° messages (NOAA Open Data Dissemination, public domain), run 2026-09-25 00Z, steps 0, 3
and 6, only the fields AWCI uses, cropped with eccodes to 35-37° N / 2-4° E; the .idx files follow the wgrib2
inventory format with offsets into the cropped files (last line closes the last message). Regenerate with
`.venv/bin/python tools/awci/make_gfs_fixture.py`.
