# AWCI — Plan d'audit complet script-par-script (en attente)

**Statut : NON DÉMARRÉ — sauvegardé le 2026-09-22 sur demande explicite de
l'utilisateur pour être lancé plus tard (prévu jeudi) plutôt que
maintenant, afin de préserver le quota/tokens restants.** Ce document
contient le brief complet tel que fourni par l'utilisateur, à réutiliser
tel quel comme prompt de lancement.

## Pourquoi ce n'est pas lancé immédiatement

Ce brief demande un audit exhaustif, fichier par fichier, sans exception,
de l'intégralité du projet AWCI (dashboard PySide6 ~28 fichiers, moteur de
complexité `awci.complexity.*`, `awci.hazards.*`, `awci.api.*`,
`awci.data.*`, importeurs, tests, documentation) avec pour chaque script :
lecture intégrale, compréhension du rôle/dépendances, vérification
scientifique (formules/unités/domaines de validité), correction réelle,
ajout/exécution de tests, puis une validation inter-modules globale et un
rapport final structuré (tableau des corrections, problèmes scientifiques,
architecture, dette technique restante). C'est un travail de plusieurs
sessions intensives, pas une tâche ponctuelle - donc explicitement
reporté pour ne pas épuiser le quota avant jeudi.

## Constat scientifique réel à vérifier en priorité (trouvé le 2026-09-22)

