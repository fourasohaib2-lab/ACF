# AWCI Web — SP2 (front 2D) : guide

Spec : `docs/superpowers/specs/2026-09-25-awci-web-sp2-frontend-design.md`. Plan :
`docs/superpowers/plans/2026-09-25-awci-web-sp2-frontend.md`. Code : `web/awci/` (Vite + React 19 +
TypeScript strict + MapLibre GL 6), routes serveur dans `src/acf/web/awci_router.py` et
`src/acf/web/awci_wms.py`. Le front n'affiche que des grandeurs calculées dans le cube (SP1/SP1C) ou
observées (EUMETView relayé), avec source, heure et statut scientifique.

## Lancer

```bash
cd web/awci && npm ci && npm run build     # produit web/awci/dist
acf-awci-web                               # 127.0.0.1:8091 : API + front sur la même origine
```

- `acf-awci-web` sert `web/awci/dist` sur `/` (ou `ACF_AWCI_WEB_DIST`), après les routes `/api/v1/*`.
  Il n'y a pas de CORS à configurer : le navigateur ne contacte que cette origine, polices, icônes et fond de
  carte compris.
- Développement : `npm run dev`. Vite relaie `/api` vers `127.0.0.1:8091`.
- Variables : `ACF_AWCI_DATA_DIR` (cubes), `ACF_AWCI_DOMAINS_FILE`, `ACF_AWCI_WMS_CACHE` (tuiles
  EUMETView, par défaut `<data>/.wms-cache`).

## Écran

| Zone | Contenu réel |
|---|---|
| Barre haute | domaine, run (partiel/échec signalés), validité ± pas, « Maintenant », niveau (hPa + FL), modèle, état des données (run, complétude, âge d'ingestion, run ancien > 18 h, cohérence nuageuse), thème, heure UTC |
| Navigation | couches **présentes dans le run** (AWCI, dangers, nuages, surface), lignes de courant, observations EUMETSAT, vues enregistrées |
| Indicateurs | `/summary` pondéré par l'aire des mailles : AWCI P95 (jauge + classe), turbulence, convection (+ MUCAPE max), givrage, cisaillement P95, plafond < 1000 ft (OACI), Cb ; badges icône + texte (seuils HYPOTHESIS) |
| Carte | champ en plus proche voisin, rééchantillonné ligne par ligne en Mercator (un placement linéaire en latitude décalerait le champ d'environ 1,2° au centre d'un domaine 15–45° N), hachures pour « sans donnée / sous le relief / indéterminé », lignes de courant RK2, tuiles EUMETView relayées à heure explicite, badge « Observé HH:MM UTC · il y a N min · © EUMETSAT » |
| Colonne droite | situation actuelle (classe, dangers au-dessus du seuil, altitude la plus complexe), inspecteur (AWCI, décomposition, part des poids réellement calculée, entrées manquantes, valeurs + statut, provenance), accord des modèles (« non disponible — mono-modèle »), derniers runs |
| Rangée basse | évolution temporelle (point + P95 domaine), profil vertical AWCI (« sous le relief »), profil atmosphérique (T, Td serveur, vent, fraction nuageuse), **panneau Nuages** (colonne en altitude, genres, espèces, octas, plafond, sommet convectif, T sommets OLR, ligne « MODEL … », frise des genres par étage et par échéance) |
| API et registre | toutes les couches servies : unité, équation, source, statut ; lien OpenAPI `/docs` |

Clavier : ←/→ échéance (les échéances manquantes sont sautées), ↑/↓ niveau, `L` place le focus sur la
couche active (puis ↑/↓ changent de couche), Espace lecture 1 pas/s, Échap efface le point. Ces raccourcis
cèdent la main aux contrôles de formulaire et à la carte (où les flèches déplacent la vue). L'URL
reproduit exactement la vue (partageable).

Cohérence de l'affichage :
- La carte ne dessine que le champ de la vue courante. Pendant un chargement, l'image précédente de la
  même couche reste visible, atténuée, sous « Chargement : … ». Un changement de couche ou une erreur
  efface le champ. Les lignes de courant n'utilisent que u et v du même pas et du même niveau.
- Les indicateurs de la vue précédente sont atténués pendant la mise à jour (`aria-busy`).
- Dès la première interaction, le run affiché est inscrit dans l'URL : l'ingestion d'un run plus récent
  ne change jamais l'heure de validité à l'écran ; un bandeau l'annonce et propose de l'afficher.
- Le fondu prévision ↔ observation ne s'applique qu'en mode comparaison.
- Plafond : une maille sans plafond (aucune couche BKN/OVC sous 6000 m) est transparente, légendée
  « Pas de plafond », jamais hachurée comme « sans donnée ». La rampe sature à « ≥ 10 000 ft ».

Relais EUMETView : délai amont de 5 s, au plus 4 requêtes amont simultanées (au-delà, refus immédiat), une
couche en échec est refusée 60 s sans contacter l'amont. Seules les heures annoncées par GetCapabilities et
les emprises de tuiles XYZ sont relayées. Cache disque 24 h, 5000 tuiles au plus. Côté navigateur, les
tuiles utilisent au plus 3 connexions. Un EUMETView lent ne retarde donc pas la prévision : sans ces
limites, `/field` attendait 19,5 s derrière les tuiles ; avec elles, moins de 2 s (test e2e).

## Mesures (conteneur sans GPU, Chromium + SwiftShader, cube réel `north_africa` 2026-09-25 12Z)

| Mesure | Résultat | Critère spec |
|---|---|---|
| Premier affichage (indicateurs visibles) | 0,36 s ; réseau au repos 1,3 s | < 3 s |
| Toute première requête après démarrage du serveur (ouverture du cube 361 Mo) | 8,3 s | — |
| Changement d'échéance, p95 (20 changements, 1920×1080) | 690 ms | < 300 ms : **non vérifiable ici** |
| JavaScript de l'application par changement d'échéance | ≈ 60–70 ms (profileur CPU Chrome) | — |
| Bundle | 527 Ko gz au total (cœur 100 Ko, carte 276 Ko et worker 144 Ko chargés à la demande) | < 600 Ko gz |

Le temps d'un changement d'échéance est dominé par le **rendu WebGL logiciel** du conteneur (≈ 4 s de temps
natif sur 6 changements au profileur, contre ≈ 0,4 s de JavaScript) ; il double quand la surface d'écran
quadruple. Le critère des 300 ms doit être mesuré sur le poste prévisionniste avec un GPU : c'est une
**recette manuelle** (même script, `web/awci` → mesure p95 sur 20 changements), dont le résultat sera consigné ici.

## Tests

```bash
cd web/awci
npm test                 # Vitest + Testing Library (46 tests)
npm run lint && npm run build
npm run e2e              # Playwright (15 tests) sur tools/awci/e2e_server.py
```

Le serveur d'e2e ingère les **vraies** fixtures IFS découpées (domaine `fixture` complet ; `fixture_wet`
partiel, échéance +6 h absente) et remplace EUMETView par un relais hors ligne, construit sur l'extrait réel
des capacités. La couche cendres y échoue toujours, pour tester l'état « EUMETView indisponible ». La couche
Dust RGB y attend jusqu'au délai amont, comme un EUMETView lent. Les e2e couvrent :
- les parcours échéance, niveau et couche, le clic sur un point et le rechargement de l'URL ;
- le run partiel, le clic hors domaine et le niveau sous le relief ;
- les observations (heure et attribution), le relais en échec et le relais lent (`/field` < 2 s) ;
- la liste des couches au clavier (`L`, flèches, Espace) ;
- `prefers-reduced-motion` ;
- l'accessibilité (axe : aucune violation sérieuse ou critique, thèmes sombre et clair) ;
- la mise en page à 900, 1440, 1920 et 2560 px : zones présentes, pas de défilement horizontal, captures
  de référence dans `web/awci/e2e/layout.spec.ts-snapshots/`.

