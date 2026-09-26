# AWCI Web — SP7 : validation contre les radiosondages

Spec : `docs/superpowers/specs/2026-09-26-awci-web-sp7-radiosonde-verification-design.md`. Code :
- `src/acf/awci/obs/sounding.py` : liste IGRA, client University of Wyoming, lecture du CSV ;
- `src/acf/awci/obs/ingest.py` (`acf-awci-obs --soundings`) et `src/acf/awci/ops/auto.py` (`acf-awci-auto --soundings`) :
  ingestion ;
- `src/acf/awci/ops/verify_sounding.py` : appariement et scores ;
- `src/acf/web/awci_sounding.py` : route ;
- `web/awci/src/panels/SoundingVerification.tsx` et `web/awci/src/charts/VerticalScoreProfile.tsx` : écran ;
- `tools/awci/verify_soundings.py` : cumul sur plusieurs runs, IFS et GFS.

## Pourquoi

Les METAR ne valident que la surface. Le givrage et la turbulence en altitude reposent sur la température,
l'humidité et le vent du modèle en altitude, qui n'avaient **jamais été confrontés à une mesure**. Les radiosondages
mesurent ces grandeurs sur toute la colonne.

## Utilisation

```bash
acf-awci-obs --domain north_africa --soundings --hours 48    # archive les sondages des dernières 48 h
acf-awci-web --auto --soundings                              # archivage automatique après 00 et 12 UTC
```

- **Page Validation**, section « Radiosondages » :
  - profils verticaux du biais et de la RMSE (T, humidité relative, vent) pour IFS et GFS quand les deux ont le run ;
  - scores sur toute la colonne ;
  - tableau de contingence du givrage ;
  - nombre de sondages, de stations et exclusions.
- **API** : `GET /api/v1/awci/soundings/verification?domain=&run=&model=ifs|gfs`. Le rapport est mis en cache
  jusqu'à la modification du cube ou de l'archive.
- **Cumul** : `tools/awci/verify_soundings.py --data-dir DIR --runs R1,R2,…` (total et par échéance).

## Données

- **Stations** : liste IGRA v2 de la NOAA NCEI, relue chaque semaine. On garde les stations du domaine actives
  l'année en cours. L'indicatif OMM vient de l'identifiant IGRA ; aucune liste n'est écrite en dur.
- **Profils** : University of Wyoming (CSV).
  - **Niveaux** : les 12 niveaux AWCI (1000 à 100 hPa) figurent exactement dans les profils, sans interpolation
    verticale. Un niveau absent reste absent.
  - **Grandeurs gardées** : géopotentiel, T, Td, humidité relative sur l'eau, vent, heure et position du lâcher.
- **Service académique**, interrogé avec ménagement :
  - une requête à la fois, une seconde de pause entre deux ;
  - un profil déjà archivé n'est jamais redemandé ;
  - une réponse 404 (« Data Not Found ») ou 400 « Unable to retrieve the data » signifie « pas de sondage à cette
    heure » et n'est pas une panne ;
  - une requête en échec est sautée ; l'ingestion n'échoue que si toutes les requêtes échouent.
- **Archive** : `.obs/<domaine>/sounding/AAAA-MM-JJ.jsonl`, supprimée avec les autres observations (7 jours).

## Science

**Appariement**
- **Heure** : sondage nominal de 00 ou 12 UTC contre l'échéance du run valide à la même heure. Le lâcher réel a lieu
  avant l'heure nominale (23:31 UTC pour le sondage d'Alger du 25/09 à 00 UTC) ; son heure est archivée.
- **Lieu** : maille la plus proche du point de lâcher. La **dérive du ballon**, quelques dizaines de kilomètres en
  altitude, est **négligée**.
- **Niveaux** : on écarte ceux sous la surface du modèle (valeur absente) ou manquants dans l'observation.

**Scores**, par niveau et au total (biais = moyenne(modèle − observation), RMSE = √moyenne((modèle − observation)²)) :

