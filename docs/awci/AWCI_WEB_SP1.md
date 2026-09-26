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

Pour un téléchargement automatique (runs, observations, suppression après 7 jours) : `acf-awci-web --auto`,
voir `AWCI_WEB_AUTO.md`. Les commandes ci-dessous restent disponibles pour une ingestion ponctuelle.

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

## SP1C — Nuages et champs étendus

Spec : `docs/superpowers/specs/2026-09-25-awci-web-sp1c-clouds-design.md`. Code :
`src/acf/awci/ops/{parcel,accum,clouds,cloud_profile,calibration}.py`. Profil des seuils :
`config/awci/clouds/cloud-v1.json` (`--cloud-profile` pour en changer). Tous les produits
nuageux sont des **diagnostics modèle** (statut HYPOTHESIS), jamais des observations.

**Entrées ajoutées** (7 messages IFS par échéance) : `tcw`, `tcwv`, `ttr`, `sf`, `sd`, `rsn`, `tp`.
Les cumuls sont différenciés avec l'échéance précédente **ingérée** ; après une échéance manquante,
ils valent `null` (`accumulation_interval_h` du manifest).

**Couches** :

| Famille | Couches |
|---|---|
| Par niveau | `cloud_fraction`, `cloud_genus` (code OMM 0500, −1 clair, −2 indéterminé), `cloud_species`, `potential_instability` |
| Étages | `cloud_cover_low/mid/high/total_diag`, `genus_low/mid/high` (nuage présent dans l'étage) |
| Aviation | `ceiling_m` (définition OACI), `lowest_cloud_base_m`, `highest_cloud_top_m` |
| Convection | `convective_class` (Cu, TCU, Cb calvus, Cb capillatus), `convective_top_m`, `convective_top_temp_k` |
| Espèces | `species_flags` (castellanus, lenticularis, fractus, nebulosus, spissatus) |
| Autres | `cloud_top_teff_k`, `column_condensate`, `snowfall_mm`, `snow_depth_cm`, `freezing_precip_mm`, `surface_height_m`, `cloud_cover_bias` |

**Routes** :
- `/clouds?domain&run&step&lat&lon` : couches du point (genre, espèces, base et sommet, octas),
  ligne « MODEL BKN030 OVC080 CB », plafond, convection, T_e, `tcc` IFS et biais ;
- `/volume?…&layer&step&stride=1|2|4` : float32 niveaux × lat × lon, suivi de `gh` ;
- `/terrain?…&stride` : hauteur de surface (0 m sur mer).

`/meta` et `/clouds` exposent aussi le statut nuageux du run (`cloud_status`), le contrôle de
cohérence avec le `tcc` IFS par échéance et l'intervalle de cumul (`accumulation_interval_h`).
Un run ingéré avant SP1C reste servi ; ses couches nuageuses renvoient 404.

**Hauteur de surface** : toutes les hauteurs au-dessus du sol (plafond, bases, profondeur convective,
`/terrain`) utilisent `surface_height_m`, la surface du modèle IFS obtenue par l'équation hypsométrique
à partir de `sp` (±2 m sur mer). Elle est cohérente avec le masque sous le relief et la particule.
Le relief SRTM15+ embarqué (grille à 1°) n'est pas utilisé : sa bathymétrie déborde sur les côtes
(−677 m près d'Alger), ce qui relevait les plafonds côtiers jusqu'à environ 1 km.

**Règles notables** : un Cb est une convection profonde à sommet glacé. Depuis le profil 1.2.0
(calibration contre les METAR, voir `docs/awci/AWCI_WEB_SP3.md`), TCU et Cb exigent en plus une convection
**réalisée** par l'IFS : taux de précipitation modèle ≥ 0,1 mm/h. Sans cela, la convection seulement
possible (CAPE, profondeur) reste Cu. Les Cb secs à base haute (Sahel, Sahara, virga), dont la pluie
n'atteint pas le sol du modèle, sont donc sous-diagnostiqués : c'est le prix, mesuré, de la division par
quatre des fausses alertes. Les espèces sont portées par chaque
couche (`cloud_species`) ; *fractus* ne s'applique qu'au St (OMM-N° 407).

**Calibration de RHc** :

```bash
.venv/bin/python tools/awci/calibrate_cloud_rhc.py --domain north_africa --runs 2026092512 --steps 0-72/6 --write
```

Sur le run 2026-09-25 12Z (13 échéances, 379 093 cellules), RHc passe de 0,80 / 0,70 / 0,70 à
**0,80 / 0,60 / 0,80** (bas / moyen / haut, profil 1.1.0). La RMSE de la couverture totale
diagnostiquée face au `tcc` IFS passe de 0,266 à 0,262, avec un biais de +0,038. L'écart restant
(écart-type ≈ 0,26) est **structurel** : 12 niveaux standard contre le schéma nuageux pronostique de
l'IFS sur 137 niveaux. Une calibration sur plusieurs runs et régimes reste à faire.

**Mesures réelles** (run IFS 2026-09-25 12Z, `north_africa`, 25 échéances, profil 1.1.0, après
les corrections de la revue finale) :

| Mesure | Résultat |
|---|---|
| Ingestion | 577 s, contre 8,1 min en SP1 (budget +2 min respecté) |
| Cube | 361 Mo (+15 %) |
| Hauteur de surface IFS | de −369 m (mer Morte) à 2 899 m, médiane 280 m |
| Biais moyen de couverture | de +0,004 à +0,080 selon l'échéance, statut « ok » partout |
| Latences p95 | `/clouds` 18,6 ms ; `/volume` 11,5 ms (stride 1) et 6,6 ms (stride 2) ; `/terrain` 4,9 ms ; `/point` 32 ms |
| Genre par étage (% des cellules × échéances) | bas : clair 74,5, Cb 11,8, Sc 9,3, Cu 3,4, Ns 0,6, St 0,4 ; moyen : clair 56,4, Cb 13,2, Ac 13,2, As 10,9, Cu 3,9, Ns 1,4 ; haut : clair 46,2, Cs 21,7, Cb 13,2, Ci 11,6, As 4,5, Cu 1,4 |
| Convection | Cb 13,2 % (capillatus 9,3, calvus 4,0), TCU 3,9 %, Cu humilis/mediocris 0,2 % |
| Plafond < 1000 ft | 1,4 % |
| Espèces | nebulosus 13,1 %, castellanus 12,0 %, spissatus 0,3 %, lenticularis 0,07 %, fractus 0,0 % |

Sur la fixture humide (Atlantique tropical, convection profonde), la température d'émission tirée de
l'OLR (≈ 209 K) et la température du sommet de la particule (≈ 214 K) concordent. Ces deux grandeurs
sont indépendantes l'une de l'autre.

**Limites et priorités de validation** :
- **Convection profonde probablement surdiagnostiquée** : Cb sur 13 % des cellules. Avant la revue,
  la règle exigeait de la pluie au sol ; les Cb secs à base haute apparaissaient alors en TCU (14 %).
  Cu humilis/mediocris sont presque absents. La particule de surface ignore l'inhibition entre deux
  niveaux standard, et la profondeur est quantifiée par des niveaux espacés de 1 à 2 km. Pour
  l'aviation, l'excès de Cb est l'erreur la moins dangereuse, mais il nuit à la confiance.
  Priorité n° 1 : tables de contingence contre les groupes TCU/CB des METAR, RDT et la foudre (SP3),
  puis ajout d'un critère d'inhibition (CIN et LFC par la particule), avant tout réglage de seuil.
  **Fait en SP3** : le biais mesuré contre les METAR valait 4,4. La règle recalibrée (convection réalisée
  par l'IFS, profil 1.2.0) le ramène à 1,14 sur des runs de test indépendants, avec une ETS de 0,16 au
  lieu de 0,11 (`docs/awci/AWCI_WEB_SP3.md`). Le CIN reste à ajouter : les critères fondés sur la seule
  CAPE n'amélioraient rien.
- Couches fines (Sc de 200 m, Ci fin) manquées par la résolution verticale ; incertitude de la base
  renvoyée (`base_uncertainty_m`).
- Le plafond ignore les couches convectives, dont la couverture n'est pas connue à l'échelle de la
  maille : la ligne METAR modèle les marque `///…CB`.
- *Castellanus* fréquent (12 %) : un critère d'instabilité conditionnelle entre deux niveaux
  standard est grossier ; à valider.
