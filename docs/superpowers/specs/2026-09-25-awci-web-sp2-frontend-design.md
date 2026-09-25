# AWCI Web — SP2 : front (coque, carte, observation satellite & foudre, inspecteur) — design

**Date :** 2026-09-25 · **Statut :** en revue · **Sous-projet :** 2 / 6
**Entrées :** spec SP1 (`2026-09-25-awci-web-sp1-data-science-design.md`), API `/api/v1/awci/*` (PR #6),
spec SP1C nuages (`2026-09-25-awci-web-sp1c-clouds-design.md`, prérequis des couches nuageuses),
maquette de référence fournie par l'utilisateur (dashboard « AWCI – Aviation Weather Complexity Index »,
thème sombre, copiée en `docs/reference/awci_web_mockup.jpg`).

## 1. Objectif et critères de succès

Fournir aux prévisionnistes un tableau de bord web **opérationnel** qui reprend la structure et
l'ambiance de la maquette, mais n'affiche **que des grandeurs réellement calculées ou observées**,
avec leur source, leur heure et leur statut scientifique.

**Critères de succès**
1. Toutes les zones de la maquette dont la donnée existe (voir §3) sont présentes et fonctionnelles ;
   aucune valeur fictive, aucune case vide « décorative ».
2. Changer d'échéance, de niveau ou de couche met la carte à jour en < 300 ms (p95, réseau local,
   cube déjà servi) ; premier affichage complet < 3 s.
3. Une cellule sans donnée n'est **jamais** colorée comme un risque faible (hachures + légende).
4. Toute observation (satellite, foudre) porte son heure d'observation et n'est jamais présentée
   comme synchrone de l'échéance de prévision affichée.
5. Navigable au clavier ; contraste ≥ 4,5:1 pour le texte ; aucune information portée par la couleur
   seule ; `prefers-reduced-motion` respecté ; responsive 1024 → 2560 px (la cible est le poste
   prévisionniste ≥ 1440 px ; < 1024 px : mise en page simplifiée carte + inspecteur).
6. Fonctionne sur un réseau interne sans accès Internet côté navigateur (polices, icônes, fond de
   carte embarqués ; imagerie relayée par le serveur).

**Hors périmètre SP2 :** vue volume 3D/4D (SP2B, spec `2026-09-25-awci-web-sp2b-3d4d-design.md`),
aéroports/METAR/TAF/SIGMET (SP3), route/coupe verticale/segments/exports
(SP4), ensemble ECMWF (SP5), multi-modèle (SP6), authentification, i18n autre que le français
(les libellés sont regroupés pour une traduction ultérieure).

## 2. Architecture

```
web/awci/                       (nouveau, Vite + React 18 + TypeScript strict)
  src/api/        client typé de /api/v1/awci (types générés à la main depuis les réponses réelles)
  src/state/      état d'URL (domaine, run, échéance, niveau, couche, point, fond, overlays)
  src/map/        MapLibre GL : fond vectoriel, raster champ, hachures, lignes de courant, overlays WMS
  src/panels/     barre haute, navigation, KPI, situation, inspecteur, évolution, profils
  src/theme/      tokens (sombre par défaut, clair), palette AWCI validée, statuts
  public/basemap/ Natural Earth 1:50m (côtes, pays) en GeoJSON simplifié (domaine public)
  public/fonts/   Fira Sans / Fira Code (SIL OFL), Lucide (ISC) en dépendance npm

src/acf/web/awci_app.py        sert le build statique sur "/" (même origine que l'API → pas de CORS)
src/acf/web/awci_router.py     + /summary, + /wms (relais EUMETView), + dewpoint dans /profile
```

Dépendances npm (runtime) : `react`, `react-dom`, `maplibre-gl`, `@tanstack/react-query`,
`lucide-react`, `@fontsource/fira-sans`, `@fontsource/fira-code`. Dev : `vite`, `typescript`,
`vitest`, `@testing-library/react`, `@playwright/test`, `eslint`. Pas de framework CSS : CSS modules
+ variables CSS (tokens).

### 2.1 État et données
- **L'URL est la source de vérité** : `?domain=&run=&step=&level=&layer=&lat=&lon=&base=&ov=`.
  Un lien reproduit exactement la vue ; le bouton « Maintenant » sélectionne le run le plus récent
  et l'échéance la plus proche de l'heure courante.
