# AWCI ops test fixture

Real ECMWF IFS 0.25° Open Data (run 2026-09-25 00Z, steps 0 h and 3 h), the
115 messages AWCI Web ingests (SP1 + SP1C), cropped with eccodes to 35–37°N / 2–4°E (9×9).
Regenerate with `tools/awci/make_ops_fixture.py`.

Source: https://data.ecmwf.int/forecasts/ — © ECMWF, licensed CC-BY-4.0
(https://creativecommons.org/licenses/by/4.0/). Values are unmodified apart
from the spatial crop.
