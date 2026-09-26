# AWCI Web — SP5 : ensemble ECMWF (probabilités et dispersion)

Statut : conception validée par délégation (« continue selon ton jugement »), 2026-09-26.
Prérequis : SP1 (pipeline), SP1C/SP3 (nuages recalibrés, profil 1.2.0), SP2/SP2B (front).

## 1. Objectif

Donner au prévisionniste la **confiance** de la prévision. AWCI est mono-modèle depuis SP1, et le panneau
« Accord des modèles » l'annonce. L'ensemble ECMWF (IFS ENS, 50 membres perturbés, 0,25°) permet de calculer,
pour chaque maille et chaque niveau, la **probabilité** des dangers et des nuages, ainsi que la dispersion de
l'AWCI. C'est la « variabilité » nuageuse demandée.

## 2. Données (mesurées le 2026-09-26)

- Source : `https://data.ecmwf.int/forecasts/{date}/{hh}z/ifs/0p25/enfo/{…}-{step}h-enfo-ef.grib2` et son
  `.index` JSON, qui contient le champ `number` du membre (1 à 50, type `pf`). Échéances toutes les 3 h jusqu'à
  144 h. Licence CC-BY-4.0.
- Ce fichier contient tous les paramètres que le pipeline déterministe utilise (niveaux 1000 à 100 hPa et
  surface). Chaque membre est donc traité par **`compute_step` inchangé**.
- Volume : 77 Mo par membre et par échéance, en champs globaux. Les plages d'octets ne permettent pas de
  découper un domaine. Soit 3,8 Go par échéance pour 50 membres.
- Débit mesuré depuis data.ecmwf.int : 0,6 Mo/s en séquentiel, 7,1 Mo/s avec 16 connexions. Le miroir AWS S3
  répond « 503 Slow Down ». Le client utilise donc ECMWF, avec un parallélisme borné et réglable.
- Calcul par membre et par échéance (domaine Afrique du Nord) : décodage et découpe 6 s, `compute_step` 1,7 s.
- Budget par défaut (échéances 0 à 48 h toutes les 6 h, 50 membres) : environ 35 Go téléchargés et une heure et
  demie, ce qui est compatible avec des runs toutes les 12 h. Les échéances et les membres sont paramétrables.
- Produits dérivés publiés (probabilités `ep`) : seulement à 240 et 360 h, donc sans intérêt pour l'aviation à
  courte échéance.

## 3. Traitement (`acf.awci.ops.ensemble`, commande `acf-awci-ens`)

Pour chaque échéance, on lit une seule fois l'index de l'échéance. Puis, pour chaque membre, en flux : on
télécharge les messages de ce membre, on les décode et on les découpe au domaine, on applique `compute_step`
avec le relief et les profils du déterministe, puis on met à jour les compteurs. Les champs du membre sont
ensuite libérés. Il n'y a pas d'accumulation inter-échéance par membre : `previous = None`, et les cumuls
neige et verglas ne sont pas produits pour l'ensemble.

Produits : seuils existants, aucun nouveau seuil.

| Produit | Événement par membre | Dimensions |
|---|---|---|
| `p_awci_high` | AWCI ≥ borne basse de la classe High du profil opérationnel | niveau |
| `p_cloud_bkn` | `cloud_fraction` ≥ 5/8 | niveau |
| `p_icing` | `icing_potential` = 1 | niveau |
| `p_cat_moderate` | `cat_category` ≥ 2 | niveau |
| `p_convection` | `convective_class` ≥ 2 (TCU/Cb réalisé, profil nuageux 1.2.0) | surface |
| `p_ceiling_1500ft` | `ceiling_m` < 457,2 m (1500 ft ; aucun plafond = non) | surface |
| `awci_mean`, `awci_std` | moyenne et écart-type de l'AWCI sur les membres valides | niveau |

- **Stockage exact** : les comptes d'occurrences sont stockés en `uint8`, avec le nombre de membres valides par
  maille et par échéance (une valeur NaN, par exemple sous le relief, n'est pas comptée). La probabilité vaut
  compte / n et n'est jamais calculée sur un effectif nul.
- **Emplacement** : `data/awci/{domaine}/ens/{run}/{cube.nc, manifest.json}`, écrit dans un répertoire
  temporaire puis renommé. Le manifeste donne les membres utilisés, les membres manquants par échéance et les
  profils avec leur version.
- Un membre en échec (téléchargement ou décodage) est **exclu et compté**, jamais remplacé.

## 4. API (`/api/v1/awci/ens/…`)

| Route | Contenu |
|---|---|
| `GET /ens/runs?domain=` | runs ENS disponibles et leurs échéances |
| `GET /ens/meta?domain=&run=` | manifeste : produits, échéances, membres |
| `GET /ens/field?domain=&run=&product=&step=[&level=]` | probabilité (0 à 1) ou moyenne/écart-type, en float32 comme `/field` |
| `GET /ens/point?domain=&run=&lat=&lon=&level=` | série par échéance de tous les produits au point et au niveau, avec n |

Attribution « © ECMWF, CC-BY-4.0 — IFS ENS ».

## 5. Front

- **Groupe de couches** « Probabilités (ensemble ECMWF) », palette séquentielle de 0 à 100 %.
  - Il n'apparaît que si le run ENS existe pour le run affiché.
  - Il n'est proposé qu'aux échéances calculées (toutes les 6 h). Sinon, un message dit pourquoi, et l'échéance
    voisine n'est jamais substituée.
- **Panneau « Accord des modèles »**, renommé « Ensemble ECMWF ». Au point et au niveau, il donne :
  - les probabilités ;
  - la moyenne ± l'écart-type de l'AWCI, et la valeur déterministe en regard ;
  - le nombre de membres.
- **Inspecteur** : il affiche P(AWCI ≥ High) à côté de l'AWCI déterministe.

## 6. Tests

- **Fixture réelle** : messages ENS découpés à 35–37° N / 2–4° E, 4 membres, échéances 0 et 6 h.
- **Tests Python** :
  - sélection des entrées par membre ;
  - comptes et effectifs, NaN exclus, membre en échec exclu ;
  - probabilités exactes sur des membres construits à la main ;
  - écriture atomique ;
  - routes, dont les 404 pour un run absent ou une échéance non calculée.
- **Tests front** : Vitest pour les panneaux et les couches ; Playwright pour la couche de probabilité,
  l'échéance non calculée et l'accessibilité.

## 7. Limites

- Pas de validation probabiliste contre les METAR (score de Brier, fiabilité) dans cette première étape : elle
  viendra en SP5b.
- Le téléchargement domine le coût ; l'exploitation doit planifier la commande après la publication de l'ENS.
- 50 membres donnent une résolution de probabilité de 2 %. Les valeurs extrêmes (0 % et 100 %) ne sont pas des
  certitudes.
