# AWCI Web — SP1 : socle données & science (design)

**Date :** 2026-09-25 · **Statut :** en revue · **Sous-projet :** 1 / 4
**Entrée :** `docs/awci/AWCI_WEB_PREWORK_AUDIT.md`

## 1. Contexte et objectif

AWCI Web est un **outil opérationnel** (prévisionnistes, réseau interne,
sans comptes en V1) qui affiche la complexité météorologique aviation
calculée à partir d'une **vraie prévision numérique** : ECMWF IFS Open
Data 0,25°. Le desktop Qt est hors périmètre.

Le projet est découpé en 4 sous-projets :

| # | Sous-projet | Dépend de |
|---|---|---|
| **SP1** | **Socle données & science** (ce document) | — |
| SP2 | Front : coque + carte + détail explicable | SP1 |
| SP3 | Aéroports + METAR/TAF/SIGMET | SP1, SP2 |
| SP4 | Route grand cercle, coupe verticale, profil, évolution | SP1, SP2 |

**Objectif de SP1 :** produire, pour chaque run IFS et chaque domaine
configuré, un cube de champs AWCI et de dangers **réels, traçables,
reproductibles**, et les servir par une API typée en lecture seule.

**Critères de succès**
1. Un run IFS réel est ingéré de bout en bout sans intervention, pour
   le domaine par défaut, en moins de 30 min sur un serveur 4 cœurs.
2. Deux ingestions du même run produisent des cubes identiques bit à
   bit (hors métadonnées d'horodatage d'ingestion).
3. Aucune valeur manquante n'est jamais servie comme 0 : les modules
   non alimentés valent `null` et sont listés dans `missing_inputs`.
4. Toute réponse API porte la provenance (modèle, run, échéance, heure
   de validité, domaine, attribution CC-BY-4.0) et un `source_tier`.
5. Les requêtes API de lecture répondent en < 300 ms (p95) sur le
   domaine par défaut ; aucune requête ne déclenche de calcul lourd.
6. Le moteur vectorisé reproduit les scores de module d'`AWCICalculator` à
   1e-12 près et son `awci` à l'arrondi 0,1 près (|Δ| ≤ 0,05) sur le
   profil `legacy` (test de parité).

**Hors périmètre SP1 :** front web, METAR/aéroports, route et coupe
verticale, authentification, interpolation verticale, ensemble ECMWF
(ENS), modification du desktop ou d'`AWCICalculator`.

## 2. Source de données (vérifiée le 2026-09-25 sur l'index réel)

- URL : `https://data.ecmwf.int/forecasts/{YYYYMMDD}/{HH}z/ifs/0p25/oper/`
- Fichiers par échéance : `{YYYYMMDDHH0000}-{step}h-oper-fc.grib2` et
  son `.index` (JSON par ligne : `param`, `levtype`, `levelist`,
  `_offset`, `_length`).
- Téléchargement **par plages d'octets** (`Range:`) des seuls messages
  utiles, à partir de l'index.
- Runs 00/06/12/18z ; échéances utilisées en V1 : 0 → 72 h pas de 3 h
  (25 pas).
- Licence : **CC-BY-4.0**, attribution « © ECMWF, CC-BY-4.0 » exposée
  par l'API et affichée par le front.

**Champs ingérés**

| Type | Paramètres | Niveaux |
|---|---|---|
| Niveaux pression | `t` (K), `q` (kg/kg), `r` (%), `u`, `v` (m/s), `w` (Pa/s), `gh` (gpm), `d` (s⁻¹) | 1000, 925, 850, 700, 600, 500, 400, 300, 250, 200, 150, 100 hPa |
| Surface | `2t`, `2d` (K), `10u`, `10v`, `10fg` (m/s), `sp`, `msl` (Pa), `mucape` (J/kg), `tprate` (kg m⁻² s⁻¹), `ptype` (code), `tcc` (0–1), `lsm` | — |

Le niveau 50 hPa et 10 hPa sont exclus (hors domaine aviation civile).

## 3. Architecture

```
config/awci/domains.json        config/awci/profiles/operational-v1.json
          │                                  │
          ▼                                  ▼
acf-awci-ingest (CLI, planifié cron/systemd)
  ops/source_ecmwf.py   index → plages d'octets → GRIB en mémoire/disque temp
  ops/decode.py         GRIB → xarray (cfgrib), découpe domaine, unités SI
  ops/diagnostics.py    dangers vectorisés (NumPy)
  ops/engine.py         AWCI vectorisé (profils legacy / operational-v1)
  ops/store.py          cube NetCDF + manifest.json, écriture atomique, rétention
          │
          ▼  data/awci/{domain}/{run}/cube.nc + manifest.json
          │
src/acf/web/awci_router.py   /api/v1/awci/*  (lecture seule)
```

