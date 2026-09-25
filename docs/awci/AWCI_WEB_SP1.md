# AWCI Web — SP1 (données & science) : guide d'exploitation

Spec : `docs/superpowers/specs/2026-09-25-awci-web-sp1-data-science-design.md`.
Code : `src/acf/awci/ops/` (ingestion, diagnostics, moteur, stockage) et
`src/acf/web/awci_router.py` (API). Le desktop Qt n'est pas concerné.

## Installation

```bash
pip install -e ".[formats,web,science]"   # eccodes, netCDF4/xarray, fastapi/uvicorn
```

`acf-awci-web` n'importe ni `paramiko` ni `torch` : l'API AWCI démarre seule.

## Ingestion

```bash
acf-awci-ingest --run latest --domain all          # 0-72 h / 3 h, profil operational-v1
acf-awci-ingest --run 2026092506 --domain north_africa --steps 0-24/3
```

- Données écrites sous `ACF_AWCI_DATA_DIR` (défaut `<repo>/data/awci/`),
  un dossier par domaine et par run : `cube.nc` + `manifest.json`.
- Écriture atomique (`<run>.tmp/`, bascule via `<run>.old`). Rétention : `--keep 8`.
- Une réingestion qui finit `partial` ne remplace jamais un run `complete`
  (le manifest renvoyé porte `rejected_rerun_status`) ; `--force` pour l'imposer.
- `latest` = run le plus récent dont la dernière échéance demandée est
  publiée ; sinon repli automatique sur le run précédent.
- Une échéance en échec est journalisée et marquée ; le run est `partial`.
  Aucun cube n'est écrit si toutes les échéances échouent (`failed`,
  code de sortie 1).

**Mesures réelles** (run IFS 2026-09-25 06Z, domaine `north_africa`
15–45°N / 20°W–40°E, 25 échéances, conteneur 4 cœurs) :
durée **8,1 min** (critère < 30 min), cube **314 Mo** (l'estimation
initiale de la spec, ~170 Mo, était sous-évaluée), `status: complete`.
Niveaux valides après masquage sous le relief : 39 % des points à
1000 hPa, 89 % à 925 hPa, 99 % à 850 hPa, 100 % dès 700 hPa (relief et
dépression thermique saharienne).

### Planification systemd

```ini
# /etc/systemd/system/acf-awci-ingest.service
[Service]
Type=oneshot
Environment=ACF_AWCI_DATA_DIR=/srv/awci
ExecStart=/opt/acf/.venv/bin/acf-awci-ingest --run latest --domain all

# /etc/systemd/system/acf-awci-ingest.timer
[Timer]
OnCalendar=*-*-* 02,08,14,20:15:00 UTC
Persistent=true
[Install]
WantedBy=timers.target
```

Les runs 00/06/12/18Z sont publiés par ECMWF environ 7–9 h après
l'heure nominale ; le repli `latest` absorbe un retard.

### cron (alternative)

```
15 2,8,14,20 * * * ACF_AWCI_DATA_DIR=/srv/awci /opt/acf/.venv/bin/acf-awci-ingest --run latest --domain all
```

## API

```bash
ACF_AWCI_DATA_DIR=/srv/awci ACF_AWCI_CORS_ORIGINS=http://awci.intra acf-awci-web   # 127.0.0.1:8091
```

| Route | Contenu |
|---|---|
| `/api/v1/awci/domains` | domaines configurés (`config/awci/domains.json`) |
| `/api/v1/awci/runs?domain=` | runs disponibles, statut, échéances manquantes |
| `/api/v1/awci/meta?domain=&run=` | niveaux hPa + FL ISA, échéances, heures de validité, couches |
| `/api/v1/awci/field?…&layer=&step=&level=&format=json\|f32` | champ 2D (JSON avec `null`, ou float32 little-endian + en-têtes `X-AWCI-*`) |
| `/api/v1/awci/point?…&step=&level=&lat=&lon=` | détail explicable d'un point (modules, couches, modules exclus) |
| `/api/v1/awci/profile?…&step=&lat=&lon=` | idem sur les 12 niveaux |
| `/api/v1/awci/timeseries?…&level=&lat=&lon=` | AWCI sur toutes les échéances |
| `/api/v1/awci/registry` | unités, équations, sources, statuts scientifiques, classes, profil |

Le router est aussi monté dans l'application existante (`acf-web`).

**Latences mesurées** (cube réel ci-dessus, 50 requêtes, TestClient) :
`/field` f32 p95 5,0 ms ; `/field` JSON p95 64 ms ; `/point` p95 29 ms ;
`/profile` p95 24 ms ; `/timeseries` p95 20 ms (critère < 300 ms).

## Garanties et limites

- Source : ECMWF IFS 0,25° Open Data, **© ECMWF, CC-BY-4.0** — attribution
  obligatoire dans le front (fournie par chaque réponse).
- Valeur manquante = `null` (JSON) / `NaN` (f32), jamais 0. Modules non
  alimentés en V1 (`temporal`, `confidence`) listés dans `excluded_modules`.
  `awci = null` si les modules présents pèsent moins de 0,5.
- Statuts scientifiques (`/registry`) : HYPOTHESIS pour la turbulence CAT
  (seuils Ellrod calibrés sur des grilles plus grossières que 0,25° ;
  ~3,5 % des points à 250 hPa en « Moderate-Severe » sur le run mesuré ;
  TI2 négatif = divergence > déformation, classé « Smooth »), le
  givrage (seuils T/HR choix ACF), la base nuageuse LCL (n'est pas un
  plafond), la poussière (proxy) et le composite AWCI.
- Niveaux sous le relief (pression du niveau > pression de surface) : `null`
  pour toutes les couches par niveau — ce sont des extrapolations IFS.
- Givrage : humidité relative par rapport à l'eau calculée depuis q, T, p
  (le `r` IFS, relatif à la glace sous −23 °C, n'est pas utilisé).
- `/point`, `/profile`, `/timeseries` : `missing_inputs`, `present_weight` et
  `decomposition` (points AWCI) par point.
- Pas d'interpolation verticale : niveaux IFS natifs uniquement.
- Domaines traversant l'antiméridien non supportés en V1.

## Tests

```bash
QT_QPA_PLATFORM=offscreen .venv/bin/python -m pytest -q tests/test_awci_ops_*.py tests/test_web_awci_api.py
ACF_AWCI_NETWORK_TESTS=1 .venv/bin/python -m pytest -q tests/test_awci_ops_network.py   # réseau réel (opt-in)
```

La fixture `tests/data/awci_ops/` contient de vraies données IFS découpées
(voir son `NOTICE.md`) ; `tools/awci/make_ops_fixture.py` la régénère.
