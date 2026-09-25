# AWCI ops wet test fixture

Real ECMWF IFS 0.25° Open Data (run 2026-09-25 00Z, steps 0 h and 3 h), the
115 messages AWCI Web ingests, cropped with eccodes to 15–17°N / 20–18°W (9×9):
tropical Atlantic off Senegal, chosen because it is the 2°×2° box of the
`north_africa` domain with the most widespread precipitation at +3 h
(tprate up to 28.8 mm/h, every cell > 0.1 mm/h, mucape up to 1260 J/kg).
It exercises precipitating genera (Ns, Cu, Cb), convection and ptype.
Regenerate with
`tools/awci/make_ops_fixture.py --box 15 17 -20 -18 --out tests/data/awci_ops_wet`.

Source: https://data.ecmwf.int/forecasts/ — © ECMWF, licensed CC-BY-4.0
(https://creativecommons.org/licenses/by/4.0/). Values are unmodified apart
from the spatial crop.
