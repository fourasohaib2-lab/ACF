# AWCI Web — SP6 : second modèle (NOAA GFS) et désaccord IFS–GFS

Spec : `docs/superpowers/specs/2026-09-26-awci-web-sp6-gfs-multimodel-design.md`. Code :
- `src/acf/awci/ops/source_gfs.py` : adaptateur GFS ;
- `src/acf/web/awci_models.py` et `src/acf/web/awci_compare.py` : API ;
- `web/awci/src/panels/ModelAgreement.tsx` : panneau du front ;
- `tools/awci/compare_models_verification.py` : scores IFS et GFS contre les METAR.

## Utilisation

```bash
acf-awci-ingest --model gfs --run latest --domain north_africa --steps 0-72/3   # cubes dans <données>/gfs/
acf-awci-web --auto --gfs                                                       # suivi automatique IFS + GFS
```

- **Sélecteur « Modèle »** (barre du haut) : IFS ou GFS. Toutes les couches, profils, coupes et validations passent
  sur le modèle choisi (`model=gfs` dans l'URL).
- **Couches « Désaccord IFS–GFS »** : elles apparaissent quand le run existe dans les deux modèles, et seulement aux
  échéances présentes dans les deux.
  - **Écart d'AWCI (GFS − IFS)** : palette divergente, bleu quand GFS est plus bas, orange quand il est plus haut,
    centre sombre quand les deux concordent.
  - **Accords** (givrage, CAT ≥ modérée, TCU/Cb) : bleu pour IFS seul, jaune pour GFS seul, rouge pour les deux.
- **Panneau « Accord des modèles »** : les valeurs IFS et GFS au point cliqué, la classe AWCI de chacun, et le
  désaccord dit en clair (« Givrage potentiel : GFS seul »).
- **Ensemble ECMWF** : l'ensemble reste celui de l'IFS. Il n'est comparé qu'à la valeur déterministe de l'IFS.

## Science : même pipeline, différences de définition déclarées

GFS passe par le pipeline **inchangé** (`compute_step`). L'adaptateur lui donne les noms et unités de l'IFS.

**Champs recalculés ou reconstruits** :
- **Humidité relative** : recalculée depuis q, T, p avec la saturation à phase mixte de l'IFS. Le profil nuageux,
  calibré sur le `r` de l'IFS, reçoit ainsi la même grandeur.
- **Divergence** : calculée sur la sphère.
- **Type de précipitation** : tiré des indicateurs catégoriels de GFS.
- **Cumul OLR** : reconstruit depuis les moyennes GFS par seaux de 6 h. L'OLR entre deux échéances est exact.

**Différences de définition**, inscrites dans chaque manifeste et montrées dans le panneau :

| Champ | Différence avec l'IFS |
|---|---|
| Rafale | instantanée (IFS : maximum depuis le post-traitement précédent) |
| MUCAPE | parcelle la plus instable des 255 hPa inférieurs (IFS : 350 hPa) |
| Condensat | eau nuageuse seule |
| Masque terre | 0/1 |
| Chute de neige | pas de couche (pas d'équivalent GFS), jamais un zéro |

**Grilles** : IFS et GFS doivent être identiques après découpe (0,25°). Sinon la comparaison est refusée,
jamais rééchantillonnée.

## Validation contre les METAR (4 runs réels, profil nuageux 1.2.0 pour les deux)

Runs du 24/09 12Z, du 25/09 00Z et 12Z et du 26/09 00Z, domaine Afrique du Nord, mêmes stations, heures de
validité et appariement METAR que SP3. Commande :
`tools/awci/compare_models_verification.py --runs 2026092412,2026092500,2026092512,2026092600`.

| Événement | Modèle | n | Obs. | POD | FAR | Biais | ETS |
|---|---|---|---|---|---|---|---|
| Plafond < 500 ft | IFS | 11 681 | 63 | 0,11 | 0,95 | 2,14 | 0,03 |
| | GFS | 11 709 | 65 | 0,03 | 0,98 | 1,52 | 0,01 |
| Plafond < 1000 ft | IFS | 11 681 | 136 | 0,14 | 0,90 | 1,44 | 0,05 |
| | GFS | 11 709 | 138 | 0,07 | 0,92 | 0,86 | 0,03 |
| Plafond < 1500 ft | IFS | 11 681 | 197 | 0,18 | 0,84 | 1,13 | 0,08 |
| | GFS | 11 709 | 199 | 0,10 | 0,88 | 0,80 | 0,05 |
| TCU/Cb | IFS | 11 901 | 247 | 0,26 | 0,76 | 1,08 | 0,13 |
| | GFS | 11 901 | 247 | 0,19 | 0,62 | 0,51 | 0,14 |

Base du plafond (modèle − observé, deux plafonds sous 5000 ft) :

| Modèle | Cas | Biais | Erreur absolue moyenne |
|---|---|---|---|
| IFS | 251 | −1305 ft | 1610 ft |
| GFS | 267 | −1069 ft | 1390 ft |

Lecture :
- **Plafonds bas** : l'IFS est meilleur (ETS 0,08 contre 0,05 à 1500 ft) et GFS les sous-prévoit. C'est cohérent avec
  des diagnostics nuageux calibrés sur l'IFS (RHc, SP1C) : ils ne sont pas transposables tels quels à un autre modèle.
- **Convection** : l'ETS est équivalent (0,14 contre 0,13). GFS la prévoit deux fois moins souvent (biais 0,51),
  avec moins de fausses alertes. Le seuil de convection réalisée (précipitation ≥ 0,1 mm/h) a été calibré sur l'IFS.
- **Base du plafond** : les deux modèles la placent trop bas ; GFS un peu moins.
- **Portée** : 4 runs d'une même semaine, cas non indépendants. C'est une indication, pas une hiérarchie des
  modèles. Une calibration propre à GFS demandera l'archive que constitue le téléchargement automatique.

## Performances mesurées (conteneur 4 cœurs, NOAA Open Data sur AWS)

| Ingestion GFS | Durée | Volume |
|---|---|---|
| +0 à +24 h / 3 h | ≈ 55 s | ≈ 72 Mo téléchargés par échéance (champs globaux) |
| +0 à +72 h / 3 h | 167 s | — |

- **Comparaison** : `/compare/field` 1,4 s et `/compare/point` 2,2 s au premier appel (ouverture des deux cubes),
  puis quelques millisecondes.

## Défauts trouvés sur données réelles et corrigés

- **Périodes en jours** : wgrib2 écrit une période en jours quand ses deux bornes sont des jours entiers
  (« 0-1 day acc fcst » à +24 h). L'échéance +24 h était perdue.
- **Téléchargement tronqué** : un corps de réponse coupé (`IncompleteRead`) n'était pas retenté et arrêtait toute
  l'ingestion. Cela concernait aussi l'IFS.

## Limites

- Diagnostics nuageux et convectifs calibrés sur l'IFS, appliqués tels quels à GFS (HYPOTHESIS).
- Pas de chute de neige GFS.
- Pas d'ensemble GFS (GEFS).
- Pas de moyenne multi-modèle : elle attend une validation plus longue.
