#!/usr/bin/env python3
import json
import subprocess
import urllib.request
from pathlib import Path

HPC = "sfoura@sms1.meteo.dz"
PROJECT = "/onm/dem/home/sfoura/ACF"
OLLAMA = "http://127.0.0.1:11434/api/chat"


def hpc(cmd):
    remote = f"source ~/miniforge3/etc/profile.d/conda.sh && conda activate acf-hpc && cd {PROJECT} && {cmd}"
    return subprocess.run(
        ["ssh", HPC, remote],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    ).stdout


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

    with urllib.request.urlopen(req, timeout=1800) as r:
        return json.loads(r.read())["message"]["content"]


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

    prompt = f"""
Projet ACF situé sur le HPC:
{PROJECT}

Branche actuelle:
acf-historical-recovery-9223251

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
