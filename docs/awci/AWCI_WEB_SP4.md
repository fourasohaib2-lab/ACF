# AWCI Web — SP4 : route, coupe verticale et météogramme de route

Spec : `docs/superpowers/specs/2026-09-26-awci-web-sp4-route-section-design.md`. Code :
- `src/acf/awci/ops/route.py` : géométrie ;
- `src/acf/web/awci_route.py` : API ;
- `web/awci/src/panels/RoutePanel.tsx`, `charts/CrossSection.tsx`, `charts/RouteMeteogram.tsx` : écran.

## Utilisation

- **Tracer une route** :
  - bouton « Route » sur la carte, puis un clic par point (2 à 20). Un clic sur un aérodrome ajoute
    l'aérodrome lui-même. Échap ou « Terminer le tracé » pour finir ;
  - ou bien saisir des codes OACI dans « Aérodromes OACI », par exemple `GMMN DAAG DTTA HECA`. Un code inconnu
    dans le domaine est signalé, jamais deviné.
- **Partage** : la route est dans l'URL (`route=lat,lon;lat,lon`).
- **Coupe verticale** : couche de la carte si elle a une dimension verticale, sinon l'AWCI (le panneau le dit).
  - abscisse : distance en km (NM au survol) ;
  - ordonnée : pression en échelle logarithmique, graduée en FL ISA et en hPa ;
  - relief du modèle IFS en aplat (pression de surface) ; hachures : pas de donnée au-dessus du relief ;
  - niveau de la carte en pointillé, points d'appui nommés ;
  - survol : distance, niveau, valeur, maille lue.
- **Météogramme de route** : AWCI maximal le long de la route pour chaque échéance et chaque niveau.
  - chaque case est un bouton : un clic affiche cette échéance et ce niveau sur la carte ;
  - son libellé donne aussi la médiane et la part de la route en classe ≥ High, en givrage, en CAT ≥ modérée et
    en nuage ≥ 5/8.

## Science

- **Géométrie** : orthodromie (grand cercle) par slerp, rayon moyen IUGG 6 371,0088 km. L'écart à l'ellipsoïde
  WGS84 est de l'ordre de 0,5 % au plus.
- **Échantillonnage** : tous les 10 km, moins de la moitié d'une maille de 0,25° : aucune maille traversée n'est
  sautée. Chaque échantillon prend la valeur de sa maille la plus proche, comme l'inspecteur : aucune interpolation.
- **Domaine** : une route qui sort du domaine est refusée, avec la distance et la position de la sortie.
- **Parts de route** : les échantillons étant équidistants, une part d'échantillons est une part de distance. Les
  niveaux sous le relief ne comptent pas. Seuils : ceux d'ACF (classe High du profil opérationnel, Ellrod TI2 ≥ 2,
  givrage potentiel, 5/8), aucun seuil nouveau.

## API

| Route | Contenu |
|---|---|
| `/route/section?domain&run&step&layer&points` | valeurs (niveau × échantillon), pression et hauteur de surface, distances, mailles, points d'appui |
| `/route/meteogram?domain&run&points` | par échéance et niveau : AWCI max et médian, parts de route (High, givrage, CAT, BKN) |

`points` : `lat,lon;lat,lon;…`, 2 à 20 points, 10 000 km au plus.

## Vérifié

- **Données réelles** : route Casablanca → Alger → Tunis → Le Caire (3 770 km, 380 échantillons, run IFS du
  25/09 12Z) sans erreur de console. La coupe montre l'Atlas et le Tell sous forme de relief du modèle.
- **Tests Python** :
  - distances connues (quart de méridien, Alger–Tunis) et contrôle par la formule haversine ;
  - antiméridien, points de la route sur le grand cercle ;
  - valeurs de la coupe égales au cube à chaque maille, `null` exactement sous le relief (21 cas sur la route du
    test) ;
  - météogramme égal aux maxima et parts calculés directement ;
  - refus des entrées invalides.
- **Tests front** :
  - Vitest sur les vraies réponses ;
  - Playwright : tracé à la souris, Échap, coupe et météogramme, un clic règle l'échéance et le niveau, route
    depuis l'URL et effacement, audit axe.
- **Contraste** : texte des cases du météogramme contrôlé en WCAG AA (blanc sur les deux classes les plus sombres,
  sombre ailleurs, 4,7:1 au minimum).
- **Défaut corrigé pendant les tests** : deux clics rapides n'ajoutaient qu'un point. L'ajout se fait maintenant
  sur l'état courant.

## Limites

- Heure de passage unique : la coupe est à l'échéance affichée pour toute la route. Pas de vitesse sol ni de
  profil de montée et de descente.
- Pas d'optimisation de route (`docs/awci/future-improvements.md` §1).
