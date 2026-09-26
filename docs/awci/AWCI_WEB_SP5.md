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

- Pas encore de validation probabiliste contre les METAR (score de Brier, diagramme de fiabilité) : prévue en
  SP5b, avec l'archive d'observations de SP3.
- Pas de cumuls neige et verglas pour l'ensemble.
- Le coût est dominé par le téléchargement : les champs globaux ne se découpent pas par plage d'octets.
