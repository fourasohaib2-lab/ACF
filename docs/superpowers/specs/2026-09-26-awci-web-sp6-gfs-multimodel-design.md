# AWCI Web — SP6 : second modèle (NOAA GFS) et désaccord entre modèles

Statut : conception validée par délégation (« let's go to SP6 »), 2026-09-26.
Prérequis : SP1 (pipeline), SP1C et SP3 (profil nuageux 1.2.0), SP2 (front), SP3 (validation METAR).

## 1. Objectif

Donner au prévisionniste un **second avis indépendant**. L'ensemble ECMWF (SP5) mesure l'incertitude à
l'intérieur d'un même modèle ; un modèle différent (physique, assimilation, résolution) révèle une incertitude
que l'ensemble ne voit pas. On veut :
1. afficher toutes les couches AWCI calculées sur **GFS 0,25°** (NOAA/NCEP), au même format que l'IFS ;
2. une carte du **désaccord IFS–GFS**, à heure de validité et niveau égaux ;
3. la **validation de GFS contre les METAR**, sur les mêmes paires que l'IFS, pour savoir lequel croire.

## 2. Données (mesurées le 2026-09-26)

- **Source** : `https://noaa-gfs-bdp-pds.s3.amazonaws.com/gfs.{date}/{hh}/atmos/gfs.t{hh}z.pgrb2.0p25.f{FFF}`
  (NOAA Open Data Dissemination, domaine public, sans compte). Miroir NOMADS joignable aussi.
- **Index** : `.idx` au format inventaire wgrib2 (`n:offset:d=…:VAR:niveau:échéance:`). La longueur d'un message
  vaut l'offset du suivant moins le sien ; plages d'octets comme pour l'IFS.
- **Grille** : 0,25° régulière, longitudes 0 à 359,75, ramenées à [−180, 180) comme l'IFS. Après découpe au
  domaine, les grilles IFS et GFS doivent être **identiques**, sinon c'est une erreur, jamais un rééchantillonnage.
- **Runs** : 00, 06, 12 et 18 UTC, échéances horaires jusqu'à 120 h puis trihoraires.

## 3. Correspondance des champs (adaptateur `acf.awci.ops.source_gfs`)

Le pipeline (`compute_step`) reste **inchangé**. L'adaptateur produit un `StepFields` aux noms et unités de l'IFS.
Toute différence de définition est documentée et **jamais masquée** :

| IFS | GFS | Traitement |
|---|---|---|
| t, q, u, v, gh | TMP, SPFH, UGRD, VGRD, HGT | identiques (K, kg/kg, m/s, gpm) |
| w (Pa/s) | VVEL (Pa/s) | identique |
| r (%) | — | **recalculée** depuis q, T, p avec la saturation à phase mixte de l'IFS (voir ci-dessous) |
| d (s⁻¹) | — | **calculée** : divergence horizontale sur la sphère, différences centrées |
| 2t, 2d, 10u, 10v, sp, msl | TMP 2 m, DPT 2 m, UGRD/VGRD 10 m, PRES sol, PRMSL | identiques |
| 10fg (rafale max. depuis le post-traitement précédent) | GUST sol (instantanée) | **définition différente**, signalée |
| mucape (parcelle la plus instable, 350 hPa inférieurs) | CAPE 255–0 hPa au-dessus du sol | **profondeur différente**, signalée |
| tprate | PRATE instantané (kg m⁻² s⁻¹) | identique |
| ptype (table ECMWF) | CRAIN, CSNOW, CFRZR, CICEP (0/1) | codes ECMWF : verglaçante 3 > granules 8 > mixte 7 > neige 5 > pluie 1 ; aucune → 0 |
| tcc (0–1) | TCDC atmosphère entière (%) | ÷ 100 |
| lsm | LAND | masque terre (0/1 au lieu d'une fraction) |
| tcwv | PWAT | identique |
| tcw | PWAT + CWAT | CWAT = eau nuageuse seule : le condensat n'inclut **pas** pluie et neige (IFS : oui) |
| ttr (J m⁻², cumulé, négatif) | ULWRF sommet, moyennes par seau de 6 h | cumul reconstruit : ttr = −Σ moyenne × durée ; OLR = différence entre échéances, exacte |
| tp (m, cumulé) | APCP « 0–N h acc » (mm) | ÷ 1000 |
| sd, rsn | WEASD (mm eq. eau), SNOD (m) | sd = WEASD/1000 ; rsn = WEASD/SNOD si SNOD > 0 |
| sf (chute de neige cumulée) | absent | **pas de couche « chute de neige »** pour GFS (NaN, dit dans le manifeste) |

- **Humidité relative à la manière de l'IFS**, pour que le profil nuageux, calibré sur le `r` de l'IFS, reçoive la
  même grandeur (ECMWF, *IFS Documentation*, Part IV « Physical processes », fonction de saturation à phase mixte, formule de Tetens aux constantes de Buck 1981) :
  - e_sat = α·e_w + (1 − α)·e_i ;
  - Tetens : e = a₁·exp(a₃ (T − T₀)/(T − a₄)), a₁ = 611,21 Pa, T₀ = 273,16 K ;
  - sur l'eau : a₃ = 17,502, a₄ = 32,19 K ; sur la glace : a₃ = 22,587, a₄ = −0,7 K (Buck 1981) ;
  - α = 1 au-dessus de T₀, 0 sous T_ice = 250,16 K, ((T − T_ice)/(T₀ − T_ice))² entre les deux.
- **Divergence** : d = (1/(a cos φ)) ∂u/∂λ + (1/a) ∂v/∂φ − (v tan φ)/a, avec les pas de grille de
  `acf.awci.ops.kinematics` (mêmes différences centrées que la déformation d'Ellrod).
- **Statut** : les diagnostics nuageux GFS gardent le statut HYPOTHESIS. Leur calibration est celle de l'IFS ;
  la validation METAR dira si elle tient.

## 4. Stockage et API

- **Stockage** : cubes GFS sous `data/awci/gfs/{domaine}/{run}/`, même format et même rétention que l'IFS.
  Le manifeste porte `model: gfs` et la liste des écarts de définition.
- **API** : chaque route du cube accepte `model=ifs|gfs` (défaut `ifs`). L'ensemble et les observations restent
  indépendants du modèle.
- **Nouvelle route** `/compare/field?domain&run&step&level&product` : calculée à la lecture, pour un même run et
  une même échéance présents dans les deux modèles.
  - produits : `awci_diff` (AWCI GFS − IFS), `agree_icing`, `agree_cat` (catégorie ≥ modérée), `agree_convection`
    (classe ≥ TCU) ;
  - codes d'accord : 0 aucun, 1 IFS seul, 2 GFS seul, 3 les deux.
- **Désaccord au point** : `/compare/point` renvoie les valeurs IFS et GFS au point et au niveau, pour le panneau
  « Accord des modèles », qui existe déjà.

## 5. Écran

- **Sélecteur « Modèle »** dans la barre du haut (IFS ou GFS), partagé dans l'URL (`model=`). Il n'est proposé que
  si le run affiché existe pour ce modèle.
- **Groupe de couches « Désaccord IFS–GFS »** :
  - `awci_diff` en palette divergente centrée sur 0 ;
  - accords en 4 catégories (aucun, IFS seul, GFS seul, les deux).
- **Panneau « Accord des modèles »** : valeurs IFS et GFS au point, écarts, et le désaccord dit en clair.
- **Page Validation** : scores de GFS à côté de ceux de l'IFS, sur les mêmes paires.

## 6. Téléchargement automatique

`acf-awci-auto --gfs` suit aussi les runs GFS (mêmes heures, même règle de publication par interrogation, même
suppression après 7 jours).

## 7. Tests

- **Adaptateur** :
  - index wgrib2 réel ;
  - sélection des messages ;
  - humidité IFS contre des valeurs calculées à la main ;
  - divergence d'un champ analytique ;
  - reconstruction du cumul OLR sur les seaux de 6 h ;
  - codes ptype.
- **Fixture réelle** : GFS découpé au domaine de test, run du 25/09 00Z, passé par le pipeline inchangé.
- **API** : `model=gfs`, `/compare/*` égal aux différences des cubes, grilles différentes refusées, run absent → 404.
- **Front** : Vitest sur de vraies réponses, Playwright pour le sélecteur de modèle, la couche de désaccord et le
  panneau.

## 8. Hors périmètre

- **Ensemble GEFS** : trop volumineux pour l'usage visé.
- **ICON (DWD) et ARPEGE (Météo-France)** : même adaptateur à écrire, plus tard.
- **Moyenne multi-modèle pondérée** : elle demande d'abord une validation plus longue.
