# Front test data

Real API responses, not hand-written: `airport_daag.json`, `airports_0300.json`, `verification_fixture.json`
come from the AWCI API over the cropped IFS fixture (`tests/data/awci_ops`, © ECMWF CC-BY-4.0) and the
recorded AWC observations of `tests/data/awc` (public domain); `sigmets_real.json` holds real international
SIGMETs of 2026-09-26 (AWC); `verification_north_africa_2026092512.json` is the verification of the real
IFS 2026-09-25 12Z run over North Africa against 12 531 METAR (+0..+21 h observed at the time).
`ens_point_fixture.json` and `ens_meta_fixture.json` come from `/ens/point` and `/ens/meta` over the real 4-member IFS ENS
fixture (`tests/data/awci_ens`, © ECMWF CC-BY-4.0).
