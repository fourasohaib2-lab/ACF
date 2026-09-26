# AWCI Web — SP5 : ensemble ECMWF (probabilités et dispersion)

Spec : `docs/superpowers/specs/2026-09-26-awci-web-sp5-ensemble-design.md`. Code :
- `src/acf/awci/ops/ensemble.py` : événements et comptes ;
- `ens_ingest.py` : commande `acf-awci-ens` ;
- `ens_store.py` : stockage ;
- `src/acf/web/awci_ens.py` : API ;
- `web/awci/src/panels/EnsemblePanel.tsx` : panneau du front.

## Produire l'ensemble d'un run

```bash
acf-awci-ens --run latest --domain north_africa                 # 50 membres, +0 à +48 h toutes les 6 h
acf-awci-ens --run 2026092600 --domain north_africa --steps 0-24/6 --members 1-50 --connections 16
```

- **Traitement** : chaque membre perturbé de l'IFS ENS passe par **le pipeline déterministe inchangé**
  (`compute_step`, même relief, profils AWCI et nuageux). Aucune science propre à l'ensemble n'est ajoutée.
- **Flux** : pour chaque échéance, l'index est lu une fois. Chaque membre est ensuite téléchargé par plages
  d'octets (connexions parallèles bornées, membres suivants préchargés), décodé (eccodes, séquentiellement),
  calculé, compté, puis libéré. La mémoire reste bornée.
- **Membre en échec** : il est exclu et consigné dans le manifeste (`failed_members`), jamais remplacé.
- **Échéance sans membre** : elle est marquée manquante.
- **Stockage** : `data/awci/{domaine}/ens/{run}/`. Il contient les comptes exacts, le nombre de membres valides
  par maille (`uint8`), la moyenne et l'écart-type de l'AWCI. Écriture atomique, rétention de 4 runs.

## Produits

Seuils déjà définis dans ACF, aucun nouveau seuil.

| Produit | Événement par membre |
|---|---|
| P(AWCI ≥ High) | AWCI ≥ borne basse de la classe High du profil opérationnel (50) |
| P(nuage ≥ 5/8) | fraction nuageuse au niveau ≥ 5/8 (BKN, table OMM 2700) |
| P(givrage potentiel) | givrage potentiel = 1 |
| P(turbulence CAT ≥ modérée) | catégorie Ellrod TI2 ≥ 2 |
| P(TCU/Cb réalisé) | classe convective ≥ TCU, avec le profil nuageux 1.2.0 recalibré contre les METAR |
| P(plafond < 1500 ft) | plafond OACI < 457,2 m ; pas de plafond compte comme « non » |
| Dispersion de l'AWCI | écart-type des membres (échantillon, ddof = 1) |

La probabilité vaut compte / n, où n est le nombre de membres ayant une valeur finie dans la maille. Elle n'est
jamais calculée sur n = 0. Avec 50 membres, sa résolution est de 2 %.

## Écran

