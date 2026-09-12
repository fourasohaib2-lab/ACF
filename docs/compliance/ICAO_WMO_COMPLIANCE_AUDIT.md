# Audit de conformité ICAO (OACI) / OMM (WMO) — état réel

**Date de première passe :** 2026-09-12.
**Demande utilisateur :** "je veux que tout ACF soit conforme à toutes les
lois de l'OACI et de l'OMM" (+ "toute autre loi" applicable).

## 0. Ce que "conformité" peut/ne peut pas vouloir dire ici

Point de départ honnête, expliqué à l'utilisateur avant de commencer :
l'Annexe 3 de l'OACI (Service météorologique pour la navigation aérienne)
et le Règlement technique n°49 / Manuel des codes n°306 de l'OMM imposent
des obligations **aux États et à leurs services météorologiques désignés**
(MWO — Meteorological Watch Office), pas à un logiciel. Un logiciel ne peut
pas devenir "légalement conforme OACI" par lui-même — cela nécessiterait une
désignation officielle par une autorité aéronautique nationale, une garde
opérationnelle 24/7, une responsabilité de forecaster certifié, etc.

Ce document audite donc la **conformité technique** — le code respecte-t-il
les formats, unités, seuils et conventions réels que ces textes définissent
— pas une certification légale, qui n'est pas de ce ressort. Toute
affirmation "100% conforme OACI/OMM" au sens légal serait une fabrication
du même type que celles déjà trouvées et corrigées dans ce codebase
(ex. le faux `"ACF-UI-001 Production Certified"` dans
`earth_system_operations.py`).

## 1. Ce qui est déjà réel, cité et honnête (trouvé lors de cet audit)

- **`acf.aviation.icao.metar_decoder`/`taf_decoder`/`sigmet_decoder`** —
  parseurs réels, basés sur token/regex, citant explicitement ICAO Annexe 3
  / OMM n°306 (FM 15-XV METAR, FM 51-XV TAF, Appendice 6 Table A6-1A
  SIGMET). Chaque module documente honnêtement sa couverture de grammaire
  incomplète (ex. pas de RVR trend arrows, pas de groupes TX/TN TAF) plutôt
  que de prétendre une conformité totale. Historique documenté : ces 3
  décodeurs remplaçaient des stubs qui fabriquaient un résultat fixe
  indépendamment du texte réel — déjà corrigé avant cette session.
- **`acf.aviation.hazards.aviation_hazards.AVIATION_HAZARDS_REGISTRY`** —
  seuils réels et cités (EDR Ellrod pour CAT, LWC pour givrage, delta de
  vent pour microburst), références précises (ICAO Doc 9837, FAA AC 00-54).
