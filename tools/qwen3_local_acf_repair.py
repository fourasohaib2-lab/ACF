#!/usr/bin/env python3
import json
import re
import subprocess
import sys
import urllib.error
import urllib.request
from pathlib import Path

HPC = "sfoura@sms1.meteo.dz"
PROJECT = "/onm/dem/home/sfoura/ACF"
OLLAMA = "http://127.0.0.1:11434/api/chat"


def hpc(cmd):
    remote = f"source ~/miniforge3/etc/profile.d/conda.sh && conda activate acf-hpc && cd {PROJECT} && {cmd}"
    result = subprocess.run(
        ["ssh", HPC, remote],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    if result.returncode != 0:
        # ssh (ou la commande distante) a échoué : le dire explicitement au
        # lieu de continuer avec un diagnostic tronqué/vide envoyé à qwen()
        # comme s'il était complet (silencieusement trompeur - la version
        # précédente n'inspectait jamais returncode).
        print(
            f"[ERREUR] ssh {HPC} a retourné le code {result.returncode}",
            file=sys.stderr,
        )
    return result.stdout


def qwen(prompt):
    data = json.dumps(
        {
            "model": "qwen3",
            "stream": False,
            "options": {"temperature": 0},
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "Tu es un ingénieur Python senior. "
                        "Analyse ACF et propose uniquement des corrections "
                        "minimales et sûres. Ne crée pas de doublons. "
                        "Ne supprime jamais les tests."
                    ),
                },
                {"role": "user", "content": prompt},
            ],
        }
    ).encode()

    req = urllib.request.Request(
        OLLAMA,
        data=data,
        headers={"Content-Type": "application/json"},
    )

    try:
        with urllib.request.urlopen(req, timeout=1800) as r:
            return json.loads(r.read())["message"]["content"]
    except (urllib.error.URLError, OSError) as exc:
        # Sans ce garde-fou, un Ollama local injoignable (service arrêté,
        # mauvais port, etc.) faisait planter le script avec une
        # traceback brute au lieu d'un message exploitable - repro en
        # local, aucun service Ollama n'écoutant sur 127.0.0.1:11434.
        raise SystemExit(
            f"[ERREUR] Impossible de joindre Ollama sur {OLLAMA}: {exc}\n"
            "Vérifiez qu'un serveur Ollama local sert bien le modèle "
            "'qwen3' (ex. `ollama serve` + `ollama run qwen3`)."
        ) from exc


def main():
    print("=== DIAGNOSTIC ACF HPC ===")

    diagnostic = hpc("""
echo '=== BRANCH ==='
git branch --show-current
echo '=== STATUS ==='
git status --short
echo '=== COMPILE ==='
python -m compileall -q src
echo COMPILE=$?
echo '=== RUFF ==='
ruff check src tests
echo RUFF=$?
echo '=== PYTEST ==='
pytest -q
echo PYTEST=$?
echo '=== MODULES ==='
find src/acf -type f | grep -E \
'arpege|time_axis|vertical_axis|verification_engine|netcdf_writer|files' | sort
""")

    print(diagnostic)

    # Le diagnostic ci-dessus interroge déjà `git branch --show-current` en
    # direct sur le HPC ; extraire cette valeur réelle plutôt que de coder
    # en dur un nom de branche ("acf-historical-recovery-9223251") figé au
    # moment où ce script a été écrit. Ce nom devient faux dès que le HPC
    # change de branche (ce qui a très probablement eu lieu depuis - le
    # dépôt local en est à la Phase 52) et induirait alors qwen() en erreur
    # avec une prémisse fausse sur la branche réellement diagnostiquée.
    branch_match = re.search(
        r"=== BRANCH ===\n(.*)\n=== STATUS ===", diagnostic, re.DOTALL
    )
    branch = branch_match.group(1).strip() if branch_match else "(inconnue - échec ssh ?)"

    prompt = f"""
Projet ACF situé sur le HPC:
{PROJECT}

Branche actuelle:
{branch}

Diagnostic réel exécuté sur le HPC:

{diagnostic}

Analyse les erreurs restantes.

Important:
- src/acf/models/implementations/arpege.py existe
- src/acf/model4d/time_axis.py existe
- src/acf/model4d/vertical_axis.py existe
- src/acf/verification/verification_engine.py existe
- src/acf/data/writers/netcdf_writer.py existe
- src/acf/utils/files.py existe
- certains anciens imports semblent utiliser des chemins historiques
- ne crée pas de doublons
- ne déplace pas arbitrairement les fichiers
- propose le plan de correction exact
- indique quels tests doivent être corrigés ou conservés

Réponds avec:
1. cause racine
2. fichiers concernés
3. corrections exactes
4. ordre des corrections
5. commandes de validation
"""

    print("\n=== QWEN3 LOCAL ===\n")
    answer = qwen(prompt)

    print(answer)

    report = Path.home() / "ACF" / "reports" / "qwen3_local_repair.txt"
    report.parent.mkdir(parents=True, exist_ok=True)
    report.write_text(answer)

    print("\nRapport:", report)


if __name__ == "__main__":
    main()
