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
  - une réponse 404 (« Data Not Found ») signifie « pas de sondage à cette heure » et n'est pas une panne ;
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
