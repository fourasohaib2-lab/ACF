# AWCI Web — SP3 : aérodromes, METAR/TAF, SIGMET, validation des nuages

Spec : `docs/superpowers/specs/2026-09-26-awci-web-sp3-aero-obs-design.md`. Code : `src/acf/awci/obs/`
(décodage METAR, client AWC, stockage, ingestion), `src/acf/awci/ops/verify.py` (validation),
`src/acf/web/awci_obs.py` (API), `web/awci/src/panels/{AirportPanel,SigmetList,ValidationPage,AeroControls}.tsx`.

## Ingérer les observations

```bash
acf-awci-obs --domain north_africa              # une passe : stations, METAR (3 h), TAF, SIGMET
acf-awci-obs --domain north_africa --hours 72   # rattrapage des METAR d'un run entier (AWC : ≥ 7 jours)
```

- Source : Aviation Weather Center (NOAA/NWS), API de données publique, **domaine public**.
- À planifier toutes les 10 à 30 min (cron/systemd), comme `acf-awci-ingest`.
- Stockage : `{ACF_AWCI_DATA_DIR}/.obs/{domaine}/`.
  - `metar/` et `sigmet/` : archives par jour UTC, dédoublonnées, écritures atomiques, rétention 10 jours.
  - `taf/latest.json` : dernier TAF.
  - `stations.json` : liste des stations, rafraîchie chaque semaine.
  - `status.json` : bilan de la dernière ingestion.
