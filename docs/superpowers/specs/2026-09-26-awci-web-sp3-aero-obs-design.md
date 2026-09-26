# AWCI Web — SP3 : aérodromes, METAR/TAF, SIGMET (dont cendres), validation des nuages

Statut : conception approuvée par délégation (« continue selon ton jugement »), 2026-09-26.
Prérequis : SP1 (cube IFS), SP1C (nuages), SP2 (front 2D).

## 1. Objectif

Confronter la prévision nuageuse et convective d'AWCI aux **observations aéronautiques réelles**, et
les montrer au prévisionniste là où il travaille (carte, panneaux) :

1. catalogue des aérodromes METAR du domaine ;
2. METAR (archive), TAF (dernier émis), SIGMET internationaux (archive, dont cendres volcaniques VA) ;
3. **validation** du plafond et de la convection (TCU/CB) du modèle contre les METAR, avec des scores
   de vérification standard, par échéance ;
4. front : aérodromes et SIGMET sur la carte à l'heure de validité affichée, panneau aérodrome
   (observé vs modèle), page Validation.

Hors périmètre : PIREP/AIREP, validation du TAF lui-même, VAAC (avis de cendres autres que SIGMET),
visibilité modèle (non disponible dans IFS Open Data).

## 2. Sources (vérifiées le 2026-09-26)

Aviation Weather Center (NOAA/NWS), API de données publique, **domaine public** (gouvernement US) :

| Route | Contenu | Remarque mesurée |
|---|---|---|
| `/api/data/stationinfo?bbox=` | stations (`icaoId`, `lat`, `lon`, `elev` m, `siteType`) | réponse **plafonnée à 400** : 557 stations METAR sur 15–45° N / 20° W–40° E en tuilant |
| `/api/data/metar?ids=&hours=&format=json` | METAR/SPECI : `rawOb`, `obsTime`, `clouds` (couverture, base ft) | plafond de 400 éléments ; historique ≥ 7 jours ; **ni type CB/TCU ni temps présent** dans le JSON |
| `/api/data/taf?ids=&format=json` | TAF brut + périodes décodées | |
| `/api/data/isigmet?format=json` | SIGMET internationaux : danger (TS, TURB, ICE, VA, TC, MTW), base/sommet ft, polygone, validité, texte brut | mondial ; 126 SIGMET dont 10 VA au moment de la mesure |

Conséquences :
- Le **METAR brut est décodé par ACF** (FM 15 OMM-N° 306, OACI Annexe 3) : c'est le seul moyen d'obtenir
  CB/TCU, `///`, `VV`, CAVOK, NSC, NCD et le temps présent (TS, VCTS). Le décodage des couches est
  contrôlé contre le JSON décodé par l'AWC sur un corpus réel.
