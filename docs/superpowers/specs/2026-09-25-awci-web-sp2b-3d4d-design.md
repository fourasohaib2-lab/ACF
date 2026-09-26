# AWCI Web — SP2B : vue volume 3D et lecture 4D — design

**Date :** 2026-09-25 · **Statut :** implémenté le 2026-09-26 (écarts au §7) · **Sous-projet :** 2B (après SP2, avant SP3)
**Entrées :** spec SP2 (front 2D), spec SP1C (`/volume`, nuages), maquette (bascule 2D/3D/4D,
empilement « AWCI Vertical Profile »).

## 1. La 3D est-elle utile ? Décision argumentée

Les dangers aéronautiques sont **étagés** : couches nuageuses par étage, givrage entre 0 et −20 °C,
turbulence en air clair au voisinage du jet, colonnes de Cb qui traversent tous les niveaux, relief
qui masque les basses couches. En 2D, un seul niveau est visible à la fois ; la coupe verticale (SP4)
ne montre qu'un plan. Une vue volume montre **d'un seul coup d'œil** trois choses :
- l'empilement (où les couches se chevauchent) ;
- la continuité verticale (une colonne de Cb, et non trois taches sur trois niveaux) ;
- la relation avec le relief.

Elle sert au briefing et à la compréhension de situation.

Elle a aussi des limites connues : occlusion, perspective qui fausse les distances, lecture
quantitative médiocre. D'où la décision :
- **la 3D est retenue comme vue complémentaire**, jamais comme seule source d'une information :
  tout ce qu'elle montre existe aussi en 2D, dans la coupe ou dans l'inspecteur ;
- **la 4D** est la même vue animée sur les échéances, pour suivre le déplacement et l'évolution
  verticale d'un système (montée des sommets convectifs, descente d'une couche de givrage) ;
- **aucune interpolation temporelle** entre les échéances (3 h) : elle inventerait des états
  intermédiaires. L'animation passe d'une échéance à l'autre, heure de validité affichée en
  permanence ;
- **aucune interpolation spatiale** : on affiche des voxels, c'est-à-dire les cellules de grille
  réelles, comme le rééchantillonnage « nearest » du 2D. Les isosurfaces (Lorensen & Cline 1987)
  interpolent entre les points de grille ; elles pourront être ajoutées plus tard en option, avec
  la mention de l'interpolation.

## 2. Technique

- **deck.gl 9** (MIT), superposé à MapLibre via `@deck.gl/mapbox` (`MapboxOverlay`, mode entrelacé) :
  même caméra, même fond, même état d'URL (`view=3d`, `pitch`, `bearing`, `exag`).
- **Voxels** : `ColumnLayer` avec `diskResolution: 4` et `angle: 45` (prisme carré de la taille de
  la cellule de 0,25°). Les limites verticales d'un niveau sont les **interfaces** entre
  altitudes géopotentielles réelles : milieu des `gh` voisins ; en bas, le relief ACF ; en haut
  (100 hPa), gh₁₀₀ plus la moitié de l'écart gh₁₀₀ − gh₁₅₀. Les niveaux sous le relief (SP1,
  `null`) ne sont pas dessinés.
- **Relief** : maillage construit côté client depuis `GET /api/v1/awci/terrain?domain=` (float32,
  relief ACF de SP1), rendu par `SimpleMeshLayer`. Aucune tuile externe n'est nécessaire, ce qui
  garantit le fonctionnement sur réseau interne.
- **Exagération verticale** : ×40 par défaut, réglable de ×10 à ×100, **toujours affichée**
  (« Relief et altitudes exagérés ×40 »). Une échelle verticale en FL et en km est dessinée dans la
  scène.
- **Données** : `/volume` (SP1C), float32 niveaux × lat × lon, plus `gh`. Le **seuil** est appliqué
  côté client dans un Web Worker, qui construit les attributs binaires deck.gl (pas d'objets JS par
  voxel). `stride` passe à 2 quand le zoom est large.
- **Couches volumiques proposées** :

  | Couche | Seuil par défaut | Couleur |
  |---|---|---|
  | Nuages par genre (SP1C) | `cloud_fraction` ≥ 5/8 (BKN), réglable | palette catégorielle validée (dataviz, `--categorical`, daltonisme), opacité proportionnelle à C |
  | Givrage | `icing_potential` = 1 | teinte unique |
  | Turbulence CAT | catégorie ≥ Moderate | séquentielle |
  | AWCI | classe ≥ High | palette AWCI SP2 |
  | Sommets convectifs | colonnes de la base (LCL) à `convective_top_m` | selon `convective_class` |

  Il y a au plus deux couches simultanées, pour limiter l'occlusion.
- **Sélection** : un clic sur un voxel ouvre l'inspecteur au point (lat, lon), avec le niveau
  sélectionné. Un survol affiche genre, niveau, FL et valeur.
- **Caméra** : préréglages « vue de dessus », « oblique sud », « oblique ouest » ; clavier
  (flèches + Maj : rotation et inclinaison, +/− : exagération) ; bouton « revenir en 2D ».
