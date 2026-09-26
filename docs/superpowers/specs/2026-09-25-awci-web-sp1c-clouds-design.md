# AWCI Web — SP1C : nuages (couverture par niveau, étages, genres, espèces, variabilité) et champs étendus — design

**Date :** 2026-09-25 · **Statut :** implémenté (écarts de mise en œuvre intégrés) · **Sous-projet :** 1C (s'insère entre SP1 et SP2)
**Entrées :** spec et code SP1 (`src/acf/awci/ops/`, PR #6), index réels ECMWF Open Data
(`oper` et `enfo`, run 2026-09-25 06Z, consultés le 2026-09-25), capacités WMS EUMETView du même jour,
maquette `docs/reference/awci_web_mockup.jpg`.

## 0. Pourquoi un sous-projet dédié, et feuille de route révisée

La prévision du **type de nuage par étage** est demandée comme fonction centrale. Elle nécessite de
nouvelles entrées (ingestion), une science propre (diagnostics), de nouvelles couches (cube) et une
API ; c'est un travail « données & science » du même ordre que SP1, qui doit précéder le front pour
que SP2 affiche des nuages réels dès sa première version.

| SP | Contenu | Statut |
|---|---|---|
| 1 | ingestion IFS, diagnostics aviation, moteur AWCI, API | livré (PR #6) |
| **1C** | **nuages + champs étendus (neige, pluie verglaçante, OLR, condensat)** — ce document | nouveau |
| 2 | front 2D : coque, carte, satellite, foudre, inspecteur, **panneau Nuages** | spec révisée |
| **2B** | **vue volume 3D et 4D** (spec `2026-09-25-awci-web-sp2b-3d4d-design.md`) | nouveau |
| 3 | aéroports, METAR/TAF, SIGMET (dont **cendres volcaniques**), alertes ; validation nuages vs METAR | inchangé + VA |
| 4 | route, coupe verticale (avec étages nuageux), rapports, exports | inchangé |
| 5 | ECMWF ENS : probabilités, **variabilité des nuages** (§7) | enrichi |
| 6 | GFS, accord multi-modèle | inchangé |
| V | validation (piste parallèle) : nuages vs METAR, RDT, foudre | enrichi |

## 1. Ce que les données permettent réellement (vérifié)

**IFS HRES `oper` et ENS `enfo` (50 membres), mêmes paramètres :**
- par niveau (1000, 925, 850, 700, 600, 500, 400, 300, 250, 200, 150, 100, 50, 10 hPa) :
  `t q r u v w d vo gh` (et `z`) ;
- surface : `tcc`, `tcw`, `tcwv`, `ttr`, `ssr`, `ssrd`, `str`, `strd`, `tp`, `tprate`, `sf`, `sd`,
  `rsn`, `asn`, `ptype`, `mucape`, `skt`, `100u`, `100v`, `2t`, `2d`, `sp`, `msl`, `10fg`, `lsm`…

**Absents de l'Open Data** (et donc jamais présentés comme disponibles) : couverture nuageuse par
niveau (`cc`), eau et glace nuageuses (`clwc`, `ciwc`), couvertures basse/moyenne/haute
(`lcc`/`mcc`/`hcc`), base nuageuse IFS (`cbh`), précipitations convectives (`cp`), visibilité.

Conséquence : la couverture par niveau et le genre **se diagnostiquent** à partir de l'humidité, de la
température, du vent et de la stabilité, avec des méthodes publiées ; **le `tcc` de l'IFS sert de
contrôle de cohérence** à chaque échéance (§3.3). Tous les produits nuageux sont des
**diagnostics modèle**, jamais des observations.

**Observations nuageuses disponibles (EUMETView, WMS public, images colorées) :**
`msg_fes:cth` (hauteur du sommet, 15 min), `msg_fes:clm` (masque nuageux), `msg_fes:rdt` (orages à
développement rapide, NWC SAF), `mtg_fd:rgb_cloudtype`, `mtg_fd:rgb_cloudphase` (10 min),
`msg_fes:rgb_ash` (cendres volcaniques). Ce sont des images : elles servent au contrôle visuel
(overlays SP2) ; la validation **quantitative** se fait contre les groupes nuageux METAR (SP3) et,
si l'ONM obtient un accès, les produits NWC SAF numériques (Data Store EUMETSAT, compte requis).

## 2. Ingestion : paramètres ajoutés

Ajoutés à `SFC_PARAMS` : `tcw`, `tcwv`, `ttr`, `sf`, `sd`, `rsn`, `tp`. Coût : 7 messages par
échéance en plus des 108 actuels (+6,5 %). Les niveaux restent les 12 niveaux SP1 (1000→100 hPa) : 50
et 10 hPa n'apportent rien sous la tropopause subtropicale. Les grandeurs **cumulées** (`ttr`, `sf`,
`tp`) sont différenciées entre échéances consécutives : l'échéance 0 et une échéance dont la
précédente manque donnent `null`, jamais 0.

## 3. Science

Toutes les équations ci-dessous sont publiées (référence donnée) ; les **seuils** qui ne proviennent
pas d'une définition normative sont des **choix ACF**, regroupés dans un profil versionné
`config/awci/clouds/cloud-v1.json`, exposés par `/registry` avec le statut **HYPOTHESIS**.

### 3.1 Humidité relative pour la nébulosité
Le `r` de l'IFS est défini par l'ECMWF par rapport à l'eau au-dessus de 0 °C, à la glace au-dessous de
−23 °C, avec une interpolation quadratique entre les deux (base de paramètres ECMWF, param 157 ; IFS
Documentation, Part IV « Physical Processes », chapitre sur les nuages). C'est la saturation utilisée par le schéma nuageux de l'IFS : il
est donc **adapté à la nébulosité** (et reste exclu du givrage, qui exige l'eau liquide, cf. SP1).

### 3.2 Fraction nuageuse par niveau — Sundqvist et al. (1989)
Sundqvist, Berge & Kristjánsson (1989), *Mon. Wea. Rev.* 117, 1641–1657 :

  C = 1 − √[(1 − RH) / (1 − RHc)] pour RH ≥ RHc ; C = 0 sinon ; C = 1 si RH ≥ 1,

avec RH en fraction et RHc l'humidité critique. RHc dépend de l'étage (§3.4) : `RHc_low`,
`RHc_mid`, `RHc_high` sont des paramètres du profil. Valeurs initiales : 0,80 / 0,70 / 0,70, puis
**calibration reproductible** par `tools/awci/calibrate_cloud_rhc.py`, qui minimise l'erreur
quadratique entre la couverture totale diagnostiquée (§3.3) et le `tcc` IFS sur des runs réels
archivés. Le résultat (valeurs, runs utilisés, erreur) est écrit dans le profil. Limite déclarée :
avec un espacement de 25 à 100 hPa entre niveaux, une couche fine (Sc de 200 m, Ci fin) peut échapper
au diagnostic.

### 3.3 Recouvrement et couvertures par étage — maximum-aléatoire
Geleyn & Hollingsworth (1979), *Beitr. Phys. Atmos.* 52, 1–16 ; forme de Räisänen (1998),
*Q. J. R. Meteorol. Soc.* 124 : sur les niveaux k ordonnés du haut vers le bas,

  C_tot = 1 − ∏_k (1 − max(C_k, C_{k−1})) / (1 − C_{k−1}),

les niveaux nuageux adjacents se recouvrant au maximum et les couches séparées par un niveau clair
se recouvrant aléatoirement. La même formule restreinte aux niveaux d'un étage donne
`cloud_cover_low/mid/high`.

**Contrôle de cohérence** (à chaque échéance, par cellule) : `cloud_cover_bias = C_tot − tcc`.
Sa moyenne et son écart-type sur le domaine sont inscrits au manifest et affichés dans l'état des
données. Un biais moyen supérieur à 0,15 en valeur absolue passe le statut nuageux du run en
« dégradé » (seuil ACF).

### 3.4 Étages
- **Couvertures par étage** : bornes de l'ECMWF pour `lcc`/`mcc`/`hcc`, en σ = p/p_s :
  bas σ > 0,8 ; moyen 0,45 < σ ≤ 0,8 ; haut σ ≤ 0,45 (base de paramètres ECMWF, params 186–188).
  Ces bornes suivent le relief, ce qui est indispensable au-dessus de l'Atlas et du Hoggar.
- **Affichage** : chaque couche porte aussi sa base et son sommet en pieds et en FL (ISA, SP1) pour
  la lecture pilote. Les étages de l'Atlas international des nuages (OMM-N° 407 : bas 0–2 km, moyen
  2–7 km en région tempérée et 2–8 km en région tropicale, haut au-dessus) sont affichés comme
  **référence**, pas comme critère de calcul : ils se chevauchent et dépendent de la latitude.

### 3.5 Couches, bases, sommets, plafond
- **Couche** = suite de niveaux contigus au-dessus du sol avec C ≥ 1/8 (1 octa, seuil de
  déclaration FEW). Une couche qui traverse une borne d'étage est attribuée à l'étage de sa base,
  comme dans l'Atlas.
- **Base et sommet** : altitude géopotentielle `gh` du niveau le plus bas et du plus haut de la
  couche, moins l'altitude du relief ACF (déjà utilisée en SP1). La résolution verticale est celle
  des niveaux : l'incertitude (demi-intervalle) est renvoyée avec chaque valeur.
- **Base de la couche basse** : le minimum de la LCL (SP1, Espy) et de la base diagnostiquée pour une
  couche basse convective. Pour une couche stratiforme, c'est la base diagnostiquée qui fait foi.
- **Couverture en octas** : arrondi de 8·C ; FEW 1–2, SCT 3–4, BKN 5–7, OVC 8 (OACI Annexe 3,
  Appendice 3).
- **Plafond** (`ceiling_m`) : hauteur au-dessus du sol de la base de la couche la plus basse, sous
  6 000 m, couvrant plus de la moitié du ciel (BKN ou OVC). C'est la **définition OACI** (Annexe 2,
  Définitions). Pas de couche qualifiante : `null`, avec la mention « pas de plafond ».

### 3.6 Température du sommet — rayonnement IR sortant
OLR moyen sur l'intervalle Δt : OLR = −[ttr(t) − ttr(t−Δt)] / Δt, en W m⁻², avec `ttr` cumulé
en J m⁻² et négatif vers le haut (convention ECMWF). On en tire la température d'émission
effective T_e = (OLR / σ)^(1/4), avec σ = 5,670 374 419 × 10⁻⁸ W m⁻² K⁻⁴ (CODATA 2018, valeur
exacte). T_e est une grandeur **large bande** : elle est affichée comme telle et **comparée
visuellement** au canal IR 10,5 µm de MTG (overlay SP2). Elle n'en est pas une simulation.

### 3.7 Condensat colonne
`column_condensate = tcw − tcwv` (kg m⁻²) : eau liquide et glace nuageuses, pluie et neige
(définitions ECMWF de `tcw` et `tcwv`). C'est une **sortie directe de l'IFS**, le seul signal
d'épaisseur optique disponible. Elle distingue les voiles minces (Ci) des nuages épais (Ns, Cb).

### 3.8 Convection : ascendance de particule et sommet
- **Particule** : issue du niveau valide le plus bas (surface : `2t`, `2d`, `sp`). On la soulève à
  sec jusqu'au niveau de condensation (Bolton 1980, éq. 15, depuis T et Td), puis selon la pseudo-adiabatique, en
  conservant θe (Bolton 1980, SP1). À chaque niveau, on résout T tel que
  θe_sat(T, p) = θe_particule, par **bissection** vectorisée (θe_sat croît avec T ; 40 itérations,
  précision < 10⁻⁹ K ; borne haute telle que e_s ≤ p/2 pour garder q_s fini).
  La flottabilité utilise la température virtuelle.
- **Niveau d'équilibre (EL)** : le plus haut niveau où la particule est plus chaude que
  l'environnement. On en tire `convective_top_m` et `convective_top_temp_k`.
- **Profondeur convective** : EL − base (LCL).
- **CAPE** : le `mucape` de l'IFS reste la référence d'intensité. L'EL de la particule de surface
  peut donc différer de celui de la particule la plus instable ; c'est une limite déclarée, la
  particule de surface étant le choix classique pour la convection à base basse.

### 3.9 Genres (10 genres OMM) — règles diagnostiques
Chaque couche reçoit **un** genre. Les critères reposent sur des grandeurs physiques :
- étage de la base ;
- épaisseur ;
- couverture ;
- **instabilité potentielle** dans la couche (∂θe/∂z < 0 : cumuliforme ; ≥ 0 : stratiforme ;
  définition du glossaire AMS) ;
- précipitation (`tprate`, `ptype`) ;
- condensat colonne ;
- convection (§3.8).

| Genre | Critère (seuils du profil, HYPOTHESIS sauf mention) |
|---|---|
| **Cb** | `mucape` ≥ CAPE_min ET condensat colonne IFS ≥ 0,01 kg m⁻² (sans nuage dans le modèle, pas de nuage convectif ; vaut pour toutes les classes convectives) ET profondeur convective ≥ D_cb ET T sommet ≤ T_glace (−20 °C initial : début de glaciation des sommets convectifs observé vers −20 à −25 °C, Rosenfeld & Lensky 1998, *BAMS* 79, 2457–2476) |
| **Cu** (dont TCU) | convection présente, mais critères Cb non atteints ; espèce §3.10 |
| **Ns** | couche stratiforme de base basse ou moyenne, épaisseur ≥ D_ns, précipitation continue au sol (`tprate` ≥ 0,1 mm h⁻¹ et `ptype` ≠ 0 ; seuil choix ACF) |
| **St** | base basse ≤ H_st (base type < 600 m, OMM-N° 407), stable |
| **Sc** | base basse, au-dessus de H_st ou potentiellement instable |
| **As** | base moyenne, stable, épaisseur ≥ D_as, pas de précipitation continue |
| **Ac** | base moyenne, mince ou potentiellement instable |
| **Cs** | base haute, stable, couverture ≥ 5/8 |
| **Ci** | base haute, couverture < 5/8 |
| **Cc** | base haute, potentiellement instable, mince |

L'**Atlas OMM** définit les genres par leur **aspect visuel**. Aucun modèle ne les « voit » :
l'interface les nomme donc « genre probable (diagnostic modèle) ». Une règle qui s'applique mal
(couche trop mince pour la résolution verticale, par exemple) donne « indéterminé », jamais un genre
choisi par défaut.

### 3.10 Espèces diagnosticables (sous-ensemble honnête)

| Espèce | Grandeur physique | Pertinence aviation |
|---|---|---|
| Cb *capillatus* / *calvus* | T sommet ≤ T_cap (−38 °C : congélation homogène, Pruppacher & Klett 1997, *Microphysics of Clouds and Precipitation*) / au-dessus | enclume glacée, grêle, foudre |
| Cu *congestus* (TCU) / *mediocris* / *humilis* | profondeur convective (seuils du profil) | TCU = groupe METAR |
| Ac, Sc, Cc *castellanus* | instabilité conditionnelle au-dessus de la base : ∂θe*/∂z < 0 (θe saturante) | convection à base élevée, orages secs |
| Ac, Sc, Cc *lenticularis* | onde orographique : couche stable (N² > 0), vent transverse au relief ≥ U_min, nombre de Froude Fr = U/(N·h) dans [Fr_min, Fr_max], pente du relief ACF | turbulence d'onde de montagne |
| St, Cu *fractus* | couche basse sous précipitation, vent 10 m ≥ U_fra | plafond très bas et variable |
| St, Cs *nebulosus* | couverture ≥ 7/8 et faible variance spatiale (voisinage 3×3) | voile uniforme |
| Ci *spissatus* | condensat colonne ≥ Q_spi avec un seul étage nuageux, le haut | Ci dense, IMC |

**Non diagnosticables** à 0,25° et aux niveaux standard, donc **jamais affichées** :
- *fibratus*, *uncinus*, *floccus*, *stratiformis* (texture) ;
- *volutus* (rouleaux) ;
- les **particularités supplémentaires** (*mamma*, *arcus*, *tuba*, *virga*, *asperitas*) ;
- les **variétés** (*opacus*, *translucidus*, *undulatus*…), à une exception documentée près :
  *translucidus*/*opacus* de jour seulement, par le rapport ssr/ssrd, et en statut EXPERIMENTAL.

### 3.11 Neige, pluie verglaçante (« Snow & Icing Accumulation » de la maquette)
- `snowfall_mm` : différence de `sf` entre échéances (m d'équivalent en eau → mm).
- `snow_depth_cm` = `sd` · ρ_eau / `rsn` · 100 (`sd` en m d'équivalent en eau, `rsn` masse volumique
  de la neige en kg m⁻³, ρ_eau = 1000 kg m⁻³).
- `freezing_precip_mm` : différence de `tp` sur l'intervalle, lorsque `ptype` ∈ {3 pluie
  verglaçante, 12 bruine verglaçante} (codes ECMWF, déjà dans SP1) aux deux bornes de l'intervalle.
  C'est un **cumul de précipitation verglaçante**. Aucune épaisseur de glace accrétée n'est estimée :
  il faudrait un modèle d'accrétion et l'eau liquide, indisponibles.

## 4. Couches ajoutées au cube (registre `LAYERS`)

Par niveau (`level`, `lat`, `lon`) :
- `cloud_fraction` (0–1) ;
- `cloud_genus` (code OMM 0500 du genre de la couche à laquelle appartient le niveau ;
  −1 = clair, −2 = indéterminé, `NaN` = sous le relief) ;
- `potential_instability` (∂θe/∂z, K km⁻¹).

Surface (`lat`, `lon`) :
- `cloud_cover_low`, `cloud_cover_mid`, `cloud_cover_high`, `cloud_cover_total_diag` ;
- `tcc` (IFS brut) et `cloud_cover_bias` ;
- `ceiling_m` ;
- `lowest_cloud_base_m` et `highest_cloud_top_m` ;
- `genus_low`, `genus_mid`, `genus_high` : genre du nuage **présent** dans l'étage (plus forte
  couverture à l'intérieur de l'étage, quelle que soit l'altitude de la base ; Cb/TCU sur tous les
  étages que la colonne convective traverse). L'étage de la base, au sens de l'Atlas, reste donné
  couche par couche par `/clouds` ;
- `surface_height_m` : hauteur de la **surface du modèle IFS**, utilisée pour toutes les hauteurs au-dessus
  du sol. Elle vient de l'équation hypsométrique à partir de `sp` et du niveau valide le plus bas :
  z_s = gh_k − (R_d·T̄_v/g)·ln(p_s/p_k), cohérente avec le masque sous le relief et la particule, et vaut
  ±2 m sur mer. Le relief SRTM15+ embarqué est une grille à 1°, dont la bathymétrie déborde
  jusqu'à des dizaines de km dans les terres (−677 m près d'Alger) ; il ne sert plus pour les nuages ;
- `cloud_species` (par niveau) : espèces de la couche à laquelle appartient le niveau. Chaque couche a
  ses propres espèces ; `species_flags` est leur OU sur la colonne ;
- `convective_class` (0 aucun, 1 Cu hum/med, 2 TCU, 3 Cb calvus, 4 Cb capillatus) ;
- `convective_top_m` et `convective_top_temp_k` ;
- `cloud_top_teff_k` ;
- `column_condensate` ;
- `species_flags` (bits : castellanus, lenticularis, fractus, nebulosus, spissatus) ;
- `snowfall_mm`, `snow_depth_cm`, `freezing_precip_mm`.

Estimation de taille : environ +25 % par cube, soit ≈ 390 Mo pour le domaine de référence (mesure
réelle exigée à la livraison, comme pour SP1). L'AWCI n'est **pas** modifié : les nuages ne
l'alimentent pas en `operational-v1`. Un futur `operational-v2` pourra les utiliser après validation.

## 5. API

- `GET /api/v1/awci/clouds?domain=&run=&step=&lat=&lon=` renvoie :
  - les couches du point : étage, genre probable, espèces, base et sommet en m, ft et FL
    (± demi-intervalle), octas et code FEW/SCT/BKN/OVC ;
  - le plafond OACI, la convection (classe, sommet, T sommet), T_e, le condensat, le `tcc` IFS et
    le biais ;
  - une **ligne nuageuse de type METAR** (« BKN030 OVC080 CB », préfixée « modèle ») ;
  - la provenance, les statuts et les seuils du profil.
- `GET /api/v1/awci/terrain?domain=&run=&stride=` renvoie `surface_height_m` en float32 (404 pour un
  run antérieur à SP1C, dont le relief contient la bathymétrie).
- `GET /api/v1/awci/volume?domain=&run=&step=&layer=&stride=` renvoie, pour la vue 3D (SP2B), le
  champ 3D en float32 (niveaux × lat × lon) et `gh` en float32 (mêmes dimensions), avec les en-têtes
  `X-AWCI-*`. `stride` ∈ {1, 2, 4} ; seules les couches par niveau sont autorisées.
- `/field`, `/point`, `/profile`, `/timeseries` servent les nouvelles couches sans changement de
  contrat.
- `/registry` expose les couches, unités, équations et références, statuts, seuils du profil
  nuageux, et la table des codes de genre et d'espèce.
- `/summary` (SP2) ajoute :
  - `ceiling_below_1000ft_pct` (définition OACI, en remplacement de l'indicateur LCL qui était
    moins exact) ;
  - `cb_area_pct` ;
  - `cloud_cover_bias_mean`.

## 6. Tests et validation

- **Unitaires** (valeurs de référence calculées à la main ou tirées des articles) :
  - Sundqvist : bornes, monotonie, C(RHc) = 0, C(1) = 1 ;
  - recouvrement : couche unique = C ; deux couches adjacentes = max ; deux couches séparées =
    1 − (1 − a)(1 − b) ;
  - T_e : OLR 240 W m⁻² donne 255,06 K ;
  - bissection θe : θe conservé à 0,05 K près et comparaison au pseudo-adiabat de MetPy si installé
    (test sauté sinon, marqué) ;
  - octas et codes ; plafond selon la définition OACI (cas BKN au-dessus de 6000 m exclu) ;
  - règles de genre et d'espèce (un cas par ligne des tableaux, plus le cas « indéterminé ») ;
  - neige et pluie verglaçante (différences, `null` à l'échéance 0).
- **Fixture réelle** : régénération de `tests/data/awci_ops/` avec les 7 paramètres ajoutés, et
  ajout d'une **seconde fixture humide** (cellule 9×9 sur une zone précipitante du run réel) pour
  couvrir Ns, Cb et `ptype`. Cela corrige aussi le point mineur « fixture sèche » de SP1.
- **Cohérence** : sur la fixture et sur un run réel complet, distribution de `cloud_cover_bias`
  publiée dans le guide.
- **Validation (piste V, SP3)** : genres convectifs contre les METAR CB/TCU et contre RDT et la
  foudre LI ; plafond et octas contre les groupes nuageux METAR, avec tables de contingence (POD,
  FAR, CSI, biais) par étage. Le statut ne passe de HYPOTHESIS à VALIDATED qu'avec ces scores.

## 7. Variabilité (livrée avec SP5, conçue ici)

Le diagnostic nuageux est une fonction pure des champs d'une échéance : il s'applique **tel quel à
chacun des 50 membres ENS**. SP5 fournira :
- P(couverture d'un étage ≥ BKN) ;
- P(Cb) et P(TCU) ;
- P(plafond < 1000 ft et < 500 ft) ;
- le genre majoritaire et sa fréquence ;
- la dispersion (P10, P50, P90) des bases et des sommets.

Deux variabilités sont disponibles **dès SP1C**, sans ensemble :
- **temporelle** : apparition, dissipation et persistance d'un genre sur la fenêtre, montrées dans
  l'évolution temporelle ;
- **spatiale** : fraction de cellules d'un genre dans un voisinage de 5×5 cellules (≈ 125 km).

## 8. Risques

| Risque | Mitigation |
|---|---|
| Genres surinterprétés par l'utilisateur | libellé « genre probable (diagnostic modèle) », statut affiché, validation METAR |
| RHc mal calibrée hors du domaine de calibration | calibration par domaine, contrôle `tcc` à chaque échéance, statut « dégradé » |
| Couches fines manquées (niveaux standard) | limite déclarée ; incertitude de base/sommet renvoyée |
| Temps d’ingestion (+ bissection, + 7 messages) | budget : +2 min maximum sur les 8,1 min mesurées ; profilage avant optimisation |
| Cumuls (`ttr`, `sf`, `tp`) sur des échéances manquantes | `null` explicite, jamais une différence sur 6 h présentée comme 3 h |
