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

## 4. Feuille de route réelle restante (non traitée cette passe, disclosed)

Périmètre trop vaste pour une seule passe honnête (130+ fichiers touchent
ICAO/OMM d'une façon ou d'une autre dans ce codebase) — liste priorisée
pour les passes suivantes, même discipline que le sweep Tier F/C/E déjà
documenté dans `docs/STATUS.md` :

1. **Unités & UTC, audit systématique** — un premier spot-check (aviation/
   awci, header clock) n'a rien trouvé d'autre de faux mais n'est pas
   exhaustif sur les ~30k lignes de `gui/`. Chercher tout usage de
   `datetime.now()` non-UTC dans du code affichant une donnée météo, et
   tout mélange d'unités (kt vs m/s, ft vs m) sans conversion explicite.
2. **Grammaire METAR/TAF complète** — compléter les groupes non couverts
   déjà disclosed dans les docstrings (RVR trend arrows, remarques
   complètes, TX/TN, groupes WS, état de piste).
3. **`wmo_tables.py`** — scoper et peupler avec de vraies tables de codes
   OMM (ex. Common Code Table C-1 à C-14) une fois le périmètre exact
   défini.
4. **BUFR** — vérifier s'il existe un vrai support BUFR (format
  d'observation OMM standard) dans ce codebase ou seulement GRIB — non
  vérifié cette passe.
5. **Décision produit §3 ci-dessus** — clarifier le statut SIGMET vs
   NOAA SPC de l'écran "Alerts & Hazards".
6. **Annexe 5 OACI (unités de mesure)** — vérifier la cohérence des
   unités utilisées dans les interfaces pilote-facing (ft vs m pour
   l'altitude, kt vs m/s pour le vent, cohérent avec l'usage
   opérationnel réel de l'aviation, par opposition aux unités SI
   internes de l'OMM) — audit non fait cette passe.