| Grandeur | Modèle | Observation |
|---|---|---|
| T (K) | `t` du cube | `temperature_C` + 273,15 |
| Humidité relative sur l'eau (%) | recalculée depuis q, T, p (`thermo.relative_humidity_pct`, plafonnée à 100 %) | publiée sur l'eau par Wyoming |
| Vitesse du vent (m/s) | √(u² + v²) | publiée |
| Vent vectoriel (m/s) | RMSE = √moyenne(Δu² + Δv²) | u = −V sin(dd), v = −V cos(dd) |
| Cisaillement vertical (s⁻¹) | `vertical_shear` du cube | même définition (`kinematics.layer_shear`), Δz tiré du géopotentiel observé |
| Givrage potentiel | `icing_potential` du cube | même diagnostic (−20 °C ≤ T ≤ 0 °C et HR ≥ 70 %) appliqué au profil observé |

**Limites affichées dans l'écran** :
- **Givrage** : la référence est le diagnostic appliqué au profil mesuré, pas une observation de givrage (aucune n'est
  disponible en accès libre sur le domaine). Le tableau valide donc les **entrées** du diagnostic.
- **Turbulence** : l'indice d'Ellrod exige la déformation horizontale, qu'un sondage ne mesure pas. Seul son terme de
  cisaillement vertical est validé.
- **Indépendance** : les niveaux d'un même sondage, et les sondages d'un même jour, ne sont pas indépendants. Aucun
  intervalle de confiance n'est donné.
- **Assimilation** : à l'échéance +0 h, l'analyse a pu assimiler ces sondages. Les scores de +0 h mesurent donc
  l'accord de l'analyse avec les sondages, pas une prévision. Les échéances suivantes sont de vraies prévisions.

## Résultats réels (Afrique du Nord, mesurés le 2026-09-26)

**Archive** : `acf-awci-obs --soundings --hours 96`, 57 stations IGRA actives, 8 heures nominales (23/09 00 UTC →
26/09 12 UTC), 456 requêtes en 45 min environ (≈ 5 s par réponse, plus la pause).
- 195 sondages archivés ;
- 152 réponses 404 et 109 réponses 400 « Unable to retrieve the data », sur 15 stations (Grèce, Turquie, Maroc,
  Tunisie, Madère…) : c'est la façon dont le service dit qu'il n'a pas le sondage. Ce 400 était d'abord compté comme
  une erreur ; il est désormais traité comme « pas de sondage ». Un autre 400 reste une erreur.

**Scores** : `tools/awci/verify_soundings.py`, runs IFS et GFS 24/09 12Z, 25/09 00Z, 25/09 12Z, 26/09 00Z.
- **Appariement** : 263 paires sondage-run sur 30 stations, soit 2 769 niveaux pour IFS et 2 744 pour GFS. Deux
  sondages sont exclus, leur point de lâcher étant hors du domaine.
- **Pourquoi 30 stations sur 57** : un sondage n'est apparié que si un run a une échéance à son heure nominale.

| Modèle | T biais / RMSE (K) | HR biais / RMSE (%) | Vitesse biais (m/s) | RMSE vect. (m/s) | Cisaillement biais / RMSE (10⁻³ s⁻¹) | Givrage POD / FAR / ETS |
|---|---|---|---|---|---|---|
| IFS | 0,03 / 0,83 | −0,3 / 11,2 | −0,36 | 3,20 | −0,57 / 2,04 | 0,80 / 0,10 / 0,72 |
| GFS | −0,03 / 0,95 | −0,8 / 11,7 | −0,48 | 3,76 | −0,61 / 2,39 | 0,77 / 0,16 / 0,66 |

**Par échéance**, RMSE de T et RMSE vectorielle du vent (nombre de sondages) :

| Modèle | +0 h (95) | +12 h (95) | +24 h (73) |
|---|---|---|---|
| IFS | 0,70 K ; 2,49 m/s | 0,85 K ; 3,26 m/s | 0,93 K ; 3,90 m/s |
| GFS | 0,85 K ; 3,25 m/s | 0,97 K ; 3,84 m/s | 1,07 K ; 4,25 m/s |

**Par niveau** (biais / RMSE ; n = nombre de niveaux IFS) :