- **Empilement « AWCI Vertical Profile » de la maquette** : il est rendu comme une **colonne
  3D au point sélectionné** (voxels AWCI par niveau, même palette), dans un petit canevas
  deck.gl de l'inspecteur. Il reprend exactement les données des barres 2D : ce n'est pas un
  élément décoratif.

## 3. 4D

- Lecture : 1 échéance par seconde, avec pause, pas à pas, boucle sur une fenêtre choisie (par
  exemple +0 à +24 h).
- Préchargement des 2 volumes suivants.
- `prefers-reduced-motion` : pas de lecture automatique, pas à pas uniquement.
- Une échéance manquante (run partiel) est **sautée et signalée**, jamais remplacée par la voisine.

## 4. Budget de performance

- Cible : 60 i/s ; au moins 30 i/s avec 300 000 voxels sur le poste prévisionniste de référence
  (GPU dédié).
- Changement d'échéance : moins de 500 ms en p95, volume préchargé.
- Mémoire : 2 volumes de 12 × 121 × 241 × 4 octets × 2 (valeur + gh) ≈ 5,6 Mo chacun.
- Mesure : Playwright avec Chromium sans affichage (SwiftShader) pour la **non-régression**. Les
  chiffres de SwiftShader ne représentent pas un GPU réel. La mesure sur le poste cible est une
  tâche de recette manuelle, et son résultat sera consigné.
- WebGL2 absent : message explicite et retour en 2D, sans écran vide.

## 5. Tests

| Niveau | Contenu |
|---|---|
| Vitest | interfaces verticales depuis `gh` (cas plat, relief, niveau sous le sol exclu), seuil + stride, construction des attributs binaires, exagération, mapping genre→couleur, saut des échéances manquantes |
| Python | `/terrain` (dimensions, bornes, float32), `/volume` (SP1C) |
| Playwright | bascule 2D↔3D, URL aller-retour, clic voxel → inspecteur, lecture 4D et reduced-motion, captures de non-régression |

## 6. Risques

| Risque | Mitigation |
|---|---|
| Occlusion et lecture trompeuse | 2 couches au maximum, exagération affichée, préréglages de caméra, information toujours disponible en 2D |
| Bundle (+ deck.gl ≈ 300 Ko gz) | chargement différé du module 3D à la première bascule |
| GPU faibles | stride automatique, seuil relevé, avertissement de performance |
| Voxels « en escalier » jugés peu esthétiques | c'est la résolution réelle du modèle ; ce choix est assumé et expliqué dans l'aide |

## 7. Écarts de mise en œuvre (2026-09-26)

- **Superposition non entrelacée** (`MapboxOverlay({interleaved: false})`) : le mode entrelacé de deck.gl 9.4
  plante avec MapLibre GL 6 (erreur d'exécution mesurée). deck.gl dessine donc sur son propre canevas,
  synchronisé avec la caméra de la carte. Le champ 2D et les lignes de courant sont masqués en 3D ; les
  aérodromes et les SIGMET restent visibles au sol.
- **Relief** : c'est la surface du modèle IFS (`/terrain`, calculée par l'équation hypsométrique depuis SP1C),
  et non le relief SRTM. Il est dessiné en colonnes de la taille des mailles, translucides pour laisser lire
  les côtes, et non en maillage : c'est cohérent avec les voxels et plus simple.
- **Emprise d'un voxel** : c'est exactement la maille de 0,25°. La largeur en mètres varie avec cos(lat) ; elle
  est calculée par bande de latitude de 2°, soit une erreur de largeur inférieure à 3,5 % dans une bande.
- **Pas de Web Worker** : la construction des voxels d'un volume complet (12 × 121 × 241 = 350 000 cellules)
  prend 17 à 38 ms, mesurés après optimisation (la première version, qui allouait une couleur par voxel,
  prenait environ 150 ms).
- **Sommets convectifs** : la couche de colonnes « LCL → sommet » n'est pas ajoutée. Les Cb apparaissent déjà
  en colonnes dans « Nuages par genre », niveau par niveau.
- **Couleurs** : nuages stratiformes gris clair, Cu/TCU vert, Cb orange-rouge ; givrage bleu ; turbulence
  ambre et orange ; AWCI dans sa palette. AWCI et turbulence ne se combinent pas (l'AWCI contient la
  turbulence et leurs teintes sont proches).
- **URL** : `view=3d`, `vol`, `exag` et `cth` y figurent ; la caméra (pitch, bearing) n'y figure pas, les
  préréglages la restituent.
- **Clic en 3D** : seul un voxel sélectionne un point. Il donne le point et le niveau du voxel. Un clic au sol
  donnerait le point sous la perspective, pas celui qu'on voit ; les aérodromes restent cliquables.
- **Échelle verticale** : graduations 850, 700, 500, 300, 200 et 100 hPa, avec le FL du run et la hauteur
  géopotentielle moyenne en km, toujours au premier plan. Les 12 niveaux se superposaient.
- **Performance** : le rendu 60 i/s ne peut pas être mesuré ici (SwiftShader, sans GPU). C'est une recette
  manuelle sur le poste cible, comme pour le critère de 300 ms de SP2.