Emplacement du code : `src/acf/awci/ops/` (nouveau sous-paquet, sans
aucune dépendance Qt). Racine de stockage configurable
(`ACF_AWCI_DATA_DIR`, défaut `<repo>/data/awci/`, déjà ignoré par git).

### 3.1 Unités (single source)

Tout est converti en SI à l'ingestion : T en K, q en kg/kg, pression en
hPa pour les calculs thermodynamiques, vitesses en m/s, `gh` en m
(géopotentiel en mètres géopotentiels, traité comme hauteur — écart
< 0,5 % aux latitudes du domaine, documenté), `tprate` converti en mm/h
(×3600, 1 kg m⁻² = 1 mm d'eau).

### 3.2 Niveaux de vol

Chaque niveau pression reçoit un libellé FL calculé par l'**atmosphère
standard OACI (Doc 7488)** complète : troposphère (gradient
−6,5 K/km jusqu'à 11 km) **et** stratosphère isotherme 11–20 km.
Implémentation unique `ops/isa.py`, testée contre les valeurs tabulées
du Doc 7488 (ex. 300 hPa → 9 164 m ≈ FL300 ; 200 hPa → 11 784 m ≈
FL387). Pas d'interpolation verticale : les données sont servies aux
niveaux natifs IFS.

## 4. Diagnostics de dangers (couches servies individuellement)

Chaque diagnostic est une fonction pure NumPy `(arrays) -> array`, avec
une fonction de référence scalaire existante (`acf.science`) utilisée
en test de parité. Chaque diagnostic déclare : grandeur, unité,
équation, source, statut (`scientific_status`).

| Couche | Définition | Unité | Source / statut |
|---|---|---|---|
| `wind_speed` | √(u²+v²) au niveau | m/s | standard |
| `vertical_shear` | ‖ΔV‖/Δz entre le niveau et le niveau supérieur adjacent (au niveau le plus haut, 100 hPa : niveau inférieur adjacent), Δz = Δ`gh` réel | s⁻¹ | standard |
| `layer_shear` | ‖ΔV‖ entre les mêmes deux niveaux | m/s | standard |
| `cat_ti2` | Ellrod–Knapp TI2 = VWS × (DEF + CVG), DEF à partir des gradients horizontaux de u,v (espacement métrique réel), **CVG = −`d`** (divergence IFS réelle) ; catégories `CATIndex.category()` (seuils 4/8/12 ×10⁻⁷ s⁻²) | s⁻² | Ellrod & Knapp (1992) — CONFIRMED pour la formule, HYPOTHESIS pour l'usage à 0,25° |
| `icing_potential` | 1 si −20 °C ≤ T ≤ 0 °C **et** HR ≥ 70 %, sinon 0 ; HR **par rapport à l'eau** calculée depuis q, T, p (le `r` IFS n'est pas utilisé : il est relatif à la glace sous −23 °C, mixte entre −23 et 0 °C — corrigé à la revue finale) | booléen | approche T+HR de Schultz & Politovich (1992) ; **seuils = choix ACF, statut HYPOTHESIS**, à calibrer (SP ultérieur) |
| `theta_e` | Bolton (1980) à partir de T, q, p | K | CONFIRMED |
| `mucape` | champ IFS tel quel (colonne) | J/kg | champ modèle |
| `cloud_base_lcl` | 125 m × (2t − 2d) (Espy) — **libellé « base nuageuse estimée (LCL) », jamais « plafond »** | m AGL | approximation standard, HYPOTHESIS comme estimateur de plafond |
| `precip_rate` | `tprate` ×3600 ; classes OMM n°8 : < 2,5 faible, 2,5–10 modérée, 10–50 forte, > 50 violente | mm/h | WMO-No. 8 |
| `precip_type` | `ptype` IFS décodé (pluie, neige, pluie verglaçante, grésil…) | code | champ modèle |
| `gust_10m` | `10fg` | m/s | champ modèle |
| `dust_proxy` | rampe(10fg ; 8→18 m/s) × (1 − rampe(HR2m ; 20→70 %)) — HR2m de 2t/2d | 0–1 | **proxy HYPOTHESIS, libellé comme tel** |

**Niveaux sous le relief :** tout niveau pression dont la pression dépasse la pression de surface `sp` est extrapolé par IFS ; toutes les couches par niveau y valent `NaN` (`null` dans l'API).

Les couches surface/colonne (`mucape`, `cloud_base_lcl`, `precip_*`,
`gust_10m`, `dust_proxy`) sont indépendantes du niveau et servies comme
telles (pas dupliquées artificiellement sur chaque niveau).

## 5. Moteur AWCI vectorisé

### 5.1 Parité avec l'existant

`ops/engine.py` réimplémente le mécanisme d'`AWCICalculator`
(normalisation, modules, interactions, renormalisation par budget de
poids, classes) sur des tableaux. Profil `legacy` = constantes actuelles
d'`AWCICalculator`/`Normalizer`/`WeightsManager` lues **depuis ces
classes** (pas recopiées). Test de parité sur ≥ 10 000 points tirés
dans les plages physiques : scores de module à ≤ 1e-12 ; `awci` égal à
celui d'`AWCICalculator` après son propre arrondi à 0,1 (|Δ| ≤ 0,05). `AWCICalculator`
n'est pas modifié.

### 5.2 Profil `operational-v1` (fichier JSON versionné)

| Module | Entrées réelles | Normalisation | Poids |
|---|---|---|---|
| dynamic | `wind_speed` (50 %) + `layer_shear` (50 %) | `normalize_wind`, `normalize_wind_shear` | 0,20 |
| thermodynamic | **`theta_e`** (remplace la température brute) | `normalize_theta_e` | 0,25 |
| convective | **`mucape` seul** (le CIN n'est plus additionné ; IFS Open Data ne publie pas de CIN) | `normalize_cape` | 0,20 |
| microphysical | `precip_rate` (50 %) + sévérité de `precip_type` (50 %, table `PHASE_SEVERITY` existante) | existantes | 0,15 |
| topographic | élévation réelle SRTM15+ embarquée (`terrain_elevation`) | `normalize_topographic` | 0,10 |
| temporal | non alimenté en V1 | — | `null` |
| confidence | non alimenté en V1 (pas d'ENS) | — | `null` |
| ceiling, visibility, dust, ash, microburst, ensemble_spread, model_disagreement | hors composite V1 (poids 0, `ceiling`/`visibility`/`dust` servis comme couches du §4) | — | 0 |

Interactions : `wind_topo`, `conv_thermo` inchangées (statut INITIAL).

**Règle des modules manquants :** un module dont une entrée requise est
absente ou non finie en un point vaut `null` en ce point ; le score
composite est renormalisé sur la somme des poids des modules présents
(formule identique à `_renormalized_score`), et la liste des modules
exclus est renvoyée. Si la somme des poids présents < 0,5, `awci` =
`null` (« données insuffisantes »), jamais une valeur basse.

**Décisions scientifiques actées (revue 2026-09-25) :**
(a) θe remplace la température brute dans le module thermodynamique
(la normalisation monotone de T contredisait sa propre documentation) ;
(b) le CIN ne contribue plus positivement à la complexité convective.
Ces deux choix ne concernent que `operational-v1` ; statut HYPOTHESIS,
enregistrés dans `scientific_status`.

### 5.3 Classes

Une seule table : `AWCICalculator.LEVEL_THRESHOLDS`
(0/20/35/50/65/85 → Very Low … Extreme), servie par `/registry`. La
palette de couleurs appartient au front (SP2).

## 6. Stockage

- Un fichier `cube.nc` (NetCDF4, float32, zlib niveau 4, chunks
  `(1, 1, lat, lon)`) par couple (domaine, run) : variables
  `(step, level, lat, lon)` pour les champs par niveau,
  `(step, lat, lon)` pour les champs surface ; `NaN` = manquant.
- `manifest.json` : run, domaine, profil et sa version, pas présents,
  pas manquants, variables, attribution, version d'ACF (git SHA), durée,
  `status` ∈ {`complete`, `partial`, `failed`}.
- Écriture dans `…/{run}.tmp/` puis bascule via `{run}.old` (le run n'est jamais absent pour un lecteur) ; un run `complete` n'est jamais remplacé par un run moins complet sans `--force`.
- Rétention : N derniers runs par domaine (config, défaut 8 = 2 jours).
- Reproductibilité : aucun aléa ; ordre de calcul déterministe ;
  attributs d'horodatage isolés dans le manifest.

## 7. Ingestion (`acf-awci-ingest`)

```
acf-awci-ingest [--run latest|YYYYMMDDHH] [--domain NAME|all] [--steps 0-72/3]
```
- `latest` = run le plus récent dont l'index du dernier pas demandé
  existe (sinon repli sur le run précédent, journalisé).
- Relances : 4 tentatives, attente exponentielle 2/4/8/16 s ; taille
  reçue vérifiée contre `_length`.
- Un pas en échec n'empêche pas les autres ; run marqué `partial`.
- Journal structuré (loguru, déjà dépendance) ; code de sortie ≠ 0 si
  `failed`.
- Planification fournie sous forme d'exemples `systemd` timer et
  `cron` dans la doc (pas d'ordonnanceur embarqué).
- Réseau : `urllib` de la bibliothèque standard (aucune nouvelle
  dépendance). Décodage : `cfgrib`/`eccodes` (extra `formats`).

## 8. API `/api/v1/awci/*`

Handlers `def` (exécutés dans le pool de threads, jamais de calcul lourd),
modèles Pydantic en entrée et en sortie, tous les paramètres bornés et
validés contre le manifest (400 sinon, 404 si run/domaine inconnu).

| Route | Réponse |
|---|---|
| `GET /domains` | domaines configurés (bbox, résolution) |
| `GET /runs?domain=` | runs disponibles + `status` + pas présents |
| `GET /meta?domain=&run=` | niveaux (hPa + FL ISA), pas, heures de validité, couches, provenance |
| `GET /field?domain=&run=&layer=&step=&level=&format=json\|f32` | champ 2D ; `json` : `null` pour manquant ; `f32` : `application/octet-stream` little-endian + en-têtes `X-AWCI-Shape`, `X-AWCI-Lats`, `X-AWCI-Lons` (bornes), `X-AWCI-Nodata: NaN` |
| `GET /point?domain=&run=&step=&level=&lat=&lon=` | point le plus proche : entrées, couches, modules, décomposition, `missing_inputs` (exclusions V1 + modules non alimentés en ce point), `present_weight`, classes, statuts |
| `GET /profile?domain=&run=&step=&lat=&lon=` | idem sur tous les niveaux |
| `GET /timeseries?domain=&run=&level=&lat=&lon=` | idem sur tous les pas |
| `GET /registry` | couches (unité, équation, source, statut), modules, poids du profil, classes |

Enveloppe commune de chaque réponse : `provenance` {model:
"ECMWF IFS 0.25° Open Data", run, step, valid_time, domain, profile,
profile_version, license: "CC-BY-4.0", attribution}, `source_tier:
"nwp_forecast"`.

CORS : origines autorisées lues depuis la config (défaut : même
origine). Le router est monté dans l'app existante
(`hpc_dashboard_server.create_app`) sans modifier les routes existantes.

## 9. Gestion d'erreurs

- Données absentes d'un point/pas : `null` + raison, jamais d'exception.
- Run partiel : servi avec `status: "partial"` et liste des pas
  manquants ; un pas manquant → 404 explicite.
- Cube illisible : 503 avec message, journalisé.
- Paramètre invalide : 422 (Pydantic) / 400 (hors manifest).

## 10. Tests

| Niveau | Contenu |
|---|---|
| Unitaires diagnostics | chaque fonction vectorisée vs référence scalaire `acf.science` (TI2, Bolton, LCL…) sur tableaux aléatoires bornés ; cas limites (HR 0, pôles exclus du domaine, Δz nul → NaN) |
| ISA | valeurs Doc 7488 en troposphère et stratosphère |
| Parité moteur | profil `legacy` vs `AWCICalculator` (≥ 10 000 points) |
| Profil opérationnel | règle des modules manquants, seuil 0,5, renormalisation |
| Ingestion | index et GRIB réels minimaux (fixture découpée, quelques Ko, attribution) ; plages d'octets simulées par un serveur HTTP local ; run partiel ; écriture atomique ; rétention |
| Reproductibilité | deux ingestions de la fixture → cubes identiques |
| API | `TestClient` : toutes les routes, validation, 404/400/422, format `f32`, absence de 0 pour manquant |
| Réseau réel | marqué `network`, ignoré par défaut : ingestion d'un pas réel |

Commandes : `ruff check`, `mypy` sur `src/acf/awci/ops` et le router,
`pytest`.

## 11. Dépendances

Aucune nouvelle dépendance Python : `numpy`, `xarray`, `netCDF4`,
`cfgrib`/`eccodes` (extra `formats`), `fastapi`/`pydantic` (extra
`web`), `loguru`. Correction incluse : l'extra `web` ne doit plus
exiger `paramiko`/`torch` pour démarrer le router AWCI — le router est
importable seul ; `create_app` continue de fonctionner comme avant.

## 12. Risques

| Risque | Mitigation |
|---|---|
| Volume de téléchargement (~1,8 Go/run) | plages d'octets, sous-ensemble de niveaux, pas limités à 72 h |
| Changement de format/URL ECMWF | parsing d'index isolé dans `source_ecmwf.py`, test réseau marqué |
| Seuils givrage/poussière non calibrés | statut HYPOTHESIS exposé par `/registry` et affiché ; calibration = sous-projet ultérieur |
| Grille 0,25° trop grossière pour la CAT locale | documenté dans la couche ; TI2 reste l'index opérationnel de référence |
| Surcharge disque | rétention configurable |
