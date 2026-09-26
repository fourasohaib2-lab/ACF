# AWCI Web — SP2B : vue volume 3D et lecture 4D

Spec : `docs/superpowers/specs/2026-09-25-awci-web-sp2b-3d4d-design.md` (§7 : écarts). Code :
`web/awci/src/volume/` (géométrie, couches, surcouche deck.gl, contrôles).

## Utilisation

- Bouton **Vue 3D** en haut de la carte, ou `?view=3d` dans l'URL. On revient avec « Revenir en 2D ».
- **Couches volumiques**, deux au plus :

  | Couche | Ce qui est dessiné |
  |---|---|
  | Nuages par genre | fraction nuageuse ≥ seuil, 5/8 (BKN) par défaut ; stratiformes, Cu/TCU et Cb distingués ; opacité croissante avec la couverture |
  | Givrage potentiel | niveaux où il vaut 1 |
  | Turbulence en air clair | catégorie ≥ modérée |
  | AWCI | classes ≥ High |

  AWCI et turbulence ne se combinent pas.
- **Exagération verticale** : ×10 à ×100, toujours énoncée (« Relief et altitudes exagérés ×40 »).
- **Échelle verticale** dans la scène : 850, 700, 500, 300, 200 et 100 hPa, avec le FL et la hauteur en km.
- **Caméra** :
  - préréglages : vue de dessus, oblique sud, oblique ouest ;
  - souris : clic droit ou Ctrl + glisser ;
  - clavier (carte active) : Maj + flèches.
- **4D** : les touches ←/→ et la lecture de la barre de temps passent d'une échéance à l'autre.
  - Les deux volumes suivants sont préchargés.
  - Aucune interpolation temporelle.
  - `prefers-reduced-motion` supprime les animations de caméra.
- **Clic sur un voxel** : l'inspecteur s'ouvre au point **et au niveau** du voxel. L'infobulle donne la couche,
  le niveau, le genre et la fraction en octas.
- **WebGL2 absent** : un message l'indique, le bouton est désactivé, et la carte 2D reste utilisable.

## Principes scientifiques

- **Voxels réels** : un voxel = une maille IFS 0,25° d'un niveau de pression.
  - Bornes verticales : interfaces entre hauteurs géopotentielles voisines, ramenées au-dessus de la surface
    modèle (même définition que `level_interfaces` côté Python).
  - Rien n'est interpolé, ni dans l'espace ni dans le temps.
  - Les niveaux sous la surface et les valeurs manquantes ne sont jamais dessinés.
- **Relief** : c'est la surface du modèle IFS, et non un relief plus fin. Il est cohérent avec les altitudes des
  voxels.
- **Rôle de la vue** : elle est complémentaire. Tout ce qu'elle montre existe aussi en 2D, dans l'inspecteur ou
  dans le panneau Nuages.

## Mesures

| Mesure | Résultat |
|---|---|
| Construction des voxels d'un volume complet (350 000 cellules) | 17 à 38 ms (Vitest) : pas de Web Worker |
| Module 3D, chargé à la première bascule | 203 Ko gz ; chargement initial inchangé (cœur 111 Ko gz) |
| Rendu sur le cube réel Afrique du Nord (IFS 2026-09-25 12Z, nuages et givrage) | sans erreur de console ; clic sur voxel → inspecteur au niveau du voxel (vérifié) |
| Images par seconde | non mesurable ici (SwiftShader) : recette manuelle sur le poste prévisionniste |

## Tests

- Vitest (`src/volume/*.test.ts`) :
  - interfaces verticales, voxels réels, relief, emprise par bande de latitude ;
  - lecture du binaire `/volume` ;
  - classement des couches et règle des deux couches ;
  - contrôles et état d'URL.
- Playwright (`e2e/view3d.spec.ts`) :
  - bascule 2D ↔ 3D et URL ;
  - exagération ;
  - préchargement 4D ;
  - absence de WebGL2 ;
  - accessibilité du panneau (axe).
