# Archive documentaire

Ce dossier reçoit les documents historiques de `docs/` qui déclaraient des
statuts ("SPRINT terminé", "CERTIFICATE v0.x", "READINESS", "COMPLETION
REPORT", roadmaps concurrentes...) issus d'une phase antérieure du projet où
l'avancement était sur-déclaré. Rien n'a été supprimé : chaque fichier est
resté sous contrôle de version (`git mv`), consultable et restaurable.

Pourquoi archiver plutôt que garder à la racine de `docs/` :

- Plusieurs documents se contredisaient (ex. plusieurs "v1.0 RELEASE
  CERTIFICATE" successifs) sans qu'aucun ne soit la vérité vérifiable.
- L'audit sweep en cours depuis début septembre 2026 (voir
  `git log --grep='^audit('`) a déjà démontré que nombre de ces documents
  contenaient des surclaims (fonctionnalités déclarées prêtes qui étaient en
  fait des stubs ou des données synthétiques non signalées comme telles).
- Un projet professionnel a besoin d'une seule source de vérité sur l'état
  d'avancement : c'est désormais `docs/STATUS.md`, qui ne déclare "fini" que
  ce qui est vérifiable (tests verts + audit réel + dépendances déclarées).

Les documents encore actifs à la racine de `docs/` sont les guides de
gouvernance, les procédures opérationnelles et les spécifications techniques
qui restent corrects indépendamment de l'avancement réel du code — pas des
déclarations de statut.

Voir `../../ARCHITECTURE.md` (table de tiers) et `../STATUS.md` (suivi réel)
pour l'état courant du projet.