- Le client **subdivise** toute requête dont la réponse atteint 400 éléments (tuiles géographiques pour
  les stations, lots d'indicatifs pour les METAR).
- Toute donnée externe est validée (types, bornes, indicatif `^[A-Z0-9]{4}$`) ; un élément invalide est
  écarté et compté, jamais propagé.
- En-tête `User-Agent` identifiant ACF ; délai 20 s ; aucune requête AWC sur le chemin d'une requête
  web (ingestion séparée, leçon SP2 C1).

## 3. Décodage METAR (`acf.awci.obs.metar`)

`parse_metar(raw) -> MetarReport` : indicatif, jour/heure, `auto`, `cavok`, `nsc`, `ncd`, `skc/clr`,
visibilité dominante (m ; `9999` = ≥ 10 km ; SM convertis, 1 SM = 1609,344 m), couches
`(couverture FEW/SCT/BKN/OVC, base ft | None, type CB|TCU|None|unknown)`, `VVhhh`, temps présent.

Grandeurs dérivées (définitions documentées dans le code) :
- **plafond observé** : base de la plus basse couche BKN ou OVC, ou VV (ft au-dessus de l'aérodrome).
  CAVOK / NSC / NCD / SKC / CLR : pas de nuage significatif sous 5000 ft (ou l'altitude minimale de
  secteur la plus élevée) → **aucun plafond sous 5000 ft**, ce qui suffit aux seuils vérifiés (§5).
  Couverture `///` : plafond **inconnu**.
- **convection observée** : `CB` ou `TCU` dans une couche, ou `TS`/`VCTS` dans le temps présent.
  **Absence connue** seulement si le METAR est manuel, ou `AUTO` avec CAVOK. Un METAR `AUTO` sans type
  (`///`) ou avec NCD laisse la convection **inconnue** (la station automatique peut ne pas détecter les
  CB) : il est exclu de ce score.
- catégorie de vol **FAA** (VFR/MVFR/IFR/LIFR, plafond et visibilité) : affichage seulement, étiquetée FAA.

## 4. Stockage (`acf.awci.obs.store`)

`data/awci/obs/{domain}/` :
- `stations.json` (rafraîchi tous les 7 jours) ;
- `metar/YYYY-MM-DD.jsonl` (UTC de l'observation), dédoublonné par (indicatif, heure, texte brut) ;
- `taf/latest.json` ;
- `sigmet/YYYY-MM-DD.jsonl` (jour de réception), SIGMET dont le polygone recoupe le domaine,
  dédoublonnés par texte brut.
Écritures atomiques ; rétention 10 jours (paramètre). Commande `acf-awci-obs --domain D [--hours H]`
(une passe ; `--hours 72` rattrape l'historique d'un run, planification par cron/systemd comme
`acf-awci-ingest`).

## 5. Validation (`acf.awci.ops.verify`)

Appariement :
- point de grille le plus proche de la station (IFS 0,25°) ;
- à chaque échéance du run, le METAR/SPECI **le plus proche** de l'heure de validité, à **± 30 min**
  au plus (un METAR horaire ou semi-horaire couvre chaque échéance tri-horaire) ; sinon pas de paire ;
- écart d'altitude station − surface modèle rapporté ; stations à |Δz| > `max_elevation_diff_m`
  (300 m, **HYPOTHESIS** : au-delà, la maille ne représente pas la hauteur au-dessus de l'aérodrome)
  exclues du score de plafond et comptées.

Événements binaires (observé / prévu) :
- `ceiling_below_{500,1000,1500}ft` : plafond < seuil (modèle : `ceiling_m` × 1/0,3048 ; NaN = pas de
  plafond). 1500 ft : plafond minimal VMC en zone de contrôle (OACI Annexe 2, 4.2), 1000 ft : IFR (FAA),
  500 ft : LIFR (FAA).
- `convective` : TCU ou CB (observé : §3 ; modèle : `convective_class` ≥ 2).

Scores (Jolliffe & Stephenson 2012, *Forecast Verification*, 2e éd., chap. 3 ; WMO/WWRP JWGFVR),
table de contingence a = succès, b = fausses alertes, c = manqués, d = rejets corrects, n = a+b+c+d :
- POD = a/(a+c) ; FAR = b/(a+b) ; CSI = a/(a+b+c) ; biais de fréquence B = (a+b)/(a+c) ;
- ETS = (a − a_r)/(a + b + c − a_r), a_r = (a+b)(a+c)/n ;
- un score au dénominateur nul vaut `null` ; n est toujours affiché ; au-dessous de 10 événements
  observés, le score est marqué « échantillon insuffisant ».

Continu (paires où les deux plafonds existent sous 5000 ft) : erreur moyenne et erreur absolue moyenne
de la base (ft, modèle − observé).

Découpage par échéance : 0–24 h, 24–48 h, 48–72 h, et total. Le rapport liste les stations utilisées,
les exclusions par motif et les paramètres.

## 6. API (`acf.web.awci_obs`, préfixe `/api/v1/awci`)

| Route | Réponse |
|---|---|
| `GET /airports?domain=&time=` | stations + METAR le plus proche de `time` (± 30 min ; défaut : maintenant) : texte brut, heure, plafond, convection, catégorie FAA, âge |
| `GET /airport?domain=&icao=&run=` | station, METAR de la fenêtre du run, TAF, série modèle au point (plafond, convection, genre bas, couvertures), Δz, paires appariées |
| `GET /sigmets?domain=&time=` | SIGMET valides à `time` recoupant le domaine (GeoJSON) : danger, qualificatif, FL base/sommet, validité, déplacement, brut |
| `GET /verification?domain=&run=` | rapport §5 (calculé à la demande, mis en cache par dates de modification du cube et de l'archive) |

Toutes portent `attribution` (« Aviation Weather Center, NOAA/NWS — domaine public ») et l'heure de la
dernière ingestion des observations.

## 7. Front

- Carte : couche **Aérodromes** (cercle coloré par catégorie FAA, anneau pour CB/TCU observé,
  indicatif aux zooms ≥ 6) à l'heure de validité affichée ; « pas d'observation à ± 30 min » sinon.
  Couche **SIGMET** (contours par danger, VA en évidence, étiquette danger + FL).
- Clic sur un aérodrome : **panneau Aérodrome** — METAR brut et décodé, TAF brut, tableau et courbe
  plafond observé / modèle par échéance, convection observée / modèle, Δz.
- Liste des SIGMET actifs (colonne droite).
- Page **Validation** : tables de contingence et scores par événement et par échéance, n, exclusions,
  mise en garde HYPOTHESIS.
- Tous les états (chargement, erreur, vide « aucune observation ingérée », hors fenêtre) ; accessibilité
  (axe) ; aucune couleur sans texte.

## 8. Tests

- Décodeur : corpus réel de 400 METAR (Afrique du Nord / Méditerranée, 2026-09-26) — couches identiques
  au JSON AWC, catégorie FAA identique à celle de l'AWC (397/397 mesurés) ; cas normatifs (CAVOK,
  NSC, NCD, `///`, VV, AUTO, TCU, CB, VCTS, SM, `M1/4SM`).
- Client : pagination par subdivision au plafond de 400, validation des entrées, erreurs amont.
- Store : dédoublonnage, jours UTC, rétention, écriture atomique.
- Vérification : scores sur tables connues (valeurs calculées à la main) ; appariement ± 30 min ;
  exclusions ; cas réel DAAG sur la fixture IFS.
- API : routes, 404/422, domaine sans observation.
- Front : Vitest (décodage d'affichage, panneaux), Playwright (couches, panneau Aérodrome, Validation,
  axe, mise en page).
- Fixtures : réponses AWC réelles enregistrées (`tests/data/awc/`, NOTICE).

## 9. Risques

- La convection est probablement surestimée (13 % de Cb diagnostiqués, SP1C) : la validation doit le
  montrer, pas le masquer.
- Représentativité : maille 25 km contre observation ponctuelle ; relief ; heure METAR ± 30 min.
- Disponibilité AWC : l'ingestion échoue proprement, le front affiche l'âge des observations.

## 10. Écarts de mise en œuvre

- SIGMET archivés par **jour UTC de début de validité** (et non de réception) : la lecture « valides à t »
  n'ouvre ainsi que deux fichiers.
- Stations : celles que `stationinfo` ne liste pas comme site METAR sont ignorées (HLMS dans le corpus),
  même si l'AWC diffuse leurs METAR.
- Exclusions : les échéances postérieures à la dernière observation archivée sont comptées à part
  (`not_yet_observed`), pour ne pas passer pour des METAR manquants.
- Carte : pas d'indicatif en étiquette (pas de glyphes locaux) ; choix de l'aérodrome par liste
  déroulante accessible au clavier, en plus du clic.
- Légende des observations sous la carte (dans la carte, elle masquait le champ sur petit écran).
- Validation calculée à la demande et mise en cache (4,3 s au premier appel sur le cube réel).
- Correctif transverse : ouverture concurrente du cube sérialisée (défaut SP1 rendu fréquent par SP3).
- Résultats réels et lecture : `docs/awci/AWCI_WEB_SP3.md`.
