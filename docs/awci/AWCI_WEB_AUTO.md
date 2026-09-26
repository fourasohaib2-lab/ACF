# AWCI Web — téléchargement automatique et suppression après une semaine

Code : `src/acf/awci/ops/auto.py` (commande `acf-awci-auto`), `src/acf/web/awci_app.py` (`acf-awci-web --auto`).

## Une seule commande

```bash
acf-awci-web --auto                  # serveur sur http://127.0.0.1:8091 + téléchargement automatique
acf-awci-web --auto --ens            # idem, avec l'ensemble ECMWF (volumineux, voir plus bas)
```

- **Processus séparé** : le téléchargement tourne dans un processus enfant, sur le même dossier de données
  (`ACF_AWCI_DATA_DIR`, par défaut `<dépôt>/data/awci`). Les calculs lourds ne ralentissent donc pas l'interface.
- **Arrêt** : le téléchargement s'arrête avec le serveur (Ctrl+C ou arrêt du service).
- **Sans serveur web** : `acf-awci-auto` fait tourner le téléchargement seul, et `acf-awci-auto --once` fait un
  seul passage (pour cron).

## Ce que fait chaque passage (toutes les 15 min)

1. **Observations** : les METAR, TAF et SIGMET (AWC, domaine public) sont récupérés si la dernière ingestion date
   de plus de 30 min. L'historique récupéré couvre le temps écoulé depuis : 72 h la première fois, 168 h au plus.
2. **Prévision déterministe IFS** : le run le plus récent parmi les heures suivies (00 et 12 UTC par défaut) dont
   la dernière échéance est publiée sur data.ecmwf.int.
   - **Détection** : l'outil interroge le serveur, sans horaire de publication supposé.
   - **Déjà complet** : un run complet n'est jamais retéléchargé.
   - **Partiel ou en échec** : il est retenté au bout d'une heure.
3. **Ensemble IFS ENS** (seulement avec `--ens`) : même règle, run de 00 UTC, +0 à +24 h toutes les 6 h.
4. **Suppression** de ce qui a plus de **7 jours** :
   - runs déterministes et ensemble, selon leur heure de run ;
   - fichiers journaliers de METAR et de SIGMET ;
   - dossiers temporaires abandonnés (`<run>.tmp`, `<run>.old` inchangés depuis un jour).

**Exception à la suppression** : le run le plus récent de chaque type est toujours gardé, même au-delà de 7 jours.
Ainsi, une machine restée éteinte une semaine ne se retrouve pas avec un tableau de bord vide. Il sera remplacé au
premier run publié.

**Robustesse** :
- une source injoignable est consignée et retentée au passage suivant ; la boucle ne s'arrête jamais pour cela ;
- un verrou (`<données>/.auto/lock`) empêche deux instances sur le même dossier ;
- le dernier passage est écrit dans `<données>/.auto/status.json`.

## Options

| Option | Défaut | Rôle |
|---|---|---|
| `--run-hours` | `0,12` | runs déterministes suivis (UTC). `0,6,12,18` pour les quatre runs quotidiens |
| `--steps` | `0-72/3` | échéances du déterministe |
| `--obs-every-min` | 30 | fréquence des observations (10 à 180) |
| `--ens` | désactivé | calcule l'ensemble ECMWF |
| `--ens-run-hours`, `--ens-steps`, `--ens-members` | `0`, `0-24/6`, `1-50` | réglages de l'ensemble |
| `--max-age-days` | 7 | durée de conservation (1 à 30 jours) |
| `--check-every-min` | 15 | intervalle entre deux passages (5 à 120) |
| `--domain` | `all` | domaines de `config/awci/domains.json` |

## Volumes (mesurés sur le domaine Afrique du Nord, conteneur 4 cœurs)

| Donnée | Temps par run | Stockage |
|---|---|---|
| Déterministe, +0 à +72 h / 3 h | ≈ 10 min (577 s mesurées) | ≈ 360 Mo par run, soit ≈ 5 Go pour 7 jours à 2 runs par jour |
| Ensemble, 50 membres, +0 à +24 h / 6 h | ≈ 31 min (1852 s mesurées), ≈ 19 Go téléchargés (77 Mo par membre et par échéance, taille lue dans l'index ECMWF) | ≈ 11 Mo par run |
| Observations (≈ 560 stations) | quelques secondes | ≈ 10 Mo pour 90 h |

- **Ensemble désactivé par défaut** : c'est le téléchargement qui coûte, pas le stockage. Les champs globaux
  d'ECMWF ne se découpent pas à la source.
- **Quatre runs par jour** : avec `--run-hours 0,6,12,18`, le stockage double (≈ 10 Go pour 7 jours).

## Premier passage mesuré (dossier vide, 26/09/2026 15:20 UTC)

`acf-awci-auto --once --steps 0-6/3` a pris 4 min 54 s :
- 41 567 METAR sur 72 h ;
- run IFS du 26/09 00Z complet.

Un second passage n'a rien retéléchargé et a pris 2,3 s : un run déjà complet n'est plus réinterrogé, et un 404 (run pas encore publié) n'est plus retenté (avant correction : 35 s).

## Démarrage avec la machine (optionnel)

- **Linux** : un service systemd lance `acf-awci-web --auto`, avec `ACF_AWCI_DATA_DIR` défini.
- **WSL** : une tâche planifiée Windows lance au démarrage de session :
  `wsl -d Ubuntu -- bash -lc "cd ~/ACF && .venv/bin/acf-awci-web --auto"`.