- L'API AWC plafonne chaque liste à 400 éléments. Le client subdivise les requêtes pleines : 557 stations METAR sur l'Afrique du Nord au lieu de 400.
- Toute entrée externe est validée ; une entrée rejetée est comptée (`rejected`), jamais propagée.
- Une passe réelle (30 h d'historique) : 17 339 METAR, 379 TAF et 6 SIGMET en 70 s, soit 3,5 Mo.
- Le serveur web lit uniquement ce stockage. Aucune requête AWC n'est faite pendant une requête web.

## Décodage METAR

Le JSON de l'AWC ne donne ni le type CB/TCU ni le temps présent. ACF décode donc le texte brut (FM 15, OMM-N° 306 et OACI Annexe 3).

**Plafond** : base de la plus basse couche BKN ou OVC, ou visibilité verticale.
- CAVOK, NSC, NCD, SKC et CLR n'indiquent **aucun plafond sous 5000 ft** ; ils ne disent rien au-dessus.
- Une couche `///` plus basse que le plafond connu rend le plafond **inconnu**.

**Convection** : CB ou TCU dans les nuages, ou TS/VCTS dans le temps présent.
- L'absence de convection n'est retenue que pour un METAR manuel, ou `AUTO` avec CAVOK.
- Un METAR `AUTO` sans type (`///`) ou avec NCD laisse la convection **inconnue**.

**Contrôle sur 400 METAR réels** :
- les couches décodées sont identiques à celles de l'AWC ;
- la catégorie de vol (FAA, affichage seulement) est identique dans 397 cas sur 397.

Sur 17 339 METAR réels, 4 textes tronqués à la source (par exemple `METAR EQYS 25`) sont refusés et comptés.

## API (`/api/v1/awci`)

| Route | Contenu | p95 sur le cube réel |
|---|---|---|
| `GET /airports?domain=&time=` | stations et METAR décodé le plus proche de `time` (± 30 min) | 114 ms |
| `GET /airport?domain=&icao=&run=` | METAR de la fenêtre du run, dernier TAF, série modèle à la maille, paires, Δz | 233 ms |
| `GET /sigmets?domain=&time=` | SIGMET valides à `time`, en GeoJSON | 5 ms |
| `GET /verification?domain=&run=` | rapport de validation, mis en cache jusqu'à la modification du cube ou de l'archive | 4,3 s au premier appel, puis 6 ms |

## Écran

- **Carte, à l'heure de validité affichée** :
  - aérodromes colorés par catégorie FAA (cercle creux s'il n'y a pas d'observation, anneau si TCU/CB observé) ;
  - SIGMET avec un style par danger, cendres volcaniques (VA) en trait épais ;
  - légende sous la carte, jamais sur le champ.
- **Choix de l'aérodrome** : liste déroulante, utilisable au clavier, ou clic sur la carte. Le point d'inspection se place alors sur l'aérodrome.
- **Panneau Aérodrome** :
  - METAR brut et décodé à la validité, ou l'une de ces mentions : « pas de METAR à ± 30 min », « échéance future : pas encore observée » ;
  - le modèle au même instant ;
  - un tableau et une courbe du plafond observé et du plafond modèle par échéance ;
  - une alerte si l'écart d'altitude entre station et surface modèle dépasse 300 m ;
  - le dernier TAF, signalé s'il ne couvre pas la validité affichée.
- **Liste des SIGMET** : danger, FL de base et de sommet, validité, FIR, déplacement, texte brut.
- **Page Validation** :
  - tables de contingence avec POD, FAR, CSI, biais et ETS, par tranche d'échéance ;
  - la mention « échantillon insuffisant » en dessous de 10 événements observés ;
  - les exclusions par motif, les définitions et les paramètres.

## Méthode de validation

L'appariement suit la spec §5 :
- maille la plus proche ;
- METAR ou SPECI le plus proche à ± 30 min, le METAR de routine l'emportant en cas d'égalité ;
- stations à plus de 300 m de la surface modèle exclues du plafond (seuil au statut HYPOTHESIS).

Les échéances pas encore observées sont comptées à part des METAR manquants.

Les scores suivent Jolliffe et Stephenson (2012), chapitre 3 :

| Score | Formule |
|---|---|
| POD | a/(a+c) |
| FAR | b/(a+b) |
| CSI | a/(a+b+c) |
| Biais | (a+b)/(a+c) |
| ETS | (a − a_r)/(a+b+c − a_r), avec a_r = (a+b)(a+c)/n |

## Premier résultat réel : IFS 2026-09-25 12Z, Afrique du Nord

Échéances observées au moment du calcul : +0 à +21 h. 12 531 METAR ont donné 2 651 paires, sur 390 des 557 stations.

| Événement | a / b / c / d | POD | FAR | CSI | Biais | ETS |
|---|---|---|---|---|---|---|
| Plafond < 500 ft | 2 / 25 / 14 / 2424 | 0,13 | 0,93 | 0,05 | 1,69 | 0,045 |
| Plafond < 1000 ft | 2 / 40 / 30 / 2393 | 0,06 | 0,95 | 0,03 | 1,31 | 0,020 |
| Plafond < 1500 ft | 6 / 45 / 37 / 2377 | 0,14 | 0,88 | 0,07 | 1,19 | 0,059 |
| Convection TCU/CB | 28 / 188 / 24 / 2268 | 0,54 | 0,87 | 0,12 | **4,15** | 0,10 |

- **Base du plafond** : erreur moyenne −1570 ft, erreur absolue moyenne 1744 ft (n = 73 ; valeur modèle − valeur observée).
- **Exclusions** : 9 469 couples station-échéance pas encore observés et 1 804 sans METAR à ± 30 min. S'y ajoutent, parmi les 2 651 paires, 140 écartées du plafond pour Δz > 300 m et 143 à convection inconnue.

Lecture :
- La convection diagnostiquée est **environ 4 fois trop fréquente**. Cela confirme la surestimation suspectée en SP1C (13 % de Cb). Elle a été recalibrée depuis (section suivante).
- Les plafonds bas sont peu prévisibles avec 12 niveaux standard (1 à 2 km entre 1000 et 700 hPa). Le plafond modèle est en moyenne plus bas que l'observé.
- Ce sont des scores d'un seul run sur 21 h. Il faut cumuler plusieurs runs avant de conclure sur des seuils.

## Recalibration de la convection (profil nuageux 1.2.0)

La convection était surdiagnostiquée d'un facteur 4 : l'ancienne règle ne demandait qu'un potentiel convectif
(MUCAPE ≥ 100 J/kg, profondeur du nuage, condensat ≥ 0,01 kg/m²).

Protocole :
- **Données** : sept runs IFS (23/09 00Z → 26/09 00Z, échéances 0 à 24 h). Les METAR sont appariés comme dans la
  validation ; les stations automatiques sans type de nuage sont exclues.
- **Candidats** : uniquement des règles **plus strictes**, faites de l'ancienne règle ET de conditions portant sur
  des grandeurs que le diagnostic reçoit (MUCAPE, condensat colonne, taux de précipitation).
- **Sélection** : sur 4 runs de calibration (23 et 24/09), la meilleure ETS parmi les règles de biais compris
  entre 0,7 et 1,5. Le jugement se fait ensuite sur 3 runs de test indépendants (25/09 00Z, 25/09 12Z, 26/09 00Z).
- **Outil reproductible** : `tools/awci/calibrate_convection.py`. L'enregistrement complet figure dans
  `calibration_convection` de `config/awci/clouds/cloud-v1.json`.

Règle retenue : TCU et Cb exigent en plus un **taux de précipitation IFS ≥ 0,1 mm/h**, c'est-à-dire une
convection réalisée par le modèle. Sinon, la convection reste Cu.

| Runs de test, poolés (7 073 paires) | a / b / c / d | POD | FAR | Biais | ETS |
|---|---|---|---|---|---|
| Règle précédente | 80 / 518 / 57 / 6418 | 0,58 | 0,87 | 4,36 | 0,11 |
| Règle recalibrée | 43 / 113 / 94 / 6823 | 0,31 | 0,72 | 1,14 | 0,16 |

- **Robustesse** : l'ETS progresse sur chacun des trois runs de test, de 0,13 à 0,19, de 0,10 à 0,15 et de 0,06
  à 0,11. Les règles voisines fondées sur la réalisation (précipitation ou condensat ≥ 0,1 kg/m²) donnent une ETS
  de test de 0,13 à 0,165. Les règles fondées sur la seule MUCAPE n'apportent rien (0,09 à 0,11).
- **Physique** : la CAPE est un potentiel. La médiane de MUCAPE est même plus forte pour les fausses alertes
  (490 J/kg) que pour les succès (387 J/kg). Ce sont la précipitation et le condensat modèle qui signalent une
  convection effectivement déclenchée.
- **Coût** : la POD passe de 0,58 à 0,31. Des TCU et Cb observés deviennent Cu dans le diagnostic, en particulier
  les Cb secs à base haute (Sahara, virga) dont la pluie n'atteint pas le sol modèle. Pour l'alerte, le potentiel
  reste visible par la MUCAPE (couche et indicateur « Convection »).
- **Portée** : la règle s'applique aux runs ingérés avec le profil 1.2.0. Les cubes antérieurs gardent leur
  diagnostic, et leur manifeste indique la version du profil utilisé.
- **Statut** : HYPOTHESIS. Sept runs d'une même semaine ne couvrent ni la saison ni le cycle diurne complet, et
  il faudra réévaluer régulièrement (page Validation).

## Tests

- Python :
  - `tests/test_awci_obs_metar.py` : cas normatifs et corpus réel ;
  - `tests/test_awci_obs_ingest.py` : plafond de 400, validation, stockage, commande d'ingestion ;
  - `tests/test_awci_ops_verify.py` : scores calculés à la main, appariement, exclusions, cas réel DAAG sur la fixture IFS ;
  - `tests/test_web_awci_obs_api.py` : routes de l'API ;
  - `tests/test_awci_ops_store_concurrency.py` : première ouverture concurrente du cube.
- Front :
  - Vitest sur des réponses d'API réelles (`web/awci/src/test-data`, avec NOTICE) ;
  - Playwright `e2e/aero.spec.ts` : aérodrome, validation, SIGMET, domaine sans observation, accessibilité (axe).
- Fixtures : réponses AWC réelles enregistrées le 2026-09-26 (`tests/data/awc`, avec NOTICE).

## Correctif transverse

La première ouverture concurrente d'un cube par plusieurs requêtes web faisait planter le serveur :
- segfault HDF5 sur 5 démarrages à froid sur 10 ;
- ou erreur 500.

Le défaut date de SP1 ; SP3 le rendait fréquent. L'ouverture est désormais sérialisée : 0 plantage sur 10 démarrages, toutes les requêtes à 200.

## Limites

- **TAF** : seul le dernier TAF est conservé. La validation du TAF lui-même n'est pas faite.
- **Carte** : pas d'étiquettes d'indicatif, faute de glyphes locaux ; l'indicatif est dans le panneau et la liste.
- **SIGMET** : ils sont retenus si la boîte englobante de leur polygone recoupe le domaine.
- **Validation** : elle est calculée à la demande (4,3 s la première fois).
- **Stations absentes** : une station qui émet des METAR mais que `stationinfo` ne liste pas comme site METAR est absente (HLMS dans le corpus).
