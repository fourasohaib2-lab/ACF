# AWCI Web — SP7 : validation contre les radiosondages

Statut : conception validée par délégation (choix « 2 » : validation contre les radiosondages), 2026-09-26.
Prérequis : SP1 (cubes), SP3 (archive d'observations, validation METAR), SP6 (IFS et GFS).

## 1. Objectif

Les METAR ne valident que la surface (plafond, convection). Le givrage et la turbulence en altitude n'ont
**jamais été validés**. Les radiosondages mesurent la colonne. Ils valident les champs du modèle qui alimentent
ces dangers : température, humidité, vent, cisaillement vertical. Ils fournissent aussi un givrage de
référence, obtenu en appliquant le diagnostic ACF au profil observé.

## 2. Données (mesurées le 2026-09-26)

- **Stations** : liste officielle IGRA v2 (NOAA NCEI, `igra2-station-list.txt`) : identifiant, coordonnées,
  altitude, années d'activité. 55 stations du domaine Afrique du Nord ont des sondages en 2026.
  - l'indicatif OMM est tiré de l'identifiant IGRA ;
  - aucune liste n'est codée en dur.
- **Profils** : University of Wyoming, `weather.uwyo.edu/wsgi/sounding?datetime=…&id=<OMM>&type=TEXT:CSV`.
  - contenu : pression, géopotentiel, T, Td, humidité relative sur l'eau et sur la glace, vent ;
  - les 12 niveaux AWCI (1000 à 100 hPa, 600 hPa compris) figurent exactement dans le profil : **aucune
    interpolation verticale** ;
  - un appel par station et par heure, en séquence (service académique, sans surcharge).
- **Archive** : `.obs/{domaine}/sounding/AAAA-MM-JJ.jsonl`. On garde les 12 niveaux AWCI et l'heure de lâcher
  réelle. Rétention : celle des observations.

## 3. Appariement

- **Heure** : sondage nominal de 00 ou 12 UTC contre l'échéance du run dont l'heure de validité est égale.
- **Lieu** : maille la plus proche de la station (position de lâcher). La dérive du ballon (quelques dizaines de
  km en altitude) est négligée et le document le dit.
- **Niveaux** : exclus s'ils sont sous la surface du modèle (NaN) ou manquants dans l'observation.

## 4. Scores

Par niveau (hPa) et au total, pour chaque modèle (IFS, GFS) :
- **Continus** (biais = modèle − observation, RMSE, n) :
  - T (K) ;
  - humidité relative sur l'eau (%) : modèle calculé depuis q, T, p ; observation Wyoming sur l'eau ;
  - vent : biais de vitesse, RMSE vectorielle √(Δu² + Δv²), avec u = −V sin(dd) et v = −V cos(dd) ;
  - cisaillement vertical |ΔV|/Δz entre niveaux voisins, même définition que le modèle
    (`acf.awci.ops.kinematics.layer_shear`, Δz tiré du géopotentiel observé).
- **Givrage potentiel** : tableau de contingence (POD, FAR, biais, ETS).
  - référence : `icing_potential(T_obs, HR_eau_obs)`, le même diagnostic appliqué au profil observé ;
  - c'est une validation des entrées du diagnostic, **pas** une observation de givrage (aucune n'est disponible
    en libre accès sur le domaine).
- **Turbulence CAT** : l'indice d'Ellrod exige la déformation horizontale, qu'un sondage ne mesure pas. Seul son
  terme de cisaillement vertical est validé, et le document le dit.

## 5. API et écran

- **`acf-awci-obs --soundings`** : ingestion des sondages des dernières 48 h (options `--hours`, stations actives
  de la liste IGRA). `acf-awci-auto` l'appelle après 00 et 12 UTC.
- **`/soundings/verification?domain&run&model`** : scores du run contre les sondages.
- **Page Validation, section « Radiosondages »** :
  - profils verticaux de biais et de RMSE (T, HR, vent) pour chaque modèle ;
  - tableau de contingence du givrage ;
  - nombre de sondages et de niveaux utilisés.
- **Outil de cumul** : `tools/awci/verify_soundings.py`, sur plusieurs runs et pour les deux modèles.

## 6. Tests

- **Analyse des fichiers** : liste IGRA et CSV Wyoming réels (fixtures enregistrées), refus des entrées invalides.
- **Formules** : conversion du vent, cisaillement observé égal à `layer_shear`, scores sur des cas calculés à la main.
- **Appariement** sur la fixture IFS réelle et un vrai sondage d'Alger ; API ; front sur de vraies réponses.