## Couleurs et accessibilité

- Palette AWCI, séquentielle et catégorielle : celles du skill dataviz, validées par `validate_palette.js`.
  Sur la carte, seuls les 3 premiers créneaux catégoriels sont valides « toutes paires » : la carte des genres
  regroupe donc les 10 genres en 3 familles (stratiformes, Cu/TCU, Cb), et l'inspecteur donne le genre exact.
- **Thème clair** : la palette AWCI échoue sur fond clair (Extreme 1,42:1 < 2:1). La carte et les barres AWCI
  restent donc sur la surface sombre validée `#0b1220` dans les deux thèmes. Les graphiques des panneaux
  passent aux créneaux catégoriels clairs validés. Les textes de statut utilisent des pas plus foncés
  (≥ 6,2:1 mesuré).
- Échéance courante : blanc sur `#256abf` (5,39:1 ; le bleu d'accent `#3987e5` n'atteignait que 3,64:1).

## Limites

- Comparaison prévision / observation par **fondu** (opacité du champ au-dessus de l'IR observé), les deux
  heures et leur écart étant affichés. Le balayage (« swipe ») de la spec demanderait une seconde carte
  synchronisée.
- Relecture animée des éclairs sur 1 h (`/wms/times` la permet) non proposée en SP2.
- Libellés du registre en anglais : ce sont ceux du serveur (`/registry`).
- Le critère de 300 ms par changement d'échéance reste à mesurer sur le poste cible (voir Mesures).
- EUMETView annonce `nearestValue` : si une heure pourtant listée dans les capacités n'est pas encore
  disponible, l'amont peut renvoyer l'image la plus proche sous cette heure. L'en-tête `Warning` de l'amont
  n'est pas encore lu.