Test end-to-end 100% réel effectué (vrais METAR NOAA aviationweather.gov +
vrai CAPE/CIN GFS NOMADS 22/09/2026 12Z) sur 5 aéroports algériens,
recoupé avec un vrai BMS niveau 2 ONM actif ce jour-là (Ouargla/Touggourt/
Ghardaïa/Tamanrasset, 20-40mm). Résultat : même avec un vrai CAPE non
négligeable (507 J/kg à Ouargla, 147 J/kg à Tamanrasset, sous alerte
active), l'AWCI ne bouge que de +1.5/+0.5 point et reste "Very Low". Le
calcul lui-même est mathématiquement exact (vérifié à la main), donc ce
n'est pas un bug d'implémentation - c'est une question de **calibration
scientifique réelle** à investiguer jeudi :
- L'échelle de normalisation CAPE (0-5000 J/kg, `normalizer.py
  normalize_cape()`) est peut-être mal calibrée pour les régimes
  convectifs sahariens/pré-sahariens (déclenchement à des CAPE bien plus
  modestes que les régimes continentaux classiques).
- Le module microphysique n'a reçu aucun signal réel car le `PRATE` d'une
  analyse instantanée (f000) ne capture pas une prévision de pluie sur
  fenêtre 3h-21h - il faudrait un vrai champ de précipitation prévue, pas
  une analyse ponctuelle.
- Piste possible : un signal de convergence d'humidité/relief, plus
  pertinent que le CAPE seul pour ce régime, actuellement absent du
  module convectif.

## Décision de l'utilisateur (confirmée le 2026-09-22)

Lancement reporté à jeudi. Point de départ choisi : **PHASE 1
(cartographie) + PHASE 2 (inventaire des scripts, sans aucune
correction)** en premier, pour produire d'abord une vue d'ensemble et une
liste priorisée CRITICAL/HIGH/MEDIUM/LOW, avant de décider ensemble par
où attaquer les corrections (PHASE 3+). Ne pas commencer directement par
des corrections dispersées.

Exécuter en plusieurs sessions/chunks plutôt qu'en un seul passage
continu, avec un point d'étape et un commit après chaque module
significatif plutôt qu'à la toute fin, pour ne jamais perdre le travail
si la session s'interrompt.

---

## Brief original de l'utilisateur (verbatim)

Je veux que tu arrêtes momentanément le développement de nouvelles fonctionnalités et que tu fasses une réanalyse complète de tout le projet AWCI.
Le projet AWCI actuel contient des bugs, incohérences, erreurs potentielles et probablement des implémentations incomplètes. Je veux maintenant une phase de remise à niveau complète, script par script, avec une approche rigoureuse de type production/scientifique.

### OBJECTIF PRINCIPAL

Réexaminer TOUS les scripts du projet AWCI, sans exception, afin de :

- détecter les bugs ;
- détecter les erreurs logiques ;
- détecter les calculs scientifiques incorrects ou fragiles ;
- détecter les incohérences entre modules ;
- détecter les imports inutiles ou cassés ;
- détecter les fonctions incomplètes ;
- détecter les TODO/FIXME/pass/placeholders ;
- détecter les valeurs hardcodées ;
- détecter les données fictives/mockées utilisées comme données réelles ;
- détecter les erreurs de gestion des données manquantes ;
- détecter les problèmes de types ;
- détecter les problèmes async/sync ;
- détecter les problèmes de performance ;
- détecter les problèmes de concurrence ;
- détecter les problèmes de gestion mémoire ;
- détecter les problèmes d'I/O ;
- détecter les problèmes de configuration ;
- détecter les problèmes d'API ;
- détecter les problèmes de validation ;
- détecter les erreurs dans les formules et unités ;
- détecter les incohérences temporelles/spatiales ;
- détecter les problèmes de compatibilité entre les différents modules ;
- détecter les problèmes du dashboard ;
- détecter les problèmes d'affichage provenant du backend ;
- détecter les problèmes de sécurité ;
- détecter les erreurs silencieuses ;
- détecter les exceptions trop larges ;
- détecter les comportements qui peuvent produire des résultats scientifiquement faux sans provoquer d'erreur Python.

### RÈGLE FONDAMENTALE

Ne fais PAS un simple audit superficiel.
Je veux que tu analyses le projet script par script.
Pour chaque fichier Python, TypeScript, JavaScript, configuration, composant frontend ou autre fichier critique :

1. lire entièrement le fichier ;
2. comprendre son rôle ;
3. comprendre ses dépendances ;
4. identifier qui l'appelle ;
5. identifier ce qu'il appelle ;
6. vérifier ses entrées ;
7. vérifier ses sorties ;
8. vérifier les types ;
9. vérifier les unités ;
10. vérifier les validations ;
11. vérifier les exceptions ;
12. vérifier les cas limites ;
13. vérifier les données manquantes ;
14. vérifier les performances ;
15. vérifier les interactions avec les autres modules ;
16. vérifier la cohérence avec l'architecture globale AWCI ;
17. vérifier les tests existants ;
18. vérifier si les tests couvrent réellement le comportement ;
19. corriger les problèmes ;
20. ajouter/améliorer les tests nécessaires ;
21. exécuter les tests concernés ;
22. vérifier que la correction n'introduit pas de régression.

Ne considère jamais qu'un script est correct simplement parce qu'il existe déjà ou parce qu'un test actuel passe.

### MÉTHODE OBLIGATOIRE

Travaille dans cet ordre :

#### PHASE 1 — CARTOGRAPHIE

Commence par analyser toute l'arborescence du projet.
Identifie :

- backend ;
- frontend ;
- calcul scientifique ;
- modèles ;
- données ;
- ingestion ;
- API ;
- services ;
- configuration ;
- database ;
- cache ;
- agents ;
- moteur AWCI ;
- calcul des indices ;
- aviation ;
- visualisation ;
- dashboard ;
- tests ;
- scripts utilitaires ;
- documentation.

Construis mentalement une carte des dépendances avant de modifier le code.
Ne commence pas immédiatement à modifier des fichiers au hasard.

#### PHASE 2 — INVENTAIRE DES SCRIPTS

Établis une liste complète des fichiers importants.
Pour chaque fichier, détermine :

- rôle ;
- niveau d'importance ;
- dépendances entrantes ;
- dépendances sortantes ;
- état ;
- problèmes détectés ;
- tests associés.

Classe les problèmes :

**CRITICAL** — Peut produire : crash ; corruption de données ; résultat
scientifique faux ; mauvais calcul AWCI ; comportement dangereux ;
incohérence majeure.

**HIGH** — Problème important affectant la fiabilité ou le fonctionnement.

**MEDIUM** — Problème fonctionnel ou architectural non critique.

**LOW** — Qualité, maintenance, lisibilité ou optimisation.

#### PHASE 3 — ANALYSE SCRIPT PAR SCRIPT

Ensuite travaille réellement fichier par fichier.
Pour chaque script :

**A. Compréhension** — Comprends précisément ce que le script est censé faire.

**B. Vérification du code** — Analyse : logique ; structures ; fonctions ;
classes ; imports ; types ; conditions ; boucles ; exceptions ; async ;
I/O ; configuration.

**C. Vérification scientifique** — Pour tout calcul AWCI : vérifier la
formule ; vérifier les unités ; vérifier les conversions ; vérifier les
constantes ; vérifier les dimensions ; vérifier les domaines de validité ;
vérifier les valeurs limites ; vérifier NaN/Inf ; vérifier les données
manquantes ; vérifier les interpolations ; vérifier les agrégations ;
vérifier les pondérations.

Ne jamais modifier une formule scientifique uniquement pour faire passer
un test. Si une formule est incertaine ou insuffisamment documentée,
signale-la explicitement et recherche sa source dans le projet/
documentation avant de la modifier.

#### PHASE 4 — CORRECTION

Après analyse d'un script :

- corrige les bugs ;
- améliore la robustesse ;
- améliore la lisibilité ;
- améliore les types ;
- améliore la validation ;
- améliore les erreurs ;
- supprime les dead paths ;
- supprime les mocks qui ne doivent pas être utilisés en production ;
- remplace les placeholders lorsqu'une implémentation réelle existe dans le projet ;
- conserve les API publiques compatibles lorsque possible.

Évite les réécritures massives inutiles. Préserve les comportements
corrects existants.

#### PHASE 5 — TESTS

Pour chaque correction :

1. exécute les tests existants ;
2. ajoute des tests si nécessaire ;
3. teste les cas normaux ;
4. teste les cas limites ;
5. teste les données invalides ;
6. teste les données manquantes ;
7. teste NaN/Inf ;
8. teste les erreurs réseau/API si concerné ;
9. teste les dimensions inattendues ;
10. teste les unités incorrectes si pertinent.

Si un test échoue : ne désactive jamais le test simplement pour obtenir
une suite verte. Comprends la cause réelle et corrige le problème.

#### PHASE 6 — VALIDATION INTER-MODULES

Après avoir analysé les scripts individuellement, vérifie les
interactions entre eux. Je veux notamment vérifier :

```text
DATA INGESTION
      ↓