| hPa | IFS T (K) | IFS HR (%) | IFS vent vect. (m/s) | GFS T (K) | GFS HR (%) | GFS vent vect. (m/s) | n |
|---|---|---|---|---|---|---|---|
| 1000 | −0,07 / 1,27 | −1,7 / 8,7 | 2,7 | 0,03 / 1,52 | −5,5 / 11,6 | 3,0 | 164 |
| 850 | 0,06 / 0,83 | −1,4 / 13,1 | 2,7 | −0,15 / 0,92 | 1,2 / 12,0 | 3,1 | 263 |
| 700 | −0,07 / 0,70 | 0,3 / 11,4 | 2,5 | −0,29 / 0,83 | 0,6 / 12,9 | 3,4 | 263 |
| 500 | −0,00 / 0,60 | −0,2 / 13,0 | 2,7 | −0,06 / 0,70 | −1,0 / 12,5 | 3,6 | 263 |
| 300 | 0,07 / 0,52 | 1,3 / 14,1 | 3,9 | −0,00 / 0,58 | 1,4 / 14,5 | 4,1 | 258 |
| 250 | 0,04 / 0,87 | 0,3 / 11,2 | 3,9 | 0,10 / 0,90 | −0,2 / 11,9 | 4,4 | 258 |
| 200 | 0,08 / 1,02 | 0,2 / 11,6 | 3,3 | 0,01 / 1,09 | −1,0 / 10,7 | 4,0 | 252 |
| 100 | 0,20 / 0,99 | 0,3 / 2,8 | 3,9 | 0,10 / 1,03 | −1,2 / 3,0 | 4,3 | 239 |

**Lecture** :
- **Précision** : IFS fait mieux que GFS sur toutes les grandeurs et à toutes les échéances. L'écart est net sur le
  vent (3,20 contre 3,76 m/s), faible sur la température.
- **Échéance** : les erreurs croissent avec elle, comme attendu d'une prévision. À +0 h, l'analyse a pu assimiler
  ces sondages : c'est une borne basse, pas un score de prévision.
- **Biais** : aucun biais de température notable (moins de 0,3 K à tous les niveaux). Le vent est un peu sous-estimé.
- **Cisaillement** : il est sous-estimé par les deux modèles (biais d'environ −0,6 × 10⁻³ s⁻¹). C'est attendu d'une
  maille de 25 km et de niveaux espacés de 50 à 150 hPa, qui lissent les couches cisaillées fines. Les seuils de
  cisaillement de la turbulence CAT sont donc à lire comme des valeurs de modèle, pas de sondage.
- **Givrage** : 131 niveaux « givrants » selon le diagnostic appliqué aux profils observés.
  - IFS en retrouve 105 (POD 0,80, FAR 0,10, biais 0,89) ; GFS en retrouve 101 (POD 0,77, FAR 0,16).
  - Les entrées du diagnostic sont donc bien prévues. Cela ne dit rien de la justesse du diagnostic face au givrage
    réel.
- **Humidité à 100 hPa** : la RMSE y est faible (≈ 3 %) parce que l'humidité relative y est proche de zéro des deux
  côtés. Les capteurs d'humidité des sondes sont d'ailleurs peu fiables aux températures très basses : ce niveau
  n'apporte pas d'information sur l'humidité.
- **Portée** : 4 runs et 3 jours d'une fin septembre. Ces scores décrivent cette période, pas une climatologie.

## Vérification

- **pytest** :
  - `tests/test_awci_obs_sounding.py` : liste IGRA et CSV Wyoming réels, convention du vent, cisaillement observé
    égal à `layer_shear`, 404, requêtes en échec, cache de la liste, profils déjà archivés, appariement sur la
    fixture IFS réelle, scores calculés à la main, API ;
  - `tests/test_awci_ops_auto.py` : cadence des radiosondages et reprise après échec ;
  - `tests/test_awci_tools_verify_soundings.py` : outil de cumul sur les fixtures IFS et GFS.
- **Vitest** : `SoundingVerification.test.tsx`, sur les réponses réelles de l'API (fixtures IFS et GFS, sondage réel
  d'Alger).
- **Playwright** : `e2e/aero.spec.ts`, section « Radiosondages » avec les deux modèles, sans violation d'accessibilité
  grave.
- **Correctif annexe** : les tableaux de la page Validation (METAR, ensemble) débordaient de l'écran sur mobile
  (largeur de page 500 px pour un écran de 390 px). Ils défilent désormais dans leur cadre.