- TanStack Query : cache par clé de requête, `staleTime` = durée de vie d'un run (les cubes sont
  immuables) ; `/runs` rafraîchi toutes les 5 min ; relances 2× sauf 4xx.
- Préchargement des échéances voisines (±1) du champ courant pour un pas-à-pas instantané.

## 3. Correspondance maquette → réalité

| Zone de la maquette | Source réelle | SP |
|---|---|---|
| Logo, titre, sous-titre | statique | 2 |
| « SYSTEM ONLINE / ACF Data: Connected » | → **État des données** : run affiché, statut complete/partial, âge du run, état du relais satellite | 2 |
| « Last Update » | heure d'ingestion (manifest) | 2 |
| Area / Date & Time / Forecast / Model | domaine (`/domains`), validité UTC + pas ±3 h + « Maintenant », échéance +h, **« ECMWF IFS 0,25° »** | 2 |
| AWCI GLOBAL (jauge) | `/summary` : P95 de l'AWCI sur le domaine au niveau/échéance + classe | 2 |
| Turbulence / Convection / Icing / Wind Shear / Ceiling | `/summary` (définitions §5) ; plafond selon la définition OACI (SP1C) | 2 |
| KPI « Visibility » | **non prévu** : l'IFS Open Data ne fournit aucune visibilité ; les diagnostics publiés fondés sur l'humidité relative à 2 m (par ex. Doran et al. 1999, utilisé dans le RUC) sont peu fiables pour le brouillard et restent candidats pour la piste validation, pas pour l'affichage opérationnel ; carte remplacée par **« Cb / TCU »** (SP1C) ; visibilité **observée** (METAR) en SP3 | 2/3 |
| Map Layers (AWCI, Turbulence, Convection, Icing, Wind Shear, Ceiling, Precipitation) | couches du cube SP1 | 2 |
| **Nuages** (demande prioritaire) | couches SP1C : couverture par étage (bas/moyen/haut), genre probable par étage, plafond OACI, classe convective, sommets, T_e, condensat ; panneau **Nuages** §7 | 2 |
| Snow & Icing Accumulation | SP1C : `snowfall_mm`, `snow_depth_cm`, `freezing_precip_mm` (cumul verglaçant, pas d'épaisseur de glace) | 2 |
| Dust / Sand | proxy poussière du cube SP1 (HYPOTHESIS) + MTG Dust RGB observé | 2 |
| Volcanic Ash | MSG Ash RGB observé (overlay) ; SIGMET VA et avis VAAC en SP3 | 2/3 |
| Map Layers « Satellite » | EUMETView MTG FCI (IR 10,5 µm, GeoColour, Dust RGB, Fog RGB, **Cloud Type RGB, Cloud Phase RGB**) + MSG (Convection RGB, **Ash RGB, Cloud Top Height, Cloud Mask, RDT**), relais `/wms` | 2 |
| Map Layers « Lightning » | EUMETView MTG LI Accumulated Flash Area, relais `/wms` | 2 |
| Map Layers « Radar » | **non proposé** (couverture quasi nulle Afrique du Nord, licence) | — |
| Map Layers « Airports », « Flight Routes » | SP3 / SP4 | 3/4 |
| Map Layers « Model Disagreement » | SP6 | 6 |
| Lignes blanches (vent) | **lignes de courant réelles** calculées côté client depuis `u`,`v` du niveau | 2 |
| 2D / 3D / 4D | 2D + lecture animée en SP2 ; **3D (voxels réels, relief, exagération affichée) et 4D (3D animée sur les échéances) en SP2B** — décision argumentée dans sa spec | 2/2B |
| Curseur temporel, ▶, « +12h » | échéances 0→72 h (pas manquants grisés), lecture 1 pas/s, respect reduced-motion | 2 |
| Légende AWCI verticale | palette validée §4 + entrée « sans donnée » hachurée | 2 |
| Current Situation | classe du P95, dangers principaux triés (KPI ≥ seuil), zone = domaine, altitude = niveau(x) où le P95 AWCI est maximal (depuis `/summary` par niveau), validité | 2 |
| Model Agreement / Confidence | **« Non disponible — mono-modèle »** (SP5/SP6) | 5/6 |
| Airport Complexity | SP3 | 3 |
| Vertical Cross Section, Flight Route Analysis | SP4 | 4 |
| Atmospheric Profile | `/profile` au point choisi : T, Td (serveur), vent, en fonction de l'altitude géopotentielle réelle (`gh`), niveaux sous le relief omis | 2 |
| Time Evolution (Global / Route / Airport) | **Point** (`/timeseries`) et **Domaine** (`/summary` sur toutes les échéances) ; Route/Airport en SP4/SP3 | 2 |
| AWCI Vertical Profile (barres + empilement 3D) | barres par niveau depuis `/profile` (SP2) ; colonne 3D au point, mêmes données (SP2B) | 2/2B |
| Recent Alerts / Latest Updates / Quick Actions | SP3 (alertes SIGMET/METAR) ; « Latest Updates » = journal des runs ingérés (2) ; « Save Scenario » = vues nommées (état d'URL, stockage local du navigateur) en SP2 ; « Generate Report », « Export Data », « Route Analysis » en SP4 | 2/3/4 |
| Navigation « Model Comparison », « Uncertainty » | SP6, SP5 | 5/6 |
| Navigation « API » | page de la documentation OpenAPI de FastAPI + navigateur du `/registry` (unités, équations, statuts) | 2 |
| Utilisateur « sfoura / Meteorologist » | **non affiché** (pas de comptes en V1) | — |
| Emojis | remplacés par Lucide (SVG) | 2 |

Les emplacements SP3/SP4/SP5/SP6 existent dans la grille mais ne sont **pas rendus** tant que leur
donnée n'existe pas : la grille se réorganise (pas de carte vide « bientôt disponible »).

## 4. Couleur

- **Palette AWCI (6 classes ordonnées, thème sombre)** — validée par
  `dataviz/scripts/validate_palette.js --ordinal --mode dark --surface "#0b1220"` (toutes vérifications
  PASS : luminance monotone, écarts ΔL ≥ 0,06, extrémité faible ≥ 2:1 sur le fond) :
  Very Low `#854494` · Low `#b94c90` · Moderate `#e45d84` · High `#ff7f6c` · Very High `#ffa85d` ·
  Extreme `#ffd368`. La **luminance croît avec la sévérité** (le plus sévère est le plus saillant sur
  fond sombre) ; les classes sont toujours accompagnées de leur libellé texte (légende, inspecteur,
  badges). La variante thème clair sera dérivée et validée avec `--mode light` à l'implémentation.
  La palette arc-en-ciel de la maquette est volontairement abandonnée (non perceptuellement uniforme,
  fausses frontières, illisible en daltonisme).
- **Couches physiques continues** (vent, CAPE, base nuageuse, précipitations) : rampes séquentielles
  mono-teinte validées de la même façon, avec échelle et unité affichées.
- **Statuts** (badges de sévérité des KPI) : palette statut réservée (bon / attention / sérieux /
  critique), toujours icône + texte.
- **Sans donnée** : transparent + hachures 45° à 2 px, entrée de légende dédiée.

## 5. Nouvelles routes serveur (petites, testées)

### 5.1 `GET /api/v1/awci/summary?domain=&run=&step=&level=`
Calculé à la volée depuis le cube (tranches 2D, < 50 ms), mis en cache par (run, step, level).
Chaque indicateur déclare définition, unité, statut dans `/registry` :

| Clé | Définition | Unité | Seuils de badge |
|---|---|---|---|
| `awci_p95` | 95ᵉ centile de `awci` (cellules non nulles) + classe `LEVEL_THRESHOLDS` | 0–100 | classes AWCI |
| `turbulence_area_pct` | % des cellules valides avec `cat_category` ≥ 2 (Moderate) | % | ≥ 5 attention, ≥ 15 sérieux, ≥ 30 critique |
| `convection_area_pct` + `mucape_max` | % des cellules avec `mucape` ≥ 1000 J/kg ; max | %, J/kg | idem |
| `icing_area_pct` | % des cellules valides avec `icing_potential` = 1 au niveau | % | idem |
| `shear_p95` | 95ᵉ centile de `vertical_shear` | s⁻¹ (affiché ×10⁻³) | ≥ 5×10⁻³ attention, ≥ 8×10⁻³ sérieux |
| `heavy_precip_area_pct` | % avec `precip_class` ≥ 3 (OMM : forte) | % | idem aires |
| `low_ceiling_area_pct` | % avec `ceiling_m` (plafond OACI, SP1C) < 304,8 m (1000 ft) | % | idem aires |
| `cb_area_pct` | % des cellules avec `convective_class` ≥ 3 (Cb, SP1C) | % | idem aires |
| `cloud_cover_bias_mean` | moyenne de la couverture diagnostiquée − `tcc` IFS (contrôle SP1C) | — | \|biais\| > 0,15 → « dégradé » |
| `valid_cells_pct` | % de cellules non nulles au niveau (masque relief) | % | — |
| `awci_p95_by_level` | P95 AWCI pour chaque niveau (pour « altitude principale ») | 0–100 | — |

Les seuils de badge (aires 5/15/30 %, cisaillement 5/8×10⁻³ s⁻¹) sont des **choix ACF, statut
HYPOTHESIS**, exposés par `/registry` ; les grandeurs elles-mêmes sont des statistiques exactes du cube.

### 5.2 `GET /api/v1/awci/wms?layer=&time=&bbox=&width=&height=`
Relais **en lecture seule** vers `https://view.eumetsat.int/geoserver/wms` (WMS 1.3.0, EPSG:3857).
- Liste blanche de couches : `mtg_fd:ir105_hrfi`, `mtg_fd:rgb_geocolour`, `mtg_fd:rgb_dust`,
  `mtg_fd:rgb_fog`, `mtg_fd:rgb_cloudtype`, `mtg_fd:rgb_cloudphase`, `msg_fes:rgb_convection`,
  `msg_fes:rgb_ash`, `msg_fes:cth`, `msg_fes:clm`, `msg_fes:rdt`, `mtg_fd:li_afa` (disponibilité et pas
  de temps vérifiés dans les capacités du 2026-09-25 : FCI 10 min, MSG 15 min). Tout autre nom → 400.
- `bbox` 4 flottants bornés à l'emprise Web-Mercator, `width`/`height` ≤ 2048 ; `time` ISO-8601
  optionnel (absent = dernière image, dont l'heure est lue dans les capacités et renvoyée en
  en-tête `X-AWCI-Observed-At`).
- Cache disque (clé = requête normalisée), TTL 5 min pour la dernière image, 24 h pour une heure
  explicite ; délai d'attente 20 s ; 502 + message si EUMETView est indisponible.
- `GET /api/v1/awci/wms/times?layer=` : les N dernières heures disponibles (animation foudre 1 h).
- Attribution « © EUMETSAT » renvoyée et affichée. Politique de données EUMETSAT à confirmer pour
  l'exploitation (l'ONM, SMHN membre de l'OMM, dispose en principe d'un accès aux données essentielles).

### 5.3 `/profile` : ajout de `dewpoint_k` par niveau
Calculé par `acf.awci.ops.thermo.dewpoint_k_from_vapor_pressure(vapor_pressure_hpa(q, p))`
(même formule que SP1, testée), pour ne jamais dupliquer de science côté navigateur.

## 6. Carte

- **Fond** : vectoriel sombre embarqué (océan, terres, côtes, frontières, graticule 5°) —
  Natural Earth 1:50m, domaine public ; option **« Satellite »** = MTG GeoColour relayé.
- **Champ** : `/field?format=f32` → `Float32Array` → canvas (1 px par cellule, palette par classe ou
  rampe continue) → source `image` MapLibre aux bornes `X-AWCI-Lats/Lons` (demi-cellule incluse) ;
  rééchantillonnage « nearest » (pas d'interpolation qui inventerait des valeurs entre les points
  de grille) ; opacité réglable.
- **Hachures** sur les cellules `NaN`.
- **Lignes de courant** du vent au niveau : intégration RK2 sur la grille `u`,`v` réelle,
  densité adaptée au zoom ; animation désactivée en reduced-motion.
- **Overlays d'observation** : satellite et foudre au-dessus du fond, sous le champ ou au-dessus
  (réglable), badge « Observé HH:MM UTC (il y a N min) ».
- **Clic** = point d'intérêt (URL `lat`,`lon`) → marqueur + inspecteur ; clic hors domaine = message.

## 7. Panneaux

- **Barre haute** : titre, sélecteurs, état des données, heure UTC courante.
- **Navigation latérale** : sections de la maquette ; les entrées SP3–SP6 absentes tant que non livrées.
- **Rangée KPI** : jauge AWCI P95 + 6 cartes (§5.1), chacune cliquable → active la couche
  correspondante sur la carte.
- **Situation actuelle**, **Accord des modèles** (non disponible, explicite).
- **Inspecteur de point** : AWCI + classe, décomposition (barres horizontales triées, points AWCI),
  `missing_inputs` et `present_weight` (« calculé sur 90 % des poids »), valeurs des couches avec
  unités, statuts scientifiques, provenance (run, échéance, validité, © ECMWF).
- **Évolution temporelle** : courbe AWCI au point (et P95 domaine), échéance courante marquée,
  hover crosshair + tooltip ; tableau de données accessible.
- **Profil vertical AWCI** : barres par niveau (FL + hPa), niveaux sous le relief marqués « sous le sol ».
- **Profil atmosphérique** : T et Td vs altitude géopotentielle, barbules ou flèches de vent,
  bandes de fraction nuageuse par niveau (SP1C) en marge.
- **Nuages** (au point, `/clouds`) : colonne verticale en FL avec les couches (base–sommet ± demi-
  intervalle, octas, genre probable, espèces), repères d'étage (σ ECMWF) et des étages OMM de
  référence, plafond OACI, sommet convectif et T_e, ligne « modèle : BKN030 OVC080 CB », `tcc` IFS
  et biais ; évolution temporelle des genres par étage (bandes) pour la variabilité temporelle.
  Libellé permanent « genre probable — diagnostic modèle, statut HYPOTHESIS ».
- **Comparaison modèle / observation** : balayage (swipe) entre `cloud_top_teff_k` (prévision) et
  MTG IR 10,5 µm (observé), heures de validité et d'observation affichées côte à côte.

Tous les graphiques suivent le skill `dataviz` (un seul axe, traits fins, hover par défaut, légende
si ≥ 2 séries, table alternative).

## 8. États

| Cas | Rendu |
|---|---|
| Chargement | squelettes aux dimensions finales (pas de saut de mise en page) |
| Aucun run | page d'état : « Aucun run ingéré pour ce domaine » + commande d'ingestion |
| Run partiel | bandeau + pas manquants grisés et non sélectionnables |
| 404 échéance / 503 cube | message dans la zone concernée, le reste de l'interface reste utilisable |
| Relais satellite en échec | overlay désactivé + message, la prévision reste affichée |
| Point hors domaine | toast explicite |
| Données anciennes (run > 18 h) | badge « Run ancien » dans l'état des données |

## 9. Accessibilité et clavier
←/→ échéance, ↑/↓ niveau, L couches, Espace lecture/pause, Échap ferme les panneaux ; focus visible ;
libellés ARIA sur tous les boutons-icônes ; zones `aria-live` polies pour les changements d'état ;
texte ≥ 12 px (données) / 14 px (corps).

## 10. Tests

| Niveau | Contenu |
|---|---|
| Python | `/summary` (définitions exactes sur la fixture, NaN exclus, cache), `/wms` (liste blanche, bornes, cache, 502, en-tête d'heure — requêtes EUMETView simulées ; un test réseau réel opt-in), `dewpoint_k` |
| Vitest | décodage f32 + en-têtes, application palette/hachures, état d'URL (aller-retour), intégration lignes de courant (champ uniforme → lignes droites), formatage unités/FL/UTC |
| Testing Library | panneaux : états chargement/erreur/vide/partiel, inspecteur (`missing_inputs`, décomposition), KPI cliquable |
| Playwright | `acf-awci-web` servant la fixture réelle : parcours échéance/niveau/couche/clic point, clavier, reduced-motion ; captures 1440 et 1920 px comparées **structurellement** à la maquette (zones présentes) et comparaison visuelle de non-régression |

## 11. Risques

| Risque | Mitigation |
|---|---|
| Disponibilité/latence EUMETView | cache serveur, dégradation propre, heure d'observation affichée |
| Licence EUMETSAT pour usage opérationnel | à confirmer par l'ONM ; overlays désactivables par configuration |
| Taille du bundle (MapLibre ~200 Ko gz) | découpage du code par panneau ; cible < 600 Ko gz au total |
| Lisibilité de la palette pour des prévisionnistes habitués au rouge = sévère | libellés texte systématiques ; retour utilisateur prévu avant figer |
| Maquette plus riche que la donnée | correspondance §3 explicite ; aucun élément fictif |