- **Couches de probabilité** : groupe « Probabilités (ensemble ECMWF) », de 0 à 100 %.
  - Il n'est proposé que si le run affiché a son ensemble.
  - À une échéance non calculée (l'ensemble est à 6 h), un message donne les échéances calculées, et aucune
    échéance voisine n'est substituée.
- **Panneau « Ensemble ECMWF »** : il remplace l'ancien encart mono-modèle. Au point et au niveau, il donne les
  probabilités, le nombre de membres, et la moyenne ± l'écart-type de l'AWCI à côté de la valeur déterministe.
  Si les versions du profil nuageux de l'ensemble et du déterministe diffèrent, un avertissement le signale.

## Mesures (conteneur, 4 cœurs, data.ecmwf.int)

Run réel : IFS ENS 2026-09-26 00Z, domaine `north_africa`, 50 membres, échéances +0 à +24 h toutes les 6 h,
16 connexions.

| Mesure | Valeur |
|---|---|
| Statut | `complete`, 50 membres à chacune des 5 échéances, aucun membre en échec |
| Durée totale | 1851,9 s, soit environ 6,2 min par échéance, dominée par le téléchargement (~77 Mo par membre) |
| Cube stocké | 11 Mo |
| Extrapolation +0 à +48 h / 6 h (9 échéances) | environ 56 min, à débit égal |

**Cohérence avec le déterministe du même run** (nuage ≥ 5/8) :
- à tous les niveaux, la probabilité moyenne de l'ensemble est proche de la fréquence déterministe ;
- là où le déterministe prévoit BKN, P(BKN) vaut 65 à 75 % à +0 h et 13 à 36 % à +24 h. La divergence
  croissante des membres est celle attendue.

**Convection** : le déterministe diagnostiquait TCU/Cb sur 12 à 22 % des mailles, contre 3 à 4 % pour
l'ensemble. L'écart ne vient pas de l'ensemble. Le cube déterministe avait été produit avec le profil nuageux
1.1.0, avant le recalibrage contre les METAR, et l'ensemble avec le 1.2.0. Le panneau affiche désormais un
avertissement quand les deux versions de profil diffèrent. Les nuages et la convection ne s'y comparent alors
pas directement.

## Validation probabiliste contre les METAR (SP5b)

Code :
- `src/acf/awci/ops/verify_ens.py` : scores ;
- route `/ens/verification` ;
- `tools/awci/verify_ensemble.py` : cumul sur plusieurs runs ;
- section « Ensemble ECMWF » de la page Validation.

**Paires** : celles de la validation déterministe (SP3), restreintes aux échéances de l'ensemble. Le déterministe
du même run est noté sur ces mêmes paires, comme une probabilité 0 ou 1.

**Scores** :
- score de Brier (Brier 1950) ;
- Brier « fair » (Ferro 2014), corrigé de la taille finie de l'ensemble ;
- BSS contre la fréquence observée de l'échantillon ;
- décomposition de Murphy (1973), dont le résidu de classement est affiché ;
- diagramme de fiabilité et netteté (histogramme des probabilités émises).

Aucun intervalle de confiance n'est donné : les cas ne sont indépendants ni dans l'espace ni dans le temps.

### Résultats (4 runs réels, profils nuageux identiques 1.2.0 pour l'ensemble et le déterministe)

Runs IFS ENS du 24/09 12Z, du 25/09 00Z et 12Z et du 26/09 00Z, domaine Afrique du Nord, +0 à +24 h toutes les
6 h, 50 membres. Observations : ≈ 560 aérodromes (AWC). Commande :
`tools/awci/verify_ensemble.py --runs 2026092412,2026092500,2026092512,2026092600`.

| Événement | Cas | Observés | BS ensemble | BS fair | BS déterministe | BSS / climatologie | Gain / déterministe |
|---|---|---|---|---|---|---|---|
| Plafond < 1500 ft | 6 046 | 90 (1,5 %) | 0,020 | 0,020 | 0,029 | −0,36 | +0,32 |
| TCU/Cb réalisé | 6 170 | 131 (2,1 %) | 0,021 | 0,021 | 0,033 | −0,03 | +0,35 |

Fiabilité (cumul des 4 runs) :

| P prévue | Plafond : cas / fréq. observée | Convection : cas / fréq. observée |
|---|---|---|
| 0–10 % (moyenne 0,1–0,2 %) | 5 814 / 1,1 % | 5 762 / 0,9 % |
| 10–30 % | 88 / 1,1 % | 198 / 13,1 % |
| 30–50 % | 42 / 2,4 % | 90 / 16,7 % |
| 50–70 % | 43 / 11,6 % | 71 / 22,5 % |
| 70–90 % | 36 / 25,0 % | 35 / 45,7 % |
| 90–100 % | 23 / 39,1 % | 14 / 42,9 % |

Lecture :
- **Contre le déterministe** : l'ensemble réduit l'erreur de Brier d'un tiers sur les deux événements, et ce sur
  chacun des 4 runs (+0,24 à +0,38). Sur ces cas, une probabilité vaut mieux qu'un oui/non déterministe.
- **Contre la climatologie** : la convection est au niveau de la fréquence observée (BSS −0,03), le plafond bas
  en dessous (BSS −0,36). Aucune compétence propre n'est donc démontrée à l'échelle de l'aérodrome.
- **Sur-confiance** : aux fortes probabilités, l'événement n'est observé qu'une fois sur deux à trois. Aux faibles
  probabilités (sous 10 %), il est observé 4,5 fois (convection) à 11 fois (plafond) plus souvent qu'annoncé.
- **Causes plausibles, non séparées ici** :
  - la représentativité : maille de 25 km contre une observation ponctuelle ;
  - la résolution verticale : 12 niveaux ne résolvent pas les plafonds bas (SP3) ;
  - la dispersion insuffisante de l'ensemble aux petites échelles.
- **Conséquence opérationnelle** : les probabilités d'ensemble se lisent comme un signal relatif (où et quand le
  risque augmente), pas comme une fréquence attendue. La page Validation l'écrit automatiquement lorsque le BSS
  est négatif.
- **Suite** : une calibration statistique (fiabilité) sur plusieurs semaines d'archive, que le téléchargement
  automatique constitue, avec validation hors échantillon comme pour la convection en SP3.

## Tests

- **Python** :
  - sélection des messages par membre ;
  - comptes exacts sur des membres construits à la main ;
  - vrais membres ENS de la fixture passés par le pipeline ;
  - membre en échec, échéance manquante, écriture atomique ;
  - API (probabilité = compte / n, 404 à une échéance non calculée).
- **Front** :
  - Vitest : couches disponibles, échéance non calculée, panneau sur une réponse d'API réelle ;
  - Playwright : couche de probabilité, message d'échéance, panneau, run sans ensemble.
- **Fixture** : `tests/data/awci_ens`, 4 membres réels du run du 25/09 00Z, découpés à 35–37° N / 2–4° E.

## Limites

- Probabilités non calibrées : l'ensemble est trop confiant à l'échelle de l'aérodrome (voir « Validation
  probabiliste »). À n'utiliser qu'avec le diagramme de fiabilité.
- Pas de cumuls neige et verglas pour l'ensemble.
- Le coût est dominé par le téléchargement : les champs globaux ne se découpent pas par plage d'octets.
