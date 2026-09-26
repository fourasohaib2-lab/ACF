# AWCI Web — SP4 : route, coupe verticale et météogramme de route

Statut : conception validée par délégation (« Oui » à « SP4 après la validation »), 2026-09-26.
Prérequis : SP1 (cube par run), SP2 (carte, inspecteur), SP3 (aérodromes).

## 1. Objectif

Répondre aux deux questions d'un vol :
1. **Où et à quel niveau** les dangers se trouvent-ils le long de la route, à l'heure de validité affichée ?
   C'est la coupe verticale.
2. **À quelle heure et à quel niveau** la route est-elle la moins complexe ? C'est le météogramme de route.

## 2. Géométrie (`acf.awci.ops.route`)

- **Route** : une polyligne de 2 à 20 points (clic sur la carte, ou aérodromes OACI). Chaque tronçon suit le
  **grand cercle** (orthodromie), interpolé par slerp de vecteurs unitaires. La distance vaut l'angle central
  multiplié par R = 6 371,0088 km, rayon moyen de la Terre (IUGG ; Moritz 2000, *Geodetic Reference System
  1980*).
- **Approximation sphérique** : l'écart à l'ellipsoïde WGS84 est au plus de l'ordre de 0,5 % sur la distance. C'est sans effet
  à l'échelle d'une maille de 0,25°.
- **Échantillonnage** : un point tous les 10 km, moins que la moitié d'une maille (0,25° ≈ 27,8 km en latitude).
  Aucune maille traversée n'est donc sautée.
- **Valeur d'un échantillon** : celle de la maille la plus proche, comme dans l'inspecteur. Aucune interpolation.
- **Domaine** : une route qui sort du domaine est refusée (400). Rien n'est inventé hors du cube.
- **Limites** : 20 points et 10 000 km au plus.

## 3. API

**`GET /route/section?domain&run&step&layer&points=lat,lon;lat,lon;…`** — coupe verticale à une échéance :
- distances cumulées (km), position des points d'appui ;
- latitude et longitude des échantillons, maille retenue ;
- valeurs (niveau × échantillon), `null` sous le relief ou sans donnée ;
- pression de surface du modèle (`sp_hpa`) et hauteur de surface (`surface_height_m`) par échantillon, pour
  dessiner le relief tel que le modèle le voit ;
- niveaux en hPa et FL ISA.

La couche est une couche par niveau du cube : AWCI, dangers, nuages, vent, température, humidité.

**`GET /route/meteogram?domain&run&points=…`** — pour chaque échéance et chaque niveau, le long de la route :
- AWCI maximal et médian ;
- part de la route en classe ≥ High (borne du profil opérationnel) ;
- part de la route en givrage potentiel, en turbulence CAT ≥ modérée et en nuage ≥ 5/8.

Les seuils sont ceux d'ACF, aucun n'est nouveau. Une échéance manquante reste `missing` et n'est pas interpolée.

## 4. Écran

- **Outil « Route »** :
  - clic pour ajouter un point, double-clic ou « Terminer » pour arrêter ;
  - saisie OACI « DAAG DTTA » ;
  - route tracée sur la carte et partagée dans l'URL (`route=`).
- **Coupe verticale** :
  - distance en abscisse, pression en échelle logarithmique en ordonnée, graduée en FL ;
  - palette de la couche choisie, relief du modèle en aplat ;
  - repères des points d'appui, niveau courant, curseur de survol avec valeur exacte ;
  - tableau de données accessible.
- **Météogramme de route** :
  - échéance × FL de l'AWCI maximal le long de la route ;
  - un clic règle l'échéance et le niveau ;
  - les heures les moins complexes sont lisibles d'un coup d'œil.

## 5. Tests

- **Géométrie** : distances connues (quart de méridien, Alger–Tunis), points équidistants, antiméridien.
- **API** : échantillons égaux aux mailles lues dans le cube, valeurs sous le relief à `null`, refus hors domaine
  et entrées invalides, météogramme égal aux maxima calculés directement.
- **Front** : Vitest sur de vraies réponses d'API, Playwright pour tracer une route, afficher la coupe, régler
  l'échéance par le météogramme, et audit axe.

## 6. Hors périmètre

- Profil de vol (montée et descente), vitesse sol, heure de passage variable le long de la route.
- Optimisation de route (voir `docs/awci/future-improvements.md` §1).