- **`acf.science.encyclopedia.aerodynamics.isa_atmosphere`** — formules de
  l'atmosphère standard OACI (ICAO Doc 7488 / ISO 2533:1975) vérifiées
  numériquement contre les tables ISA standard (0/5000/11000/15000 m,
  <0.05% d'écart, voir `tests/data/golden/isa_standard_atmosphere.json`).
- **`ForecastDecisionEngine.assess_severe_weather_risk()`** (utilisé par
  ACF Workstation Phase 45) — cite honnêtement ses seuils comme "NOAA SPC
  Severe Weather Criteria" / "Doswell et al. (1996)", jamais présenté comme
  des critères SIGMET OACI (qui sont différents — voir §3 ci-dessous).
- **`acf.standards.cf_standard_names`** — table réelle CF Conventions
  (9 quantités, unités correctes).
- Lecture/écriture GRIB réelle via eccodes/cfgrib
  (`acf.data.grib_reader`, `acf.data.readers.grib_reader`,
  `acf.data.integration.grib_adapter`) — pas de parseur GRIB maison, la
  bibliothèque de référence porte elle-même les tables OMM complètes.

## 2. Corrections faites lors de cette passe

### 2.1 `acf.standards` — 4 fichiers sur 5 étaient des stubs vides

`grib2_tables.py`, `wmo_tables.py`, `ecmwf_parameters.py`,
`noaa_parameters.py` et `__init__.py` avaient tous un docstring
auto-généré identique ("Manage X tables logic and state
representations... Module functions and constants") sans **aucun**
contenu réel — vérifié via `grep` : jamais importés nulle part dans
`src/`/`tests/`. Même famille de bug que le faux
`"ACF-UI-001 Production Certified"` déjà trouvé/corrigé dans ce projet.

Corrigé :
- **`grib2_tables.py`** : vraies identités GRIB2 (discipline/catégorie/
  numéro, OMM n°306 Vol I.2 Table 4.2) pour les 9 quantités déjà présentes
  dans `cf_standard_names.py`.
- **`ecmwf_parameters.py`** : vrais paramId ECMWF (GRIB Table 128) pour
  les mêmes 9 quantités.
- **`noaa_parameters.py`** : vrais numéros de paramètre NCEP GRIB1 Table 2
  pour les mêmes 9 quantités.
- **`wmo_tables.py`** : laissé honnêtement vide (portée "tables de codes
  OMM" trop large pour être scopée et vérifiée sans risque cette
  passe-ci) — disclosure explicite plutôt que contenu inventé.
- Tests de régression ajoutés : `tests/test_standards_parameter_tables.py`
  (couvre les 3 tables peuplées + le cas "nom inconnu → None, jamais une
  valeur devinée").

### 2.2 Horloge du header ACF Workstation — heure locale → UTC réelle

`ACFWorkstation._update_clock()` (Phase 43, 2026-09-12) affichait l'heure
locale, honnêtement étiquetée "(local)" plutôt que de prétendre "UTC" sur
une valeur qui ne l'était pas. Mais l'Annexe 3 OACI §4.1 exige l'UTC
exclusivement pour toute information météorologique aéronautique. Corrigé
en utilisant `QDateTime.currentDateTimeUtc()` — une vraie conversion UTC,
pas juste un renoncement honnête sur une valeur fausse. Test de
régression : `test_header_clock_shows_genuine_utc_not_local_time`.

## 3. Écart identifié, disclosed, PAS corrigé cette passe (nécessite une décision produit)

`ForecastDecisionEngine.assess_severe_weather_risk()` (réutilisé par
l'écran "Alerts & Hazards" de l'ACF Workstation, Phase 45) applique des
seuils CAPE/cisaillement **NOAA SPC** (convention américaine pour les
outlooks convectifs CONUS) pour produire un `risk_level`
FAIBLE/MODÉRÉ/ÉLEVÉ/CRITIQUE. C'est honnêtement cité comme tel dans le
code (`references: ["NOAA SPC Severe Weather Criteria", "Doswell et al.
(1996)"]`) — **pas un problème de fabrication**. Mais ce n'est PAS la même
chose que les critères réels d'émission SIGMET de l'Annexe 3 Appendice 6
(qui sont des phénomènes catégoriels — orage sévère/turbulence sévère/
givrage sévère/etc. — rapportés par un forecaster ou un PIREP, pas dérivés
d'un seuil numérique de CAPE). Si l'écran "Alerts & Hazards" doit un jour
prétendre représenter un risque "façon SIGMET", il faudrait soit :
(a) le relabelliser clairement comme un indice de risque convectif de
style US, non-SIGMET (ce qu'il est réellement aujourd'hui), soit
(b) construire un moteur de critères SIGMET distinct basé sur l'Appendice
6 — un travail scientifique/produit réel, pas un renommage.
**Aucun changement fait ici** — décision produit à prendre, pas un bug.

## 3bis. Passe suivante (2026-09-12) : support BUFR/GRIB dans `acf.data.integration`

En vérifiant l'item §4.4 ci-dessous ("existe-t-il un vrai support BUFR ?"),
found : **`acf.data.integration.AdapterFactory`** (8 adaptateurs : NetCDF,
GRIB, BUFR, JSON, XML, HDF5, GeoTIFF, CSV) a un `load()` qui retourne
**inconditionnellement** un `Dataset` bien formé (`.variables`/
`.dimensions`/`.metadata` réels, mais silencieusement vides) quel que soit
le contenu réel du fichier - aucune bibliothèque de décodage utilisée nulle
part dans ces 8 classes. Non disclosed avant cette passe (contrairement au
stub déjà honnête `acf.importers.readers.bufr_reader.BufrReader`, corrigé
lors de l'audit du 2026-09-06). Vérifié via `grep` : `AdapterFactory`
n'a aucun appelant réel en dehors de ses propres tests - un risque
silencieux dormant, pas une donnée actuellement corrompue en production.

Corrigé pour les 2 formats directement réglementés OACI/OMM (GRIB2/BUFR
sont les formats d'échange standard du Manuel des codes OMM n°306) :
`BUFRAdapter.load()`/`GRIBAdapter.load()` posent maintenant
`dataset.metadata["is_real_data"] = False` + une raison explicite, au lieu
d'un `Dataset` silencieusement vide indiscernable d'un vrai fichier vide.
Tests de régression ajoutés (`test_load_honestly_discloses_it_is_not_a_real_decode`
dans `test_bufr_adapter.py`/`test_grib_adapter.py`).

**Non corrigé, disclosed** : les 6 autres adaptateurs
(NetCDF/CSV/JSON/XML/HDF5/GeoTIFF) ont le même bug non-disclosed, mais
hors du périmètre OACI/OMM strict de cette session - à traiter dans une
passe dédiée "intégrité de `acf.data.integration`", pas ici, pour ne pas
diluer le périmètre demandé.

## 3ter. Passe suivante (2026-09-12) : complétion de grammaire METAR/TAF

Suite de l'item §4.2 de la feuille de route (grammaire METAR/TAF
incomplète, disclosed dans les docstrings des décodeurs eux-mêmes) :

- **METAR** : indicateur de tendance RVR U/D/N (Annexe 3 / OMM n°306) -
  `_RVR_RE` ne le capturait pas du tout ; le champ `rvr[i]["trend"]`
  était absent. Ajouté (`U`/`D`/`N`/`None`), tests de régression ajoutés.
- **TAF** : groupes TX/TN (température max/min prévue, WMO FM 51-XV) -
  totalement absents avant cette passe : ces tokens tombaient dans le
  filet "unrecognized token, skip defensively" du décodeur, silencieusement
  ignorés, aucun champ ne les portait. Ajouté comme un scan dédié
  (`TAFReport.max_temp_c`/`max_temp_day`/`max_temp_hour` +
  `min_temp_c`/`min_temp_day`/`min_temp_hour`), tests de régression ajoutés
  (valeur présente ET absence honnête à `None`).

**Non traité cette passe, toujours disclosed** : groupes de cisaillement de
vent WS (TAF), remarques complètes (RMK), état de piste, remarques
givrage/cendres volcaniques — la liste "still incomplete" des docstrings
des 2 décodeurs a été mise à jour pour retirer les 2 items maintenant
fermés, en gardant les autres explicitement ouverts.

Tests : `tests/test_metar_decoder.py`/`test_taf_decoder.py` (47 tests
combinés, tous verts), plus vérification que les 2 consommateurs réels de
`METARReport`/`TAFReport` (`awci_messages_panel.py`, pont de qualité
`metar_report_quality()`) restent inchangés et verts.

## 3quater. Passe suivante (2026-09-12) : sweep UTC systématique (`datetime.now()`)

Suite de l'item §4.1 de la feuille de route. `grep -rn "datetime.now()"`
sur tout `src/acf` (15 fichiers) - la plupart sont des horodatages
internes (logs, cache, grilles temporelles `model4d`) hors du champ
"information météorologique aéronautique" que l'Annexe 3 régit. 3 vrais
bugs trouvés et corrigés :

- **`BriefingGenerator.generate_briefing()`** (`reports/briefings/`) —
  générait un "OFFICIAL METEOROLOGICAL BRIEFING" avec un horodatage
  `datetime.now().strftime("...UTC")` : `datetime.now()` sans fuseau est
  l'heure locale réelle de la machine, donc le suffixe "UTC" était un
  faux étiquetage sur CHAQUE briefing jamais généré — code réellement
  câblé (`gui/esoc/panel_manager.py`, `module_registry.py`,
  `science/query_engine.py`), pas mort. Ce fichier avait déjà eu un
  bug de fabrication corrigé une fois (un score de consensus de modèle
  en dur) — c'est un second bug distinct dans la même méthode. Corrigé,
  aucun test n'existait pour ce générateur avant cette passe -
  `tests/test_briefing_generator_utc.py` créé (preuve par mock
  local≠UTC qui aurait échoué contre l'ancien code, + vérification
  contre l'heure système réelle).
- **`acf.events.event.Event.start_time`** (le contrat d'événement
  météo générique du Prompt Maître §12-13) — son `default_factory`
  était `datetime.now()` (heure locale, sérialisée sans offset via
  `isoformat()` — un horodatage ambigu sur chaque événement météo réel
  détecté). Corrigé en `datetime.now(timezone.utc)`.
- **`detect_strong_wind_events()`/`detect_fog_favorable_events()`**
  (`events/detectors/`) — même fallback `valid_time or datetime.now()`,
  même correction. Vérifié qu'aucun appelant réel ne passe `valid_time`
  aujourd'hui (donc 100% des événements détectés utilisaient l'heure
  locale avant ce fix) et qu'aucun code ne compare `start_time`
  arithmétiquement à un autre datetime (seul `.isoformat()` le lit) -
  donc passer à un datetime "aware" ne casse rien.

Tests de régression ajoutés (`test_event_default_start_time_is_genuinely_utc_not_local`
dans `test_events.py`). 37 tests combinés verts (events + certification
engine + briefing generator).

**Portée du sweep** : ce grep couvrait `src/acf` en entier, pas
seulement `gui`/`aviation`/`awci` — les 12 autres fichiers utilisant
`datetime.now()` (catalog, model4d, logs/console ESOC, workspace) ont
été inspectés et jugés hors du champ "information météorologique
aéronautique/officielle" régi par l'Annexe 3 (horodatages internes de
fichiers/logs/grilles de calcul) - non modifiés.

## 3quinquies. Passe suivante (2026-09-12) : groupe de cisaillement de vent WS (TAF)

Dernier item du §4.2 restant à portée raisonnable : le groupe WS
numérique standard (WMO FM 51-XV / ICAO Annex 3, ex. "WS020/24045KT" =
cisaillement à 2000 ft, vent 240°/45kt). Ajouté à `_parse_wind_visibility_
weather_clouds()` (juste après le groupe de vent, avant la visibilité -
même ordre que le TAC réel) : `TAFForecastPeriod.wind_shear_height_ft`/
`wind_shear_direction_deg`/`wind_shear_speed_kt`. Variante américaine
"WS ALL WPTS" (cisaillement affectant toutes les pistes) explicitement
non couverte, disclosed. Tests de régression ajoutés (présence ET
absence honnête à `None`,+ non-confusion avec le groupe de visibilité
suivant). 38 tests METAR/TAF combinés verts, 3 consommateurs réels
vérifiés inchangés (`awci_messages_panel.py`, `live_source.py`,
`esoc_products_panel`).

## 4. Feuille de route réelle restante (non traitée cette passe, disclosed)

Périmètre trop vaste pour une seule passe honnête (130+ fichiers touchent
ICAO/OMM d'une façon ou d'une autre dans ce codebase) — liste priorisée
pour les passes suivantes, même discipline que le sweep Tier F/C/E déjà
documenté dans `docs/STATUS.md` :

1. **Unités & UTC** — ✅ le volet UTC est fait cette passe (§3quater) :
   sweep complet de tous les `datetime.now()` de `src/acf`, 3 bugs
   réels trouvés et corrigés (briefings, événements météo). Reste
   ouvert : audit des mélanges d'unités (kt vs m/s, ft vs m) sans
   conversion explicite - non fait cette passe.
2. **Grammaire METAR/TAF complète** — ✅ largement fait cette passe
   (§3ter, §3quinquies) : RVR trend U/D/N (METAR), TX/TN et le groupe WS
   numérique standard (TAF) fermés. Restent ouverts : variante
   américaine "WS ALL WPTS", remarques complètes (RMK), état de piste.
3. **`wmo_tables.py`** — scoper et peupler avec de vraies tables de codes
   OMM (ex. Common Code Table C-1 à C-14) une fois le périmètre exact
   défini.
4. **BUFR** — ✅ vérifié cette passe (§3bis) : aucun vrai décodeur BUFR
   nulle part dans ce codebase (dépendance manquante, ex. eccodes/
   pybufrkit) — disclosed, pas un travail à faire "sans risque" ici
   (nécessite d'ajouter une vraie dépendance). Un vrai support BUFR
   reste un travail de fonctionnalité à part entière, pas un audit.
5. **Décision produit §3 ci-dessus** — clarifier le statut SIGMET vs
   NOAA SPC de l'écran "Alerts & Hazards".
6. **Annexe 5 OACI (unités de mesure)** — vérifier la cohérence des
   unités utilisées dans les interfaces pilote-facing (ft vs m pour
   l'altitude, kt vs m/s pour le vent, cohérent avec l'usage
   opérationnel réel de l'aviation, par opposition aux unités SI
   internes de l'OMM) — audit non fait cette passe.