VALIDATION
      ↓
PREPROCESSING
      ↓
SCIENTIFIC CALCULATIONS
      ↓
AWCI ENGINE
      ↓
AGGREGATION
      ↓
API / SERVICES
      ↓
DASHBOARD
```

Vérifie que les contrats entre chaque couche sont cohérents.
Pour chaque frontière : inputs ; outputs ; types ; unités ; dimensions ;
timestamps ; erreurs ; valeurs manquantes ; conventions de nommage.

#### PHASE 7 — AWCI SCIENTIFIQUE

Porte une attention particulière au moteur de calcul AWCI.
Je veux une séparation claire entre :

```text
RAW DATA
↓
QUALITY CONTROL
↓
METEOROLOGICAL VARIABLES
↓
DERIVED VARIABLES
↓
INDIVIDUAL FACTORS
↓
NORMALIZATION
↓
WEIGHTING
↓
COMPOSITE INDEX
↓
AVIATION INTERPRETATION
↓
PRESENTATION
```

Ne mélange pas : calcul scientifique ; normalisation ; classification ;
présentation ; logique UI. Les calculs doivent rester indépendants du
dashboard.

#### PHASE 8 — DONNÉES RÉELLES

Vérifie particulièrement qu'AWCI ne présente jamais comme réel :

- une donnée mock ;
- une valeur arbitraire ;
- un score inventé ;
- une valeur par défaut présentée comme calculée ;
- une simulation présentée comme observation ;
- une donnée manquante remplacée silencieusement par une valeur plausible.

Si les données nécessaires ne sont pas disponibles : le système doit le
signaler explicitement plutôt que fabriquer une valeur.

#### PHASE 9 — DASHBOARD

Analyse également tous les composants du dashboard. Vérifie : état
loading ; état error ; état no-data ; données partielles ; unités ;
timestamps ; cohérence des valeurs ; refresh ; synchronisation
frontend/backend ; graphiques ; cartes ; légendes ; tooltips ; couleurs ;
seuils ; responsive ; performance.

Le dashboard ne doit jamais masquer une erreur scientifique ou afficher
une information comme certaine lorsqu'elle ne l'est pas.

#### PHASE 10 — QUALITÉ DU CODE

Vérifie également : Ruff ; mypy ; lint ; imports ; typing ; complexité ;
duplication ; dead code ; noms ; documentation ; logging ; exception
handling ; configuration ; secrets ; chemins absolus ; dépendances
inutilisées ; dépendances manquantes.

### RÈGLE IMPORTANTE SUR LES CHANGEMENTS

Ne fais pas : "Je vais refaire tout AWCI."
Je veux : "Je comprends d'abord le système existant, puis je corrige
méthodiquement chaque problème."
Chaque modification doit avoir une justification technique. Évite les
changements architecturaux inutiles. Ne supprime pas une fonctionnalité
simplement parce qu'elle est difficile à corriger. Ne remplace pas une
implémentation réelle par un mock. Ne simplifie pas une formule
scientifique sans justification.

### ORDRE D'EXÉCUTION

Travaille exactement comme ceci :

```text
1. Cartographier
2. Inventorier
3. Analyser
4. Identifier les problèmes
5. Corriger
6. Tester
7. Vérifier les dépendances
8. Passer au script suivant
9. Réaliser une validation globale
10. Corriger les régressions
11. Lancer la suite complète
```

Ne considère pas le projet terminé tant que les interactions entre
modules n'ont pas été vérifiées.

### RAPPORT FINAL

À la fin, génère un rapport détaillé contenant :

**1. Résumé** — nombre de fichiers analysés ; nombre de fichiers
modifiés ; nombre de bugs corrigés ; nombre de tests ajoutés ; nombre de
tests exécutés ; problèmes restant à traiter.

**2. Tableau des corrections**

```text
FILE | PROBLEM | SEVERITY | FIX | TEST
```

**3. Problèmes scientifiques** — Liste séparément : formules vérifiées ;
formules corrigées ; unités corrigées ; hypothèses ; problèmes restant
incertains.

**4. Problèmes d'architecture** — Liste : dépendances circulaires ;
responsabilités mal placées ; interfaces incohérentes ; duplication ;
couplage excessif.

**5. Tests** — Donne : tests avant ; tests après ; nouveaux tests ; tests
échouants ; raison des éventuels échecs.

**6. Dette technique restante** — Ne cache aucun problème restant.

### RÈGLE FINALE

Je préfère un système qui dit clairement :

```text
DATA_UNAVAILABLE
CALCULATION_NOT_AVAILABLE
INSUFFICIENT_DATA
INVALID_INPUT
SCIENTIFIC_VALIDATION_REQUIRED
```

plutôt qu'un système qui invente une valeur pour avoir un dashboard "propre".

Je veux maintenant que tu réanalyses le projet AWCI complet et que tu
procèdes script par script, avec des corrections réelles et des tests
réels. Ne te limite surtout pas aux fichiers récemment modifiés. Analyse
l'ensemble du projet.
